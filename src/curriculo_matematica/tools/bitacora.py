"""Herramientas para registrar y consultar bitacoras de sesion de aprendizaje."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from curriculo_matematica.schemas.bitacora import build_bitacora_record

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
_DEFAULT_BASE_DIR = Path(__file__).resolve().parents[3] / "session_logs"


def _validar_id(value: str, nombre_campo: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
    if not _SAFE_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"El campo '{nombre_campo}' solo admite letras, numeros, guion y guion bajo."
        )
    return value


def _validar_timestamp(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El campo 'timestamp' es obligatorio.")

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("'timestamp' debe estar en formato ISO 8601.") from error

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_record(
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
    if turn_index < 0:
        raise ValueError("'turn_index' debe ser mayor o igual a 0.")
    if scaffolding_level < 0:
        raise ValueError("'scaffolding_level' debe ser mayor o igual a 0.")
    if not 0.0 <= detected_frustration <= 1.0:
        raise ValueError("'detected_frustration' debe estar entre 0.0 y 1.0.")

    actor = actor.strip()
    text = text.strip()
    target_concept = target_concept.strip()
    kolb_strategy = kolb_strategy.strip()
    active_misconception = active_misconception.strip() or "none"

    if not actor:
        raise ValueError("El campo 'actor' es obligatorio.")
    if not text:
        raise ValueError("El campo 'text' es obligatorio.")
    if not target_concept:
        raise ValueError("El campo 'target_concept' es obligatorio.")
    if not kolb_strategy:
        raise ValueError("El campo 'kolb_strategy' es obligatorio.")

    return build_bitacora_record(
        alumno_id=alumno_id,
        sesion_id=sesion_id,
        turn_index=turn_index,
        timestamp=timestamp,
        actor=actor,
        text=text,
        target_concept=target_concept,
        kolb_strategy=kolb_strategy,
        scaffolding_level=scaffolding_level,
        detected_frustration=detected_frustration,
        active_misconception=active_misconception,
        media_ref=media_ref,
    )


def _session_file_path(alumno_id: str, sesion_id: str) -> Path:
    return _DEFAULT_BASE_DIR / alumno_id / f"{sesion_id}.jsonl"


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def registrar_bitacora_sesion(
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
        active_misconception: str = "none",
        media_ref: str | None = None,
    ) -> dict:
        """
        Registra un turno de sesion en una bitacora estructurada para seguimiento pedagogico.

        Genera una entrada con esta estructura:
        {
          "alumno_id": "...",
          "sesion_id": "...",
          "data": {
            "turn_index": 5,
            "timestamp": "2026-04-17T17:34:00Z",
            "actor": "Lovelace_Tutor",
            "payload": {"text": "...", "media_ref": "..."},
            "pedagogical_context": {...}
          }
        }
        """
        try:
            alumno_id = _validar_id(alumno_id, "alumno_id")
            sesion_id = _validar_id(sesion_id, "sesion_id")
            timestamp = _validar_timestamp(timestamp)
            record = _build_record(
                alumno_id=alumno_id,
                sesion_id=sesion_id,
                turn_index=turn_index,
                timestamp=timestamp,
                actor=actor,
                text=text,
                target_concept=target_concept,
                kolb_strategy=kolb_strategy,
                scaffolding_level=scaffolding_level,
                detected_frustration=detected_frustration,
                active_misconception=active_misconception,
                media_ref=media_ref,
            )
        except ValueError as error:
            return {"error": str(error)}

        session_file = _session_file_path(alumno_id, sesion_id)
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with session_file.open("a", encoding="utf-8") as handler:
            handler.write(json.dumps(record, ensure_ascii=False) + "\n")

        return {
            "ok": True,
            "message": "Registro de bitacora guardado.",
            "log_file": str(session_file),
            "record": record,
        }

    @mcp.tool()
    def obtener_bitacora_sesion(alumno_id: str, sesion_id: str, limit: int = 100) -> dict:
        """Devuelve los ultimos registros de una bitacora de sesion por alumno y sesion."""
        try:
            alumno_id = _validar_id(alumno_id, "alumno_id")
            sesion_id = _validar_id(sesion_id, "sesion_id")
        except ValueError as error:
            return {"error": str(error)}

        if limit <= 0:
            return {"error": "'limit' debe ser mayor a 0."}

        session_file = _session_file_path(alumno_id, sesion_id)
        if not session_file.exists():
            return {
                "alumno_id": alumno_id,
                "sesion_id": sesion_id,
                "entries": [],
                "message": "No hay registros para esta sesion.",
            }

        with session_file.open("r", encoding="utf-8") as handler:
            rows = [line.strip() for line in handler if line.strip()]

        records = [json.loads(row) for row in rows[-limit:]]
        records.sort(key=lambda item: item.get("data", {}).get("turn_index", 0))

        return {
            "alumno_id": alumno_id,
            "sesion_id": sesion_id,
            "total_entries": len(rows),
            "returned_entries": len(records),
            "entries": records,
        }

    @mcp.tool()
    def resumir_bitacora_sesion(alumno_id: str, sesion_id: str) -> dict:
        """Devuelve un resumen pedagogico de la sesion para seguimiento del aprendizaje."""
        try:
            alumno_id = _validar_id(alumno_id, "alumno_id")
            sesion_id = _validar_id(sesion_id, "sesion_id")
        except ValueError as error:
            return {"error": str(error)}

        session_file = _session_file_path(alumno_id, sesion_id)
        if not session_file.exists():
            return {
                "alumno_id": alumno_id,
                "sesion_id": sesion_id,
                "summary": {
                    "total_turns": 0,
                    "message": "No hay registros para esta sesion.",
                },
            }

        with session_file.open("r", encoding="utf-8") as handler:
            rows = [line.strip() for line in handler if line.strip()]

        records = [json.loads(row) for row in rows]
        records.sort(key=lambda item: item.get("data", {}).get("turn_index", 0))

        concept_counts: dict[str, int] = {}
        misconception_counts: dict[str, int] = {}
        frustration_values: list[float] = []
        scaffolding_values: list[int] = []
        actor_counts: dict[str, int] = {}
        timeline: list[dict[str, str | int | float]] = []

        for record in records:
            data = record.get("data", {})
            pedagogical_context = data.get("pedagogical_context", {})

            actor = str(data.get("actor", "")).strip() or "desconocido"
            target_concept = str(pedagogical_context.get("target_concept", "")).strip() or "sin_concepto"
            misconception = (
                str(pedagogical_context.get("active_misconception", "")).strip() or "none"
            )

            actor_counts[actor] = actor_counts.get(actor, 0) + 1
            concept_counts[target_concept] = concept_counts.get(target_concept, 0) + 1

            if misconception.lower() != "none":
                misconception_counts[misconception] = misconception_counts.get(misconception, 0) + 1

            frustration = pedagogical_context.get("detected_frustration")
            if isinstance(frustration, (int, float)):
                frustration_values.append(float(frustration))

            scaffolding_level = pedagogical_context.get("scaffolding_level")
            if isinstance(scaffolding_level, int):
                scaffolding_values.append(scaffolding_level)

            timeline.append(
                {
                    "turn_index": int(data.get("turn_index", 0)),
                    "timestamp": str(data.get("timestamp", "")),
                    "target_concept": target_concept,
                    "scaffolding_level": int(scaffolding_level)
                    if isinstance(scaffolding_level, int)
                    else 0,
                    "detected_frustration": float(frustration)
                    if isinstance(frustration, (int, float))
                    else 0.0,
                }
            )

        avg_frustration = (
            round(sum(frustration_values) / len(frustration_values), 4) if frustration_values else None
        )
        avg_scaffolding = (
            round(sum(scaffolding_values) / len(scaffolding_values), 4) if scaffolding_values else None
        )

        main_concept = max(concept_counts, key=concept_counts.get) if concept_counts else None

        return {
            "alumno_id": alumno_id,
            "sesion_id": sesion_id,
            "summary": {
                "total_turns": len(records),
                "actors": actor_counts,
                "concept_coverage": concept_counts,
                "main_concept": main_concept,
                "average_scaffolding_level": avg_scaffolding,
                "average_detected_frustration": avg_frustration,
                "active_misconceptions": misconception_counts,
                "timeline": timeline,
            },
        }
