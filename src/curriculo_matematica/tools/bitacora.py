"""Herramientas MCP para registrar y consultar bitacoras de sesion de aprendizaje.

La persistencia esta delegada completamente al BitacoraDAO. Esta capa solo
se ocupa de validar entradas, construir el DTO y formatear respuestas.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from curriculo_matematica.dao.bitacora import BitacoraDAO, BitacoraEntryDTO

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str


class RegistrarBitacoraInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    alumno_id: str = Field(min_length=1)
    sesion_id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    turn_index: int = Field(ge=0)
    timestamp: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    text: str = Field(min_length=1)
    target_concept: str = Field(min_length=1)
    kolb_strategy: str = Field(min_length=1)
    scaffolding_level: int = Field(ge=0)
    detected_frustration: float = Field(ge=0.0, le=1.0)
    active_misconception: str = "none"
    media_ref: str | None = None


class ObtenerBitacoraInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    alumno_id: str = Field(min_length=1)
    sesion_id: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")
    limit: int = Field(gt=0)


class PedagogicalContextOutput(BaseModel):
    target_concept: str
    kolb_strategy: str
    scaffolding_level: int | None = None
    detected_frustration: float
    active_misconception: str


class BitacoraDataOutput(BaseModel):
    turn_index: int
    timestamp: str
    actor: str
    payload: dict[str, Any]
    pedagogical_context: PedagogicalContextOutput


class BitacoraRecordOutput(BaseModel):
    alumno_id: str
    sesion_id: str
    data: BitacoraDataOutput


class RegistrarBitacoraOutput(BaseModel):
    ok: bool
    message: str
    id: int
    record: BitacoraRecordOutput


class ObtenerBitacoraOutput(BaseModel):
    alumno_id: str
    sesion_id: str
    total_entries: int
    returned_entries: int
    entries: list[BitacoraRecordOutput]


class ResumenBitacoraOutput(BaseModel):
    model_config = ConfigDict(extra="allow")

    alumno_id: str
    sesion_id: str
    summary: dict[str, Any]


# ---------------------------------------------------------------------------
# Singleton del DAO
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _dao() -> BitacoraDAO:
    return BitacoraDAO()


def _error_response(message: str, **kwargs: Any) -> dict:
    return ErrorResponse.model_validate({"error": message, **kwargs}).model_dump()


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

def _validar_id(value: str, nombre_campo: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"El campo '{nombre_campo}' es obligatorio.")
    if not _SAFE_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"El campo '{nombre_campo}' solo admite letras, numeros, guion y guion bajo."
        )
    return value


def _validar_alumno_id(value: str) -> int:
    value = value.strip()
    if not value:
        raise ValueError("El campo 'alumno_id' es obligatorio.")
    try:
        alumno_int = int(value)
    except ValueError:
        raise ValueError("'alumno_id' debe ser un numero entero (FK a alumnos.id).")
    if alumno_int <= 0:
        raise ValueError("'alumno_id' debe ser un entero positivo.")
    return alumno_int


def _validar_timestamp(value: str) -> datetime:
    value = value.strip()
    if not value:
        raise ValueError("El campo 'timestamp' es obligatorio.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("'timestamp' debe estar en formato ISO 8601.") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _validar_numericos(
    turn_index: int,
    scaffolding_level: int,
    detected_frustration: float,
) -> None:
    if turn_index < 0:
        raise ValueError("'turn_index' debe ser mayor o igual a 0.")
    if scaffolding_level < 0:
        raise ValueError("'scaffolding_level' debe ser mayor o igual a 0.")
    if not 0.0 <= detected_frustration <= 1.0:
        raise ValueError("'detected_frustration' debe estar entre 0.0 y 1.0.")


def _validar_textos(
    actor: str,
    text: str,
    target_concept: str,
    kolb_strategy: str,
) -> tuple[str, str, str, str]:
    actor = actor.strip()
    text = text.strip()
    target_concept = target_concept.strip()
    kolb_strategy = kolb_strategy.strip()
    if not actor:
        raise ValueError("El campo 'actor' es obligatorio.")
    if not text:
        raise ValueError("El campo 'text' es obligatorio.")
    if not target_concept:
        raise ValueError("El campo 'target_concept' es obligatorio.")
    if not kolb_strategy:
        raise ValueError("El campo 'kolb_strategy' es obligatorio.")
    return actor, text, target_concept, kolb_strategy


# ---------------------------------------------------------------------------
# Registro de herramientas MCP
# ---------------------------------------------------------------------------

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
        Registra un turno de sesion en la bitacora PostgreSQL para seguimiento pedagogico.

        alumno_id debe ser el entero correspondiente a alumnos.id en la base de datos.
        """
        try:
            payload = RegistrarBitacoraInput.model_validate(
                {
                    "alumno_id": alumno_id,
                    "sesion_id": sesion_id,
                    "turn_index": turn_index,
                    "timestamp": timestamp,
                    "actor": actor,
                    "text": text,
                    "target_concept": target_concept,
                    "kolb_strategy": kolb_strategy,
                    "scaffolding_level": scaffolding_level,
                    "detected_frustration": detected_frustration,
                    "active_misconception": active_misconception,
                    "media_ref": media_ref,
                }
            )
            alumno_id = payload.alumno_id
            sesion_id = payload.sesion_id
            turn_index = payload.turn_index
            timestamp = payload.timestamp
            actor = payload.actor
            text = payload.text
            target_concept = payload.target_concept
            kolb_strategy = payload.kolb_strategy
            scaffolding_level = payload.scaffolding_level
            detected_frustration = payload.detected_frustration
            active_misconception = payload.active_misconception
            media_ref = payload.media_ref

            alumno_int = _validar_alumno_id(alumno_id)
            sesion_id = _validar_id(sesion_id, "sesion_id")
            ts = _validar_timestamp(timestamp)
            _validar_numericos(turn_index, scaffolding_level, detected_frustration)
            actor, text, target_concept, kolb_strategy = _validar_textos(
                actor, text, target_concept, kolb_strategy
            )
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        active_misconception = active_misconception.strip() or "none"
        payload: dict = {"text": text}
        if media_ref and media_ref.strip():
            payload["media_ref"] = media_ref.strip()

        entry = BitacoraEntryDTO(
            alumno_id=alumno_int,
            sesion_id=sesion_id,
            turn_index=turn_index,
            timestamp=ts,
            actor=actor,
            payload=payload,
            target_concept=target_concept,
            kolb_strategy=kolb_strategy,
            scaffolding_level=scaffolding_level,
            detected_frustration=detected_frustration >= 0.5,
            active_misconception=active_misconception,
        )

        try:
            row = _dao().create(entry)
        except Exception as error:
            return _error_response(f"Error al guardar en PostgreSQL: {error}")

        return RegistrarBitacoraOutput.model_validate(
            {
                "ok": True,
                "message": "Registro de bitacora guardado.",
                "id": row.id,
                "record": row.to_dict(),
            }
        ).model_dump()

    @mcp.tool()
    def obtener_bitacora_sesion(alumno_id: str, sesion_id: str, limit: int = 100) -> dict:
        """Devuelve los ultimos registros de una bitacora de sesion por alumno y sesion."""
        try:
            payload = ObtenerBitacoraInput.model_validate(
                {
                    "alumno_id": alumno_id,
                    "sesion_id": sesion_id,
                    "limit": limit,
                }
            )
            alumno_id = payload.alumno_id
            sesion_id = payload.sesion_id
            limit = payload.limit

            alumno_int = _validar_alumno_id(alumno_id)
            sesion_id = _validar_id(sesion_id, "sesion_id")
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        try:
            total = _dao().count_by_session(alumno_int, sesion_id)
            rows = _dao().find_by_session(alumno_int, sesion_id, limit)
        except Exception as error:
            return _error_response(f"Error al consultar PostgreSQL: {error}")

        return ObtenerBitacoraOutput.model_validate(
            {
                "alumno_id": alumno_id,
                "sesion_id": sesion_id,
                "total_entries": total,
                "returned_entries": len(rows),
                "entries": [r.to_dict() for r in rows],
            }
        ).model_dump()

    @mcp.tool()
    def resumir_bitacora_sesion(alumno_id: str, sesion_id: str) -> dict:
        """Devuelve un resumen pedagogico de la sesion para seguimiento del aprendizaje."""
        try:
            payload = ObtenerBitacoraInput.model_validate(
                {
                    "alumno_id": alumno_id,
                    "sesion_id": sesion_id,
                    "limit": 1,
                }
            )
            alumno_id = payload.alumno_id
            sesion_id = payload.sesion_id

            alumno_int = _validar_alumno_id(alumno_id)
            sesion_id = _validar_id(sesion_id, "sesion_id")
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        try:
            rows = _dao().find_by_session(alumno_int, sesion_id, limit=10_000)
        except Exception as error:
            return _error_response(f"Error al consultar PostgreSQL: {error}")

        if not rows:
            return ResumenBitacoraOutput.model_validate(
                {
                    "alumno_id": alumno_id,
                    "sesion_id": sesion_id,
                    "summary": {
                        "total_turns": 0,
                        "message": "No hay registros para esta sesion.",
                    },
                }
            ).model_dump()

        concept_counts: dict[str, int] = {}
        misconception_counts: dict[str, int] = {}
        frustration_values: list[float] = []
        scaffolding_values: list[int] = []
        actor_counts: dict[str, int] = {}
        timeline: list[dict] = []

        for row in rows:
            actor_counts[row.actor] = actor_counts.get(row.actor, 0) + 1

            concept = row.target_concept or "sin_concepto"
            concept_counts[concept] = concept_counts.get(concept, 0) + 1

            misconception = row.active_misconception or "none"
            if misconception.lower() != "none":
                misconception_counts[misconception] = misconception_counts.get(misconception, 0) + 1

            frustration_float = 0.8 if row.detected_frustration else 0.0
            frustration_values.append(frustration_float)

            if row.scaffolding_level is not None:
                scaffolding_values.append(row.scaffolding_level)

            ts_str = (
                row.timestamp.isoformat().replace("+00:00", "Z")
                if hasattr(row.timestamp, "isoformat")
                else str(row.timestamp)
            )
            timeline.append(
                {
                    "turn_index": row.turn_index,
                    "timestamp": ts_str,
                    "target_concept": concept,
                    "scaffolding_level": row.scaffolding_level or 0,
                    "detected_frustration": frustration_float,
                }
            )

        avg_frustration = (
            round(sum(frustration_values) / len(frustration_values), 4)
            if frustration_values
            else None
        )
        avg_scaffolding = (
            round(sum(scaffolding_values) / len(scaffolding_values), 4)
            if scaffolding_values
            else None
        )
        main_concept = max(concept_counts, key=concept_counts.get) if concept_counts else None

        return ResumenBitacoraOutput.model_validate(
            {
                "alumno_id": alumno_id,
                "sesion_id": sesion_id,
                "summary": {
                    "total_turns": len(rows),
                    "actors": actor_counts,
                    "concept_coverage": concept_counts,
                    "main_concept": main_concept,
                    "average_scaffolding_level": avg_scaffolding,
                    "average_detected_frustration": avg_frustration,
                    "active_misconceptions": misconception_counts,
                    "timeline": timeline,
                },
            }
        ).model_dump()
