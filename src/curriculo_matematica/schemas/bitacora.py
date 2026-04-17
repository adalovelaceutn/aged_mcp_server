"""Esquemas de payload para registros de bitacora de sesion."""

from __future__ import annotations


def build_bitacora_record(
    alumno_id: str,
    sesion_id: str,
    turn_index: int,
    timestamp: str,
    actor: str,
    text: str,
    target_concept: str,
    kolb_strategy: str,
    scaffolding_level: int,
    detected_frustration: float,
    active_misconception: str,
    media_ref: str | None,
) -> dict:
    payload: dict[str, str] = {"text": text}
    if media_ref and media_ref.strip():
        payload["media_ref"] = media_ref.strip()

    return {
        "alumno_id": alumno_id,
        "sesion_id": sesion_id,
        "data": {
            "turn_index": turn_index,
            "timestamp": timestamp,
            "actor": actor,
            "payload": payload,
            "pedagogical_context": {
                "target_concept": target_concept,
                "kolb_strategy": kolb_strategy,
                "scaffolding_level": scaffolding_level,
                "detected_frustration": detected_frustration,
                "active_misconception": active_misconception,
            },
        },
    }