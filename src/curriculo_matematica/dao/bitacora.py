"""DAO (Data Access Object) para la tabla bitacora.

Encapsula toda la logica de persistencia: create, find_by_session, count y
ensure_schema. Las herramientas MCP solo interactuan con esta capa.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from curriculo_matematica.db.engine import Base, get_engine, get_session_factory
from curriculo_matematica.models.bitacora import Bitacora


# ---------------------------------------------------------------------------
# DTO de entrada
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BitacoraEntryDTO:
    """Datos validados de un turno de sesion listos para persistir."""

    alumno_id: int
    sesion_id: str
    turn_index: int
    timestamp: datetime
    actor: str
    payload: dict
    target_concept: str
    kolb_strategy: str
    scaffolding_level: int
    detected_frustration: bool   # True si frustration >= 0.5
    active_misconception: str


# ---------------------------------------------------------------------------
# DAO
# ---------------------------------------------------------------------------

class BitacoraDAO:
    """Acceso a datos para la tabla bitacora.

    Todas las operaciones son transaccionales. El esquema se crea de forma
    idempotente la primera vez que se instancia el DAO (lazy DDL).
    """

    def __init__(self) -> None:
        self._Session = get_session_factory()
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def _ensure_schema(self) -> None:
        """Crea las tablas e indices si no existen (CREATE … IF NOT EXISTS)."""
        engine = get_engine()
        Base.metadata.create_all(engine, tables=[Bitacora.__table__], checkfirst=True)
        with engine.connect() as conn:
            for ddl in _INDEX_DDL:
                conn.execute(text(ddl))
            conn.commit()

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    def create(self, entry: BitacoraEntryDTO) -> Bitacora:
        """Inserta un nuevo registro y devuelve la fila persistida."""
        row = Bitacora(
            alumno_id=entry.alumno_id,
            sesion_id=entry.sesion_id,
            turn_index=entry.turn_index,
            timestamp=entry.timestamp,
            actor=entry.actor,
            payload=entry.payload,
            target_concept=entry.target_concept,
            kolb_strategy=entry.kolb_strategy,
            scaffolding_level=entry.scaffolding_level,
            detected_frustration=entry.detected_frustration,
            active_misconception=entry.active_misconception,
            created_at=datetime.now(timezone.utc),
        )
        with self._session() as session:
            session.add(row)
            session.flush()
            session.refresh(row)
            session.expunge(row)
        return row

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------

    def find_by_session(
        self,
        alumno_id: int,
        sesion_id: str,
        limit: int = 100,
    ) -> list[Bitacora]:
        """Devuelve los ultimos `limit` turnos ordenados por turn_index asc."""
        stmt = (
            select(Bitacora)
            .where(
                Bitacora.alumno_id == alumno_id,
                Bitacora.sesion_id == sesion_id,
            )
            .order_by(Bitacora.turn_index.desc())
            .limit(limit)
        )
        with self._session() as session:
            rows = list(session.scalars(stmt).all())
            for row in rows:
                session.expunge(row)
        rows.sort(key=lambda r: r.turn_index)
        return rows

    def count_by_session(self, alumno_id: int, sesion_id: str) -> int:
        """Cuenta el total de turnos de la sesion."""
        stmt = select(func.count()).select_from(Bitacora).where(
            Bitacora.alumno_id == alumno_id,
            Bitacora.sesion_id == sesion_id,
        )
        with self._session() as session:
            return session.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # Context manager de sesion
    # ------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# DDL para indices (idempotente)
# ---------------------------------------------------------------------------

_INDEX_DDL = [
    "CREATE INDEX IF NOT EXISTS idx_bitacora_alumno_id ON bitacora(alumno_id)",
    "CREATE INDEX IF NOT EXISTS idx_bitacora_sesion_id ON bitacora(sesion_id)",
    "CREATE INDEX IF NOT EXISTS idx_bitacora_timestamp ON bitacora(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_bitacora_actor ON bitacora(actor)",
]
