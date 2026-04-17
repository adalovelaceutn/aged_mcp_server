"""Esquemas de payload para perfil de aprendizaje Kolb."""

from __future__ import annotations

KOLB_DIMENSIONS = ("activo", "reflexivo", "teorico", "pragmatico")


def build_default_profile(alumno_id: str, updated_at: str) -> dict:
    return {
        "alumno_id": alumno_id,
        "updated_at": updated_at,
        "kolb_profile": {
            "activo": 0.25,
            "reflexivo": 0.25,
            "teorico": 0.25,
            "pragmatico": 0.25,
        },
        "preferencia_principal": "equilibrado",
        "evidencia": [],
    }


def build_evidencia(timestamp: str, origen: str, texto: str) -> dict:
    return {
        "timestamp": timestamp,
        "origen": origen,
        "texto": texto,
    }