"""Fixtures y utilidades compartidas para pruebas unitarias del servidor MCP."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


class FakeMCP:
    """Implementacion minima de FastMCP para capturar herramientas/recursos."""

    def __init__(self) -> None:
        self.tools: dict[str, object] = {}
        self.resources: dict[str, object] = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def resource(self, uri: str):
        def decorator(func):
            self.resources[uri] = func
            return func

        return decorator


@pytest.fixture()
def fake_mcp() -> FakeMCP:
    return FakeMCP()
