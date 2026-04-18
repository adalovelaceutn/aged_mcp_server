"""Herramientas para gestionar el perfil de aprendizaje Kolb por alumno."""

from __future__ import annotations

import json
import os
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


def _storage_backend() -> str:
    backend = os.getenv("KOLB_STORAGE_BACKEND", "postgres").strip().lower()
    return backend if backend in {"postgres", "json"} else "postgres"


def _database_url() -> str:
    url = os.getenv("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "La variable de entorno NEON_DATABASE_URL no está configurada. "
            "Defínela antes de arrancar el servidor."
        )
    return url


def _build_profile_from_row(row: dict) -> dict:
    updated_at = row["updated_at"]
    if hasattr(updated_at, "isoformat"):
        updated_at = updated_at.isoformat().replace("+00:00", "Z")

    evidencia = row.get("evidencia")
    if not isinstance(evidencia, list):
        evidencia = []

    return {
        "alumno_id": row["alumno_id"],
        "updated_at": updated_at,
        "kolb_profile": {
            "activo": float(row["kolb_activo"]),
            "reflexivo": float(row["kolb_reflexivo"]),
            "teorico": float(row["kolb_teorico"]),
            "pragmatico": float(row["kolb_pragmatico"]),
        },
        "preferencia_principal": row["preferencia_principal"],
        "evidencia": evidencia,
    }


def _ensure_student_profile_table(conn) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS student_profile (
                id BIGSERIAL PRIMARY KEY,
                alumno_id VARCHAR(255) NOT NULL UNIQUE,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                kolb_activo NUMERIC(5, 4) NOT NULL,
                kolb_reflexivo NUMERIC(5, 4) NOT NULL,
                kolb_teorico NUMERIC(5, 4) NOT NULL,
                kolb_pragmatico NUMERIC(5, 4) NOT NULL,
                preferencia_principal VARCHAR(32) NOT NULL,
                evidencia JSONB NOT NULL DEFAULT '[]'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


def _fetch_profile_from_postgres(alumno_id: str) -> dict | None:
    from psycopg import connect
    from psycopg.rows import dict_row

    with connect(_database_url(), autocommit=True, row_factory=dict_row) as conn:
        _ensure_student_profile_table(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    alumno_id,
                    updated_at,
                    kolb_activo,
                    kolb_reflexivo,
                    kolb_teorico,
                    kolb_pragmatico,
                    preferencia_principal,
                    evidencia
                FROM student_profile
                WHERE alumno_id = %s
                """,
                (alumno_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None
    return _build_profile_from_row(row)


def _upsert_profile_in_postgres(profile: dict) -> None:
    from psycopg import connect

    with connect(_database_url(), autocommit=True) as conn:
        _ensure_student_profile_table(conn)
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO student_profile (
                    alumno_id,
                    updated_at,
                    kolb_activo,
                    kolb_reflexivo,
                    kolb_teorico,
                    kolb_pragmatico,
                    preferencia_principal,
                    evidencia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (alumno_id) DO UPDATE SET
                    updated_at = EXCLUDED.updated_at,
                    kolb_activo = EXCLUDED.kolb_activo,
                    kolb_reflexivo = EXCLUDED.kolb_reflexivo,
                    kolb_teorico = EXCLUDED.kolb_teorico,
                    kolb_pragmatico = EXCLUDED.kolb_pragmatico,
                    preferencia_principal = EXCLUDED.preferencia_principal,
                    evidencia = EXCLUDED.evidencia
                """,
                (
                    profile["alumno_id"],
                    profile["updated_at"],
                    profile["kolb_profile"]["activo"],
                    profile["kolb_profile"]["reflexivo"],
                    profile["kolb_profile"]["teorico"],
                    profile["kolb_profile"]["pragmatico"],
                    profile["preferencia_principal"],
                    json.dumps(profile["evidencia"], ensure_ascii=False),
                ),
            )


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

        if _storage_backend() == "postgres":
            try:
                profile = _fetch_profile_from_postgres(alumno_id)
            except Exception as error:
                return {
                    "error": "No se pudo consultar Neon/PostgreSQL.",
                    "detail": str(error),
                    "alumno_id": alumno_id,
                }

            if profile is None:
                return {
                    "error": f"No existe perfil Kolb para el alumno '{alumno_id}'.",
                    "alumno_id": alumno_id,
                    "not_found": True,
                }
            return profile

        profile_file = _profile_file_path(alumno_id)
        if not profile_file.exists():
            return {
                "error": f"No existe perfil Kolb para el alumno '{alumno_id}'.",
                "alumno_id": alumno_id,
                "not_found": True,
            }

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
        if _storage_backend() == "postgres":
            try:
                profile = _fetch_profile_from_postgres(alumno_id)
            except Exception as error:
                return {
                    "error": "No se pudo consultar Neon/PostgreSQL.",
                    "detail": str(error),
                    "alumno_id": alumno_id,
                }

            if profile is None:
                profile = _default_profile(alumno_id)
        else:
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

        if _storage_backend() == "postgres":
            try:
                _upsert_profile_in_postgres(profile)
            except Exception as error:
                return {
                    "error": "No se pudo guardar en Neon/PostgreSQL.",
                    "detail": str(error),
                    "alumno_id": alumno_id,
                }
            profile_ref = f"student_profile:{alumno_id}"
        else:
            profile_file = _profile_file_path(alumno_id)
            with profile_file.open("w", encoding="utf-8") as handler:
                json.dump(profile, handler, ensure_ascii=False, indent=2)
            profile_ref = str(profile_file)

        return {
            "ok": True,
            "message": "Perfil Kolb actualizado.",
            "storage": _storage_backend(),
            "profile_file": profile_ref,
            "profile": profile,
        }
