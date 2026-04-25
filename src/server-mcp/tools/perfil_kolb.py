"""Herramientas para gestionar el perfil de aprendizaje Kolb por alumno."""

from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from curriculo_matematica.dao.student_profile import StudentProfileDAO
from curriculo_matematica.schemas.perfil_kolb import (
    DEFAULT_ASSESSMENT_NAME,
    DEFAULT_MODEL_NAME,
    KOLB_DIMENSIONS,
    build_assessment_answer,
    build_default_profile,
)


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str


class ObtenerPerfilKolbInput(BaseModel):
    alumno_id: str = Field(min_length=1)


class ActualizarPerfilKolbInput(BaseModel):
    alumno_id: str = Field(min_length=1)
    ae_score: float = Field(ge=0.0, le=1.0)
    ro_score: float = Field(ge=0.0, le=1.0)
    ac_score: float = Field(ge=0.0, le=1.0)
    ce_score: float = Field(ge=0.0, le=1.0)
    evidencia_texto: str | None = None
    origen: str = "docente"
    status: str = "completed"
    summary: str | None = None
    assessment_name: str = DEFAULT_ASSESSMENT_NAME
    model_name: str = DEFAULT_MODEL_NAME


class PersistirPerfilKolbInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    student_id: int | str | None = None
    kolb_profile: dict[str, Any] | None = None
    current_vector: dict[str, Any] | None = None


class KolbVectorOutput(BaseModel):
    ae_score: float | None = None
    ro_score: float | None = None
    ac_score: float | None = None
    ce_score: float | None = None


class AssessmentAnswerOutput(BaseModel):
    id: int | None = None
    profile_id: int | None = None
    scenario_id: int
    dimension: str | None = None
    answer_text: str | None = None


class PerfilKolbOutput(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    student_id: str
    assessment_name: str
    model_name: str
    status: str | None = None
    style: str | None = None
    confidence: float | None = None
    kolb_vector: KolbVectorOutput
    source: str | None = None
    summary: str | None = None
    created_at: str | None = None
    assessment_answers: list[AssessmentAnswerOutput] = []
    scenarios_completed: list[int] = []


class PerfilKolbUpsertResponse(BaseModel):
    ok: bool
    message: str
    storage: str
    profile: PerfilKolbOutput

@lru_cache(maxsize=1)
def _dao() -> StudentProfileDAO:
    return StudentProfileDAO()


def _error_response(message: str, **kwargs: Any) -> dict:
    return ErrorResponse.model_validate({"error": message, **kwargs}).model_dump()


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now() -> str:
    return _utc_now_dt().isoformat().replace("+00:00", "Z")


def _validar_student_id(value: str) -> int:
    value = value.strip()
    if not value:
        raise ValueError("El campo 'student_id' es obligatorio.")
    if not value.isdigit():
        raise ValueError("'student_id' debe ser numerico (FK a alumnos.id).")
    student_id = int(value)
    if student_id <= 0:
        raise ValueError("'student_id' debe ser un entero positivo.")
    return student_id


def _validar_score(score: float, dimension: str) -> float:
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"El score de '{dimension}' debe estar entre 0.0 y 1.0.")
    return float(score)


def _default_profile(student_id: int) -> dict:
    return build_default_profile(student_id=str(student_id), updated_at=_utc_now())


def _infer_style(kolb_vector: dict[str, float]) -> str:
    ac = kolb_vector["ac_score"]
    ce = kolb_vector["ce_score"]
    ae = kolb_vector["ae_score"]
    ro = kolb_vector["ro_score"]

    if ac >= ce and ae >= ro:
        return "Converging"
    if ac >= ce and ro > ae:
        return "Assimilating"
    if ce > ac and ro >= ae:
        return "Diverging"
    return "Accommodating"


def _confidence(kolb_vector: dict[str, float]) -> float:
    ordered = sorted(kolb_vector.values(), reverse=True)
    if len(ordered) < 2:
        return 0.0
    return round(max(0.0, ordered[0] - ordered[1]), 4)


def _normalize_profile(kolb_vector: dict[str, float]) -> dict[str, float]:
    total = sum(kolb_vector.values())
    if total <= 0:
        equal = round(1.0 / len(KOLB_DIMENSIONS), 4)
        return {dim: equal for dim in KOLB_DIMENSIONS}

    normalized = {dim: round(kolb_vector[dim] / total, 4) for dim in KOLB_DIMENSIONS}
    diff = round(1.0 - sum(normalized.values()), 4)
    if diff != 0:
        normalized[KOLB_DIMENSIONS[0]] = round(normalized[KOLB_DIMENSIONS[0]] + diff, 4)
    return normalized


