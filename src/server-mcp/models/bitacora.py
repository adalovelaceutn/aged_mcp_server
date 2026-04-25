"""Modelo ORM SQLAlchemy para la tabla bitacora."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from curriculo_matematica.db.engine import Base


class Bitacora(Base):
    """Representa un turno de sesion de aprendizaje registrado en la bitacora."""

    __tablename__ = "bitacora"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alumno_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    sesion_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    actor: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    target_concept: Mapped[str | None] = mapped_column(Text, nullable=True)
    kolb_strategy: Mapped[str | None] = mapped_column(Text, nullable=True)
    scaffolding_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detected_frustration: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    active_misconception: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Serializa la fila a la estructura de respuesta estandar de la API."""
        ts = self.timestamp
        if hasattr(ts, "isoformat"):
            ts_str = ts.isoformat().replace("+00:00", "Z")
        else:
            ts_str = str(ts)

        return {
            "alumno_id": str(self.alumno_id),
            "sesion_id": self.sesion_id,
            "data": {
                "turn_index": self.turn_index,
                "timestamp": ts_str,
                "actor": self.actor,
                "payload": self.payload or {},
                "pedagogical_context": {
                    "target_concept": self.target_concept or "",
                    "kolb_strategy": self.kolb_strategy or "",
                    "scaffolding_level": self.scaffolding_level,
                    "detected_frustration": 0.8 if self.detected_frustration else 0.0,
                    "active_misconception": self.active_misconception or "none",
                },
            },
        }
