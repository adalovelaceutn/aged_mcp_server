"""Gateway de acceso curricular basado en DAO + bootstrap inicial."""

from __future__ import annotations

from functools import lru_cache

from curriculo_matematica.dao.curriculo import CurriculoDAO


@lru_cache(maxsize=1)
def get_curriculo_dao() -> CurriculoDAO:
    """Devuelve un DAO listo para usar contra la DB externa."""
    return CurriculoDAO()