def _parse_answers(evidencia_texto: str | None, scenario_id: int = 0) -> list[dict]:
    if not evidencia_texto or not evidencia_texto.strip():
        return []
    return [
        build_assessment_answer(
            scenario_id=scenario_id,
            dimension="RO",
            answer_text=evidencia_texto.strip(),
        )
    ]


def _extract_scenarios_completed(assessment_answers: list[dict]) -> list[int]:
    return sorted({int(item["scenario_id"]) for item in assessment_answers})


def _as_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return dumped
    legacy_dict = getattr(value, "dict", None)
    if callable(legacy_dict):
        dumped = legacy_dict()
        if isinstance(dumped, dict):
            return dumped
    raw = getattr(value, "__dict__", None)
    if isinstance(raw, dict):
        return dict(raw)
    return {}


def _get_value(item: object, key: str, default: object = None) -> object:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _normalize_payload_answers(answers: list[object] | None) -> list[dict]:
    normalized: list[dict] = []
    for item in answers or []:
        try:
            scenario_id_raw = _coalesce(
                _get_value(item, "scenario_id"),
                _get_value(item, "scenarioId"),
            )
            scenario_id = int(scenario_id_raw)
        except Exception as error:
            raise ValueError("Cada answer debe incluir 'scenario_id' numerico.") from error

        dimension = str(_get_value(item, "dimension") or "").strip().upper()
        if dimension not in {"AE", "RO", "AC", "CE"}:
            raise ValueError("Cada answer debe incluir 'dimension' en {AE, RO, AC, CE}.")

        answer_text = str(
            _coalesce(
                _get_value(item, "answer"),
                _get_value(item, "answer_text"),
                _get_value(item, "answerText"),
                _get_value(item, "response"),
                _get_value(item, "texto"),
                "",
            )
        ).strip()
        normalized.append(
            build_assessment_answer(
                scenario_id=scenario_id,
                dimension=dimension,
                answer_text=answer_text,
            )
        )
    return normalized


def _normalize_payload_scenarios(raw_value: object) -> list[int]:
    if isinstance(raw_value, list):
        return sorted({int(value) for value in raw_value})
    if isinstance(raw_value, tuple | set):
        return sorted({int(value) for value in raw_value})
    if isinstance(raw_value, int):
        if raw_value <= 0:
            return []
        return list(range(1, raw_value + 1))
    if isinstance(raw_value, str):
        value = raw_value.strip()
        if not value:
            return []
        if "," in value:
            return sorted({int(part.strip()) for part in value.split(",") if part.strip()})
        return [int(value)]
    return []


def _coalesce(*values: object) -> object:
    for value in values:
        if value is not None:
            return value
    return None


def _vector_component(vector: dict, key_short: str, key_long: str) -> float:
    candidates = [
        vector.get(key_short),
        vector.get(key_short.upper()),
        vector.get(key_short.lower()),
        vector.get(key_long),
        vector.get(key_long.upper()),
        vector.get(key_long.lower()),
    ]
    value = _coalesce(*candidates)
    if value is None:
        return 0.0
    return float(value)


