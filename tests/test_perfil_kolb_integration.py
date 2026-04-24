from __future__ import annotations

import os

import pytest
from sqlalchemy import delete, select

from curriculo_matematica.dao.student_profile import StudentProfileDAO
from curriculo_matematica.db.engine import get_session_factory
from curriculo_matematica.models.student_profile import (
    AssessmentAnswer,
    ProfileScenarioCompleted,
    StudentProfile,
)
from curriculo_matematica.tools import perfil_kolb


pytestmark = pytest.mark.integration


def _build_mcp_tools(fake_mcp):
    perfil_kolb._dao.cache_clear()
    perfil_kolb.register(fake_mcp)
    return fake_mcp.tools


def _snapshot_current_profile(student_id: int) -> dict | None:
    return StudentProfileDAO().get_by_student_id(student_id)


def _restore_profile(student_id: int, snapshot: dict | None) -> None:
    dao = StudentProfileDAO()
    if snapshot is None:
        Session = get_session_factory()
        with Session() as session:
            profile_ids = list(
                session.scalars(
                    select(StudentProfile.id).where(StudentProfile.student_id == student_id)
                )
            )
            if profile_ids:
                session.execute(
                    delete(AssessmentAnswer).where(AssessmentAnswer.profile_id.in_(profile_ids))
                )
                session.execute(
                    delete(ProfileScenarioCompleted).where(
                        ProfileScenarioCompleted.profile_id.in_(profile_ids)
                    )
                )
                session.execute(delete(StudentProfile).where(StudentProfile.id.in_(profile_ids)))
            session.commit()
        return

    answers = [
        {
            "scenario_id": int(item["scenario_id"]),
            "dimension": item.get("dimension"),
            "answer_text": item.get("answer_text"),
        }
        for item in snapshot.get("assessment_answers", [])
    ]
    dao.upsert_profile(
        student_id=student_id,
        status=snapshot.get("status"),
        style=snapshot.get("style"),
        confidence=snapshot.get("confidence"),
        kolb_vector=snapshot.get("kolb_vector") or {
            "ae_score": 0.25,
            "ro_score": 0.25,
            "ac_score": 0.25,
            "ce_score": 0.25,
        },
        source=snapshot.get("source"),
        summary=snapshot.get("summary"),
        assessment_answers=answers,
        scenarios_completed=snapshot.get("scenarios_completed") or [],
        assessment_name=snapshot.get("assessment_name") or "Lovelace Everyday Life Profiling",
        model_name=snapshot.get("model_name") or "Kolb Cycle",
    )


def test_integracion_persistencia_perfil_mock_alumno_35(fake_mcp):
    if not os.getenv("NEON_DATABASE_URL"):
        pytest.skip("NEON_DATABASE_URL no configurada para prueba de integracion.")

    student_id = 35
    snapshot = _snapshot_current_profile(student_id)
    tools = _build_mcp_tools(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": student_id,
        "current_vector": {"AE": 0.42, "RO": 0.31, "AC": 0.72, "CE": 0.55},
        "style": "Converging",
        "confidence": 0.89,
        "answered_scenarios": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "answers": [
            {
                "scenario_id": 1,
                "dimension": "AC",
                "answer": "Mock answer para validacion en Neon",
            }
        ],
        "source": "integration_test_mock",
        "summary": "Perfil mock persistido para alumno 35",
    }

    try:
        guardar = tools["persistir_perfil_kolb"](payload)
        consultar = tools["obtener_perfil_kolb"](str(student_id))

        assert guardar["ok"] is True
        assert consultar["student_id"] == "35"
        assert consultar["source"] == "integration_test_mock"
        assert consultar["style"] == "Converging"
        assert consultar["scenarios_completed"] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert len(consultar["assessment_answers"]) == 1
        assert consultar["assessment_answers"][0]["scenario_id"] == 1
        assert consultar["assessment_answers"][0]["dimension"] == "AC"
    finally:
        _restore_profile(student_id, snapshot)
        perfil_kolb._dao.cache_clear()
