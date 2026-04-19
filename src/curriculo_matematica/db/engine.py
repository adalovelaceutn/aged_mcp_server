"""Motor SQLAlchemy compartido para toda la aplicacion.

Usa NEON_DATABASE_URL como fuente de conexion. Tanto el perfil Kolb como
la bitacora reutilizan este modulo para acceder a la misma base de datos.
"""

from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM del proyecto."""


def _database_url() -> str:
    url = os.getenv("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "La variable de entorno NEON_DATABASE_URL no esta configurada. "
            "Definela antes de arrancar el servidor."
        )
    # SQLAlchemy 2.x usa psycopg3 con el esquema 'postgresql+psycopg://'.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache(maxsize=1)
def get_engine():
    """Devuelve el motor SQLAlchemy (singleton por proceso)."""
    return create_engine(
        _database_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )


def get_session_factory():
    """Devuelve una fabrica de sesiones ligada al motor singleton."""
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
