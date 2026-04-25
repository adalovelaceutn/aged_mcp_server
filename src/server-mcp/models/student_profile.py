"""Modelo ORM SQLAlchemy para la tabla student_profile."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from curriculo_matematica.db.engine import Base


class StudentProfile(Base):
    """Perfil de aprendizaje Kolb por alumno."""

    __tablename__ = "student_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    assessment_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Lovelace Everyday Life Profiling",
    )
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Kolb Cycle")
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    style: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ae_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ro_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ac_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    ce_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
    )

    def to_profile_dict(
        self,
        assessment_answers: list[dict] | None = None,
        scenarios_completed: list[int] | None = None,
    ) -> dict:
        confidence = float(self.confidence) if self.confidence is not None else None
        ae_score = float(self.ae_score) if self.ae_score is not None else None
        ro_score = float(self.ro_score) if self.ro_score is not None else None
        ac_score = float(self.ac_score) if self.ac_score is not None else None
        ce_score = float(self.ce_score) if self.ce_score is not None else None

        return {
            "id": self.id,
            "student_id": str(self.student_id),
            "assessment_name": self.assessment_name,
            "model_name": self.model_name,
            "status": self.status,
            "style": self.style,
            "confidence": confidence,
            "kolb_vector": {
                "ae_score": ae_score,
                "ro_score": ro_score,
                "ac_score": ac_score,
                "ce_score": ce_score,
            },
            "source": self.source,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "assessment_answers": assessment_answers or [],
            "scenarios_completed": scenarios_completed or [],
        }


class AssessmentAnswer(Base):
    """Respuestas detalladas de una evaluación Kolb."""

    __tablename__ = "assessment_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("student_profile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scenario_id: Mapped[int] = mapped_column(Integer, nullable=False)
    dimension: Mapped[str | None] = mapped_column(String(10), nullable=True)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "scenario_id": self.scenario_id,
            "dimension": self.dimension,
            "answer_text": self.answer_text,
        }


class ProfileScenarioCompleted(Base):
    """Escenarios completados para analitica rapida."""

    __tablename__ = "profile_scenarios_completed"

    profile_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("student_profile.id", ondelete="CASCADE"),
        primary_key=True,
    )
    scenario_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "scenario_id": self.scenario_id,
        }
