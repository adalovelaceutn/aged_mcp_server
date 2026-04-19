"""Herramientas para gestionar el perfil de aprendizaje Kolb por alumno."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.dao.student_profile import StudentProfileDAO
from curriculo_matematica.schemas.perfil_kolb import (
    KOLB_DIMENSIONS,
    build_default_profile,
    build_evidencia,
)

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


@lru_cache(maxsize=1)
def _dao() -> StudentProfileDAO:
    return StudentProfileDAO()


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now() -> str:
    return _utc_now_dt().isoformat().replace("+00:00", "Z")


def _validar_alumno_id(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El campo 'alumno_id' es obligatorio.")
    if not _SAFE_ID_PATTERN.fullmatch(value):
        raise ValueError("'alumno_id' solo admite letras, numeros, guion y guion bajo.")
    return value


def _validar_score(score: float, dimension: str) -> float:
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"El score de '{dimension}' debe estar entre 0.0 y 1.0.")
    return float(score)


def _default_profile(alumno_id: str) -> dict:
    return build_default_profile(alumno_id=alumno_id, updated_at=_utc_now())


def _main_preference(kolb_profile: dict[str, float]) -> str:
    max_score = max(kolb_profile.values())
    principales = [dim for dim, score in kolb_profile.items() if score == max_score]
    if len(principales) > 1:
        return "equilibrado"
    return principales[0]


def _normalize_profile(kolb_profile: dict[str, float]) -> dict[str, float]:
    total = sum(kolb_profile.values())
    if total <= 0:
        equal = round(1.0 / len(KOLB_DIMENSIONS), 4)
        return {dim: equal for dim in KOLB_DIMENSIONS}

    normalized = {dim: round(kolb_profile[dim] / total, 4) for dim in KOLB_DIMENSIONS}
    diff = round(1.0 - sum(normalized.values()), 4)
    if diff != 0:
        normalized[KOLB_DIMENSIONS[0]] = round(normalized[KOLB_DIMENSIONS[0]] + diff, 4)
    return normalized


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_perfil_kolb(alumno_id: str) -> dict:
        """Obtiene el perfil Kolb actual de un alumno."""
        try:
            alumno_id = _validar_alumno_id(alumno_id)
        except ValueError as error:
            return {"error": str(error)}

        try:
            row = _dao().get_by_alumno_id(alumno_id)
        except Exception as error:
            return {
                "error": "No se pudo consultar PostgreSQL via DAO.",
                "detail": str(error),
                "alumno_id": alumno_id,
            }

        if row is None:
            return {
                "error": f"No existe perfil Kolb para el alumno '{alumno_id}'.",
                "alumno_id": alumno_id,
                "not_found": True,
            }
        return row.to_profile_dict()

    @mcp.tool()
    def actualizar_perfil_kolb(
        alumno_id: str,
        activo: float,
        reflexivo: float,
        teorico: float,
        pragmatico: float,
        evidencia_texto: str | None = None,
        origen: str = "docente",
    ) -> dict:
        """
        Actualiza el perfil Kolb de un alumno.

        Los valores deben estar en [0.0, 1.0] y luego se normalizan para que sumen 1.0.
        """
        try:
            alumno_id = _validar_alumno_id(alumno_id)
            kolb_profile = {
                "activo": _validar_score(activo, "activo"),
                "reflexivo": _validar_score(reflexivo, "reflexivo"),
                "teorico": _validar_score(teorico, "teorico"),
                "pragmatico": _validar_score(pragmatico, "pragmatico"),
            }
        except ValueError as error:
            return {"error": str(error)}

        kolb_profile = _normalize_profile(kolb_profile)

        try:
            existing = _dao().get_by_alumno_id(alumno_id)
        except Exception as error:
            return {
                "error": "No se pudo consultar PostgreSQL via DAO.",
                "detail": str(error),
                "alumno_id": alumno_id,
            }

        if existing is None:
            profile = _default_profile(alumno_id)
        else:
            profile = existing.to_profile_dict()

        profile["kolb_profile"] = kolb_profile
        profile["preferencia_principal"] = _main_preference(kolb_profile)
        profile["updated_at"] = _utc_now()

        evidencia = profile.get("evidencia", [])
        if not isinstance(evidencia, list):
            evidencia = []
        if evidencia_texto and evidencia_texto.strip():
            evidencia.append(
                build_evidencia(
                    timestamp=_utc_now(),
                    origen=origen.strip() or "docente",
                    texto=evidencia_texto.strip(),
                )
            )
        evidencia = evidencia[-100:]
        profile["evidencia"] = evidencia

        try:
            row = _dao().upsert_profile(
                alumno_id=alumno_id,
                updated_at=_utc_now_dt(),
                kolb_profile=kolb_profile,
                preferencia_principal=profile["preferencia_principal"],
                evidencia=evidencia,
            )
        except Exception as error:
            return {
                "error": "No se pudo guardar en PostgreSQL via DAO.",
                "detail": str(error),
                "alumno_id": alumno_id,
            }

        return {
            "ok": True,
            "message": "Perfil Kolb actualizado.",
            "storage": "postgresql-sqlalchemy-dao",
            "profile": row.to_profile_dict(),
        }