def _build_profile_from_agent_payload(payload: dict) -> dict:
    payload_dict = _as_dict(payload)
    nested_raw = payload_dict.get("kolb_profile")
    nested = _as_dict(nested_raw) if nested_raw is not None else payload_dict
    if not nested:
        raise ValueError("El payload debe incluir datos de perfil Kolb.")

    student_id_raw = nested.get("student_id", payload_dict.get("student_id", ""))
    student_id = _validar_student_id(str(student_id_raw))

    vector_raw = _coalesce(
        nested.get("current_vector"),
        payload_dict.get("current_vector"),
        nested.get("kolb_vector"),
        payload_dict.get("kolb_vector"),
    )
    vector = _as_dict(vector_raw)
    if not vector:
        raise ValueError("'current_vector' o 'kolb_vector' es obligatorio en el perfil Kolb.")

    kolb_vector = {
        "ae_score": _validar_score(_vector_component(vector, "ae", "ae_score"), "AE"),
        "ro_score": _validar_score(_vector_component(vector, "ro", "ro_score"), "RO"),
        "ac_score": _validar_score(_vector_component(vector, "ac", "ac_score"), "AC"),
        "ce_score": _validar_score(_vector_component(vector, "ce", "ce_score"), "CE"),
    }
    kolb_vector = _normalize_profile(kolb_vector)

    style = (
        str(nested.get("style") or "").strip()
        or str(payload_dict.get("kolb_style") or "").strip()
        or _infer_style(kolb_vector)
    )

    confidence_raw = nested.get("confidence", payload_dict.get("confidence"))
    confidence = float(confidence_raw) if confidence_raw is not None else _confidence(kolb_vector)
    confidence = round(max(0.0, min(1.0, confidence)), 4)

    answers_raw = _coalesce(
        nested.get("answers"),
        nested.get("assessment_answers"),
        nested.get("assesment_answers"),
        nested.get("assessmentAnswers"),
        payload_dict.get("answers"),
        payload_dict.get("assessment_answers"),
        payload_dict.get("assesment_answers"),
        payload_dict.get("assessmentAnswers"),
    )
    assessment_answers = _normalize_payload_answers(answers_raw)

    scenarios_raw = _coalesce(
        nested.get("answered_scenarios"),
        nested.get("scenarios_completed"),
        nested.get("answeredScenarios"),
        nested.get("scenariosCompleted"),
        nested.get("scenario_completed"),
        payload_dict.get("answered_scenarios"),
        payload_dict.get("scenarios_completed"),
        payload_dict.get("answeredScenarios"),
        payload_dict.get("scenariosCompleted"),
        payload_dict.get("scenario_completed"),
    )
    scenarios_completed = _normalize_payload_scenarios(scenarios_raw)
    if not scenarios_completed:
        scenarios_completed = _extract_scenarios_completed(assessment_answers)


    return {
        "student_id": student_id,
        "status": str(payload_dict.get("status") or "completed").strip() or "completed",
        "style": style,
        "confidence": confidence,
        "kolb_vector": kolb_vector,
        "source": str(_coalesce(nested.get("source"), payload_dict.get("source"), "agente")).strip()
        or "agente",
        "summary": str(_coalesce(nested.get("summary"), payload_dict.get("summary"), "")).strip(),
        "assessment_answers": assessment_answers,
        "scenarios_completed": scenarios_completed,
        "assessment_name": str(
            _coalesce(nested.get("assessment_name"), payload_dict.get("assessment_name"), DEFAULT_ASSESSMENT_NAME)
        ).strip()
        or DEFAULT_ASSESSMENT_NAME,
        "model_name": str(
            _coalesce(nested.get("model_name"), payload_dict.get("model_name"), DEFAULT_MODEL_NAME)
        ).strip()
        or DEFAULT_MODEL_NAME,
    }


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_perfil_kolb(alumno_id: str) -> dict:
        """Obtiene el perfil Kolb actual de un alumno."""
        try:
            payload = ObtenerPerfilKolbInput.model_validate({"alumno_id": alumno_id})
            alumno_id = payload.alumno_id
            student_id = _validar_student_id(alumno_id)
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        try:
            profile = _dao().get_by_student_id(student_id)
        except Exception as error:
            return _error_response(
                "No se pudo consultar PostgreSQL via DAO.",
                detail=str(error),
                student_id=str(student_id),
            )

        if profile is None:
            return _error_response(
                f"No existe perfil Kolb para el alumno '{student_id}'.",
                student_id=str(student_id),
                not_found=True,
            )
        return PerfilKolbOutput.model_validate(profile).model_dump()

    @mcp.tool()
    def actualizar_perfil_kolb(
        alumno_id: str,
        ae_score: float,
        ro_score: float,
        ac_score: float,
        ce_score: float,
        evidencia_texto: str | None = None,
        origen: str = "docente",
        status: str = "completed",
        summary: str | None = None,
        assessment_name: str = DEFAULT_ASSESSMENT_NAME,
        model_name: str = DEFAULT_MODEL_NAME,
    ) -> dict:
        """
        Actualiza el perfil Kolb de un alumno.

        Los valores deben estar en [0.0, 1.0] y luego se normalizan para que sumen 1.0.
        """
        try:
            payload = ActualizarPerfilKolbInput.model_validate(
                {
                    "alumno_id": alumno_id,
                    "ae_score": ae_score,
                    "ro_score": ro_score,
                    "ac_score": ac_score,
                    "ce_score": ce_score,
                    "evidencia_texto": evidencia_texto,
                    "origen": origen,
                    "status": status,
                    "summary": summary,
                    "assessment_name": assessment_name,
                    "model_name": model_name,
                }
            )
            alumno_id = payload.alumno_id
            ae_score = payload.ae_score
            ro_score = payload.ro_score
            ac_score = payload.ac_score
            ce_score = payload.ce_score
            evidencia_texto = payload.evidencia_texto
            origen = payload.origen
            status = payload.status
            summary = payload.summary
            assessment_name = payload.assessment_name
            model_name = payload.model_name
            student_id = _validar_student_id(alumno_id)
            kolb_vector = {
                "ae_score": _validar_score(ae_score, "ae_score"),
                "ro_score": _validar_score(ro_score, "ro_score"),
                "ac_score": _validar_score(ac_score, "ac_score"),
                "ce_score": _validar_score(ce_score, "ce_score"),
            }
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        kolb_vector = _normalize_profile(kolb_vector)
        style = _infer_style(kolb_vector)
        confidence = _confidence(kolb_vector)
        assessment_answers = _parse_answers(evidencia_texto=evidencia_texto)
        scenarios_completed = _extract_scenarios_completed(assessment_answers)

        try:
            existing = _dao().get_by_student_id(student_id)
        except Exception as error:
            return _error_response(
                "No se pudo consultar PostgreSQL via DAO.",
                detail=str(error),
                student_id=str(student_id),
            )

        if existing is None:
            profile = _default_profile(student_id)
        else:
            profile = existing

        profile["kolb_vector"] = kolb_vector
        profile["style"] = style
        profile["confidence"] = confidence
        profile["status"] = status
        profile["source"] = origen.strip() or "docente"
        profile["summary"] = (summary or "").strip()
        profile["assessment_name"] = assessment_name.strip() or DEFAULT_ASSESSMENT_NAME
        profile["model_name"] = model_name.strip() or DEFAULT_MODEL_NAME
        profile["updated_at"] = _utc_now()
        profile["assessment_answers"] = assessment_answers
        profile["scenarios_completed"] = scenarios_completed

        try:
            persisted = _dao().upsert_profile(
                student_id=student_id,
                status=profile["status"],
                style=profile["style"],
                confidence=profile["confidence"],
                kolb_vector=profile["kolb_vector"],
                source=profile["source"],
                summary=profile["summary"],
                assessment_answers=profile["assessment_answers"],
                scenarios_completed=profile["scenarios_completed"],
                assessment_name=profile["assessment_name"],
                model_name=profile["model_name"],
            )
        except Exception as error:
            return _error_response(
                "No se pudo guardar en PostgreSQL via DAO.",
                detail=str(error),
                student_id=str(student_id),
            )

        return PerfilKolbUpsertResponse.model_validate(
            {
                "ok": True,
                "message": "Perfil Kolb actualizado.",
                "storage": "postgresql-sqlalchemy-dao",
                "profile": persisted,
            }
        ).model_dump()

    @mcp.tool()
    def persistir_perfil_kolb(payload: dict) -> dict:
        """Persiste un perfil Kolb recibido como objeto JSON anidado desde un agente."""
        try:
            payload_model = PersistirPerfilKolbInput.model_validate(payload)
            mapped = _build_profile_from_agent_payload(payload_model.model_dump())
        except (ValidationError, ValueError) as error:
            return _error_response(str(error))

        try:
            persisted = _dao().upsert_profile(
                student_id=mapped["student_id"],
                status=mapped["status"],
                style=mapped["style"],
                confidence=mapped["confidence"],
                kolb_vector=mapped["kolb_vector"],
                source=mapped["source"],
                summary=mapped["summary"],
                assessment_answers=mapped["assessment_answers"],
                scenarios_completed=mapped["scenarios_completed"],
                assessment_name=mapped["assessment_name"],
                model_name=mapped["model_name"],
            )
        except Exception as error:
            return _error_response(
                "No se pudo guardar en PostgreSQL via DAO.",
                detail=str(error),
                student_id=str(mapped["student_id"]),
            )

        return PerfilKolbUpsertResponse.model_validate(
            {
                "ok": True,
                "message": "Perfil Kolb persistido desde payload de agente.",
                "storage": "postgresql-sqlalchemy-dao",
                "profile": persisted,
            }
        ).model_dump()
