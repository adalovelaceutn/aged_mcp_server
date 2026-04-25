"""Esquemas de payload para perfil de aprendizaje Kolb."""

from __future__ import annotations

KOLB_DIMENSIONS = ("ae_score", "ro_score", "ac_score", "ce_score")

DEFAULT_ASSESSMENT_NAME = "Lovelace Everyday Life Profiling"
DEFAULT_MODEL_NAME = "Kolb Cycle"


def build_default_profile(student_id: str, updated_at: str) -> dict:
    return {
        "student_id": student_id,
        "assessment_name": DEFAULT_ASSESSMENT_NAME,
        "model_name": DEFAULT_MODEL_NAME,
        "status": "pending",
        "style": "Balanced",
        "confidence": 0.0,
        "updated_at": updated_at,
        "kolb_vector": {
            "ae_score": 0.25,
            "ro_score": 0.25,
            "ac_score": 0.25,
            "ce_score": 0.25,
        },
        "source": "system",
        "summary": "",
        "assessment_answers": [],
        "scenarios_completed": [],
    }


def build_assessment_answer(scenario_id: int, dimension: str, answer_text: str) -> dict:
    return {
        "scenario_id": scenario_id,
        "dimension": dimension,
        "answer_text": answer_text,
    }


def build_evidencia(timestamp: str, origen: str, texto: str) -> dict:
    """Alias legacy para mantener compatibilidad de imports antiguos."""
    return {
        "timestamp": timestamp,
        "origen": origen,
        "texto": texto,
    }