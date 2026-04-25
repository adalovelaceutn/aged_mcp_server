"""DAO para persistencia normalizada del curriculo."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from curriculo_matematica.db.engine import Base, get_engine, get_session_factory
from curriculo_matematica.models.curriculo_relacional import (
    CurriculoActividad,
    CurriculoNivel,
    CurriculoNodo,
    CurriculoNodoActividad,
    CurriculoNodoAndamiaje,
    CurriculoNodoPrerequisito,
    CurriculoNodoSaber,
    CurriculoNodoVocabulario,
)


class CurriculoDAO:
    """Acceso a datos para nodos curriculares y su informacion asociada."""

    def __init__(self) -> None:
        self._Session = get_session_factory()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        engine = get_engine()
        Base.metadata.create_all(
            engine,
            tables=[
                CurriculoNivel.__table__,
                CurriculoNodo.__table__,
                CurriculoNodoSaber.__table__,
                CurriculoNodoAndamiaje.__table__,
                CurriculoNodoVocabulario.__table__,
                CurriculoActividad.__table__,
                CurriculoNodoActividad.__table__,
                CurriculoNodoPrerequisito.__table__,
            ],
            checkfirst=True,
        )

    @contextmanager
    def _session(self) -> Iterator[Session]:
        session: Session = self._Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def count_nodes(self) -> int:
        with self._session() as session:
            return len(list(session.scalars(select(CurriculoNodo.id)).all()))

    def upsert_from_dict(self, curriculo_data: dict[str, dict]) -> dict:
        """Sincroniza (upsert) el curriculo desde el diccionario fuente."""
        with self._session() as session:
            # Paso 1: niveles y nodos base.
            for nodo_id, datos in curriculo_data.items():
                nivel = self._get_or_create_nivel(session, datos["nombre_nivel"])
                nodo = session.get(CurriculoNodo, nodo_id)
                experiencia = datos["experiencia_didactica"]
                if nodo is None:
                    nodo = CurriculoNodo(
                        id=nodo_id,
                        nivel_id=nivel.id,
                        titulo=datos["titulo"],
                        capacidad=datos["capacidad"],
                        situacion_anclaje=experiencia["situacion_anclaje"],
                        pregunta_indagacion=experiencia["pregunta_indagacion"],
                    )
                    session.add(nodo)
                else:
                    nodo.nivel_id = nivel.id
                    nodo.titulo = datos["titulo"]
                    nodo.capacidad = datos["capacidad"]
                    nodo.situacion_anclaje = experiencia["situacion_anclaje"]
                    nodo.pregunta_indagacion = experiencia["pregunta_indagacion"]

            session.flush()

            # Paso 2: tablas hijas (reemplazo por nodo para mantener consistencia).
            for nodo_id, datos in curriculo_data.items():
                self._replace_children_for_node(session, nodo_id, datos)

            return {
                "ok": True,
                "nodes_synced": len(curriculo_data),
            }

    def get_node(self, nodo_id: str) -> dict | None:
        """Reconstruye un nodo en el formato del diccionario original."""
        with self._session() as session:
            nodo = session.get(CurriculoNodo, nodo_id)
            if nodo is None:
                return None

            nivel = session.get(CurriculoNivel, nodo.nivel_id)
            saberes = [
                row.texto
                for row in session.scalars(
                    select(CurriculoNodoSaber)
                    .where(CurriculoNodoSaber.nodo_id == nodo_id)
                    .order_by(CurriculoNodoSaber.orden)
                ).all()
            ]
            andamiaje = [
                row.texto
                for row in session.scalars(
                    select(CurriculoNodoAndamiaje)
                    .where(CurriculoNodoAndamiaje.nodo_id == nodo_id)
                    .order_by(CurriculoNodoAndamiaje.orden)
                ).all()
            ]
            vocabulario = [
                row.termino
                for row in session.scalars(
                    select(CurriculoNodoVocabulario)
                    .where(CurriculoNodoVocabulario.nodo_id == nodo_id)
                    .order_by(CurriculoNodoVocabulario.orden)
                ).all()
            ]
            prerequisitos = [
                row.prerequisito_nodo_id
                for row in session.scalars(
                    select(CurriculoNodoPrerequisito)
                    .where(CurriculoNodoPrerequisito.nodo_id == nodo_id)
                    .order_by(CurriculoNodoPrerequisito.prerequisito_nodo_id)
                ).all()
            ]
            actividades = [
                row.actividad_id
                for row in session.scalars(
                    select(CurriculoNodoActividad)
                    .where(CurriculoNodoActividad.nodo_id == nodo_id)
                    .order_by(CurriculoNodoActividad.orden)
                ).all()
            ]

            return {
                "nombre_nivel": nivel.nombre if nivel else "",
                "titulo": nodo.titulo,
                "capacidad": nodo.capacidad,
                "saberes": saberes,
                "prerrequisitos": prerequisitos,
                "lista_actividades": actividades,
                "experiencia_didactica": {
                    "situacion_anclaje": nodo.situacion_anclaje,
                    "pregunta_indagacion": nodo.pregunta_indagacion,
                    "andamiaje": andamiaje,
                },
                "vocabulario_clave": vocabulario,
            }

    def list_nodes_summary(self) -> dict[str, dict]:
        with self._session() as session:
            rows = session.scalars(select(CurriculoNodo).order_by(CurriculoNodo.id)).all()
            out: dict[str, dict] = {}
            for row in rows:
                nivel = session.get(CurriculoNivel, row.nivel_id)
                out[row.id] = {
                    "nombre_nivel": nivel.nombre if nivel else "",
                    "titulo": row.titulo,
                }
            return out

    def search_nodes_by_level(self, text: str) -> dict[str, dict]:
        query = (text or "").strip().lower()
        if not query:
            return {}

        with self._session() as session:
            rows = session.scalars(select(CurriculoNodo).order_by(CurriculoNodo.id)).all()
            out: dict[str, dict] = {}
            for row in rows:
                nivel = session.get(CurriculoNivel, row.nivel_id)
                nivel_nombre = nivel.nombre if nivel else ""
                if query in nivel_nombre.lower() or query in row.titulo.lower():
                    out[row.id] = {
                        "nombre_nivel": nivel_nombre,
                        "titulo": row.titulo,
                        "capacidad": row.capacidad,
                    }
            return out

    def export_as_dict(self) -> dict[str, dict]:
        """Exporta el curriculo completo en el formato compatible con upsert_from_dict."""
        summary = self.list_nodes_summary()
        out: dict[str, dict] = {}
        for nodo_id in sorted(summary.keys()):
            node = self.get_node(nodo_id)
            if node is not None:
                out[nodo_id] = node
        return out

    def _get_or_create_nivel(self, session: Session, nombre: str) -> CurriculoNivel:
        row = session.scalar(select(CurriculoNivel).where(CurriculoNivel.nombre == nombre))
        if row is None:
            row = CurriculoNivel(nombre=nombre)
            session.add(row)
            session.flush()
        return row

    def _get_or_create_actividad(self, session: Session, actividad_id: str) -> CurriculoActividad:
        row = session.get(CurriculoActividad, actividad_id)
        if row is None:
            row = CurriculoActividad(id=actividad_id)
            session.add(row)
            session.flush()
        return row

    def _replace_children_for_node(self, session: Session, nodo_id: str, datos: dict) -> None:
        session.execute(delete(CurriculoNodoSaber).where(CurriculoNodoSaber.nodo_id == nodo_id))
        session.execute(delete(CurriculoNodoAndamiaje).where(CurriculoNodoAndamiaje.nodo_id == nodo_id))
        session.execute(delete(CurriculoNodoVocabulario).where(CurriculoNodoVocabulario.nodo_id == nodo_id))
        session.execute(delete(CurriculoNodoActividad).where(CurriculoNodoActividad.nodo_id == nodo_id))
        session.execute(
            delete(CurriculoNodoPrerequisito).where(CurriculoNodoPrerequisito.nodo_id == nodo_id)
        )

        for idx, texto in enumerate(datos.get("saberes", []), start=1):
            session.add(CurriculoNodoSaber(nodo_id=nodo_id, orden=idx, texto=texto))

        andamiaje = datos.get("experiencia_didactica", {}).get("andamiaje", [])
        for idx, texto in enumerate(andamiaje, start=1):
            session.add(CurriculoNodoAndamiaje(nodo_id=nodo_id, orden=idx, texto=texto))

        for idx, termino in enumerate(datos.get("vocabulario_clave", []), start=1):
            session.add(CurriculoNodoVocabulario(nodo_id=nodo_id, orden=idx, termino=termino))

        for idx, actividad_id in enumerate(datos.get("lista_actividades", []), start=1):
            self._get_or_create_actividad(session, actividad_id)
            session.add(
                CurriculoNodoActividad(nodo_id=nodo_id, actividad_id=actividad_id, orden=idx)
            )

        prerequisitos = datos.get("nodos_requeridos", datos.get("prerrequisitos", []))
        for prereq_id in prerequisitos:
            # Si el prerequisito no existe, se ignora para evitar romper sincronizacion.
            if session.get(CurriculoNodo, prereq_id) is not None:
                session.add(
                    CurriculoNodoPrerequisito(
                        nodo_id=nodo_id,
                        prerequisito_nodo_id=prereq_id,
                    )
                )
