"""Modelo ORM SQLAlchemy para la tabla student_profile."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from curriculo_matematica.db.engine import Base


class StudentProfile(Base):
    """Perfil de aprendizaje Kolb por alumno."""

    __tablename__ = "student_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alumno_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    kolb_activo: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    kolb_reflexivo: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    kolb_teorico: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    kolb_pragmatico: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    preferencia_principal: Mapped[str] = mapped_column(String(32), nullable=False)
    evidencia: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_profile_dict(self) -> dict:
        updated_at = self.updated_at.isoformat().replace("+00:00", "Z")
        evidencia = self.evidencia if isinstance(self.evidencia, list) else []
        return {
            "alumno_id": self.alumno_id,
            "updated_at": updated_at,
            "kolb_profile": {
                "activo": float(self.kolb_activo),
                "reflexivo": float(self.kolb_reflexivo),
                "teorico": float(self.kolb_teorico),
                "pragmatico": float(self.kolb_pragmatico),
            },
            "preferencia_principal": self.preferencia_principal,
            "evidencia": evidencia,
        }
