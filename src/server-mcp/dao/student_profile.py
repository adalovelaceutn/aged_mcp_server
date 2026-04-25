"""DAO (Data Access Object) para persistencia de student_profile."""

from __future__ import annotations

from contextlib import contextmanager
from decimal import Decimal
import json
import logging
from typing import Iterator

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from curriculo_matematica.db.engine import Base, get_engine, get_session_factory
from curriculo_matematica.models.student_profile import (
    AssessmentAnswer,
    ProfileScenarioCompleted,
    StudentProfile,
)


logger = logging.getLogger(__name__)


class StudentProfileDAO:
    """Acceso a datos para perfiles Kolb."""

    def __init__(self) -> None:
        self._Session = get_session_factory()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        engine = get_engine()
        Base.metadata.create_all(
            engine,
            tables=[
                StudentProfile.__table__,
                AssessmentAnswer.__table__,
                ProfileScenarioCompleted.__table__,
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

    def _parse_student_id(self, student_id: str | int) -> int:
        if isinstance(student_id, int):
            return student_id
        value = str(student_id).strip()
        if not value.isdigit():
            raise ValueError("student_id debe ser numerico para el esquema Neon actual.")
        return int(value)

    def _log_insert(self, table_name: str, data: dict) -> None:
        logger.info(
            "[perfil_persistencia] INSERT %s data=%s",
            table_name,
            json.dumps(data, ensure_ascii=True, default=str),
        )

    def _get_answers(self, session: Session, profile_id: int) -> list[dict]:
        stmt = (
            select(AssessmentAnswer)
            .where(AssessmentAnswer.profile_id == profile_id)
            .order_by(AssessmentAnswer.scenario_id, AssessmentAnswer.id)
        )
        return [row.to_dict() for row in session.scalars(stmt).all()]

    def _get_scenarios_completed(self, session: Session, profile_id: int) -> list[int]:
        stmt = (
            select(ProfileScenarioCompleted.scenario_id)
            .where(ProfileScenarioCompleted.profile_id == profile_id)
            .order_by(ProfileScenarioCompleted.scenario_id)
        )
        return [int(value) for value in session.scalars(stmt).all()]

    def get_by_student_id(self, student_id: str | int) -> dict | None:
        student_id_int = self._parse_student_id(student_id)
        stmt = (
            select(StudentProfile)
            .where(StudentProfile.student_id == student_id_int)
            .order_by(StudentProfile.id.desc())
        )
        with self._session() as session:
            row = session.scalars(stmt).first()
            if row is None:
                return None
            answers = self._get_answers(session, row.id)
            scenarios = self._get_scenarios_completed(session, row.id)
            return row.to_profile_dict(assessment_answers=answers, scenarios_completed=scenarios)

    def get_by_alumno_id(self, alumno_id: str | int) -> dict | None:
        """Alias legacy para llamadas previas basadas en 'alumno_id'."""
        return self.get_by_student_id(alumno_id)

    def upsert_profile(
        self,
        student_id: str | int,
        status: str | None,
        style: str | None,
        confidence: float | None,
        kolb_vector: dict[str, float],
        source: str | None,
        summary: str | None,
        assessment_answers: list[dict] | None,
        scenarios_completed: list[int] | None,
        assessment_name: str = "Lovelace Everyday Life Profiling",
        model_name: str = "Kolb Cycle",
    ) -> dict:
        student_id_int = self._parse_student_id(student_id)
        stmt = (
            select(StudentProfile)
            .where(StudentProfile.student_id == student_id_int)
            .order_by(StudentProfile.id.desc())
        )
        with self._session() as session:
            row = session.scalars(stmt).first()
            if row is None:
                row = StudentProfile(
                    student_id=student_id_int,
                    assessment_name=assessment_name,
                    model_name=model_name,
                    status=status,
                    style=style,
                    confidence=Decimal(str(confidence)) if confidence is not None else None,
                    ae_score=Decimal(str(kolb_vector["ae_score"])),
                    ro_score=Decimal(str(kolb_vector["ro_score"])),
                    ac_score=Decimal(str(kolb_vector["ac_score"])),
                    ce_score=Decimal(str(kolb_vector["ce_score"])),
                    source=source,
                    summary=summary,
                )
                session.add(row)
                self._log_insert(
                    "student_profile",
                    {
                        "student_id": student_id_int,
                        "assessment_name": assessment_name,
                        "model_name": model_name,
                        "status": status,
                        "style": style,
                        "confidence": confidence,
                        "ae_score": kolb_vector["ae_score"],
                        "ro_score": kolb_vector["ro_score"],
                        "ac_score": kolb_vector["ac_score"],
                        "ce_score": kolb_vector["ce_score"],
                        "source": source,
                        "summary": summary,
                    },
                )
            else:
                row.student_id = student_id_int
                row.assessment_name = assessment_name
                row.model_name = model_name
                row.status = status
                row.style = style
                row.confidence = Decimal(str(confidence)) if confidence is not None else None
                row.ae_score = Decimal(str(kolb_vector["ae_score"]))
                row.ro_score = Decimal(str(kolb_vector["ro_score"]))
                row.ac_score = Decimal(str(kolb_vector["ac_score"]))
                row.ce_score = Decimal(str(kolb_vector["ce_score"]))
                row.source = source
                row.summary = summary

            session.flush()

            session.execute(
                delete(AssessmentAnswer).where(AssessmentAnswer.profile_id == row.id)
            )
            for answer in assessment_answers or []:
                scenario_id = int(answer["scenario_id"])
                dimension = str(answer.get("dimension") or "")
                answer_text = str(answer.get("answer_text") or "")
                session.add(
                    AssessmentAnswer(
                        profile_id=row.id,
                        scenario_id=scenario_id,
                        dimension=dimension,
                        answer_text=answer_text,
                    )
                )
                self._log_insert(
                    "assessment_answers",
                    {
                        "profile_id": row.id,
                        "scenario_id": scenario_id,
                        "dimension": dimension,
                        "answer_text": answer_text,
                    },
                )

            session.execute(
                delete(ProfileScenarioCompleted).where(
                    ProfileScenarioCompleted.profile_id == row.id
                )
            )
            for scenario_id in sorted({int(value) for value in (scenarios_completed or [])}):
                session.add(
                    ProfileScenarioCompleted(profile_id=row.id, scenario_id=scenario_id)
                )
                self._log_insert(
                    "profile_scenarios_completed",
                    {
                        "profile_id": row.id,
                        "scenario_id": scenario_id,
                    },
                )

            session.flush()
            session.refresh(row)
            answers = self._get_answers(session, row.id)
            scenarios = self._get_scenarios_completed(session, row.id)
            return row.to_profile_dict(
                assessment_answers=answers,
                scenarios_completed=scenarios,
            )
