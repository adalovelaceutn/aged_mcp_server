"""Herramientas para gestionar el perfil de aprendizaje Kolb por alumno."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from curriculo_matematica.schemas.perfil_kolb import (
    KOLB_DIMENSIONS,
    build_default_profile,
    build_evidencia,
)

_SAFE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
_PROFILE_BASE_DIR = Path(__file__).resolve().parents[3] / "student_profiles"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _profile_file_path(alumno_id: str) -> Path:
    return _PROFILE_BASE_DIR / f"{alumno_id}.json"


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

        profile_file = _profile_file_path(alumno_id)
        if not profile_file.exists():
            default_profile = _default_profile(alumno_id)
            profile_file.parent.mkdir(parents=True, exist_ok=True)
            with profile_file.open("w", encoding="utf-8") as handler:
                json.dump(default_profile, handler, ensure_ascii=False, indent=2)
            return default_profile

        with profile_file.open("r", encoding="utf-8") as handler:
            return json.load(handler)

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
        profile_file = _profile_file_path(alumno_id)

        profile_file.parent.mkdir(parents=True, exist_ok=True)
        if profile_file.exists():
            with profile_file.open("r", encoding="utf-8") as handler:
                profile = json.load(handler)
        else:
            profile = _default_profile(alumno_id)

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
        profile["evidencia"] = evidencia[-100:]

        with profile_file.open("w", encoding="utf-8") as handler:
            json.dump(profile, handler, ensure_ascii=False, indent=2)

        return {
            "ok": True,
            "message": "Perfil Kolb actualizado.",
            "profile_file": str(profile_file),
            "profile": profile,
        }
