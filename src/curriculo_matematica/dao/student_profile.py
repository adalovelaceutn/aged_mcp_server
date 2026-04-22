"""DAO (Data Access Object) para persistencia de student_profile."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from curriculo_matematica.db.engine import Base, get_engine, get_session_factory
from curriculo_matematica.models.student_profile import StudentProfile


class StudentProfileDAO:
    """Acceso a datos para perfiles Kolb."""

    def __init__(self) -> None:
        self._Session = get_session_factory()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        engine = get_engine()
        Base.metadata.create_all(engine, tables=[StudentProfile.__table__], checkfirst=True)

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

    def _parse_alumno_id(self, alumno_id: str | int) -> int:
        if isinstance(alumno_id, int):
            return alumno_id
        value = str(alumno_id).strip()
        if not value.isdigit():
            raise ValueError("alumno_id debe ser numerico para el esquema Neon actual.")
        return int(value)

    def get_by_alumno_id(self, alumno_id: str | int) -> StudentProfile | None:
        alumno_id_int = self._parse_alumno_id(alumno_id)
        stmt = select(StudentProfile).where(StudentProfile.id == alumno_id_int)
        with self._session() as session:
            row = session.scalar(stmt)
            if row is not None:
                session.expunge(row)
            return row

    def upsert_profile(
        self,
        alumno_id: str | int,
        updated_at: datetime,
        kolb_profile: dict[str, float],
        preferencia_principal: str,
        evidencia: list[dict],
    ) -> StudentProfile:
        alumno_id_int = self._parse_alumno_id(alumno_id)
        stmt = select(StudentProfile).where(StudentProfile.id == alumno_id_int)
        with self._session() as session:
            row = session.scalar(stmt)
            if row is None:
                row = StudentProfile(
                    id=alumno_id_int,
                    alumno_id=alumno_id_int,
                    updated_at=updated_at,
                    kolb_activo=Decimal(str(kolb_profile["activo"])),
                    kolb_reflexivo=Decimal(str(kolb_profile["reflexivo"])),
                    kolb_teorico=Decimal(str(kolb_profile["teorico"])),
                    kolb_pragmatico=Decimal(str(kolb_profile["pragmatico"])),
                    preferencia_principal=preferencia_principal,
                    evidencia=evidencia,
                )
                session.add(row)
            else:
                row.alumno_id = alumno_id_int
                row.updated_at = updated_at
                row.kolb_activo = Decimal(str(kolb_profile["activo"]))
                row.kolb_reflexivo = Decimal(str(kolb_profile["reflexivo"]))
                row.kolb_teorico = Decimal(str(kolb_profile["teorico"]))
                row.kolb_pragmatico = Decimal(str(kolb_profile["pragmatico"]))
                row.preferencia_principal = preferencia_principal
                row.evidencia = evidencia

            session.flush()
            session.refresh(row)
            session.expunge(row)
            return row
