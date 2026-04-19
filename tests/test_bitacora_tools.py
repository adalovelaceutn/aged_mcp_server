from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from curriculo_matematica.tools import bitacora


@dataclass
class _FakeBitacoraRow:
    id: int
    alumno_id: int
    sesion_id: str
    turn_index: int
    timestamp: datetime
    actor: str
    payload: dict
    target_concept: str
    kolb_strategy: str
    scaffolding_level: int
    detected_frustration: bool
    active_misconception: str

    def to_dict(self) -> dict:
        ts = self.timestamp.isoformat().replace("+00:00", "Z")
        return {
            "alumno_id": str(self.alumno_id),
            "sesion_id": self.sesion_id,
            "data": {
                "turn_index": self.turn_index,
                "timestamp": ts,
                "actor": self.actor,
                "payload": self.payload or {},
                "pedagogical_context": {
                    "target_concept": self.target_concept,
                    "kolb_strategy": self.kolb_strategy,
                    "scaffolding_level": self.scaffolding_level,
                    "detected_frustration": 0.8 if self.detected_frustration else 0.0,
                    "active_misconception": self.active_misconception,
                },
            },
        }


class _FakeBitacoraDAO:
    def __init__(self) -> None:
        self._rows: list[_FakeBitacoraRow] = []
        self._next_id = 1

    def create(self, entry):
        row = _FakeBitacoraRow(
            id=self._next_id,
            alumno_id=entry.alumno_id,
            sesion_id=entry.sesion_id,
            turn_index=entry.turn_index,
            timestamp=entry.timestamp,
            actor=entry.actor,
            payload=entry.payload,
            target_concept=entry.target_concept,
            kolb_strategy=entry.kolb_strategy,
            scaffolding_level=entry.scaffolding_level,
            detected_frustration=entry.detected_frustration,
            active_misconception=entry.active_misconception,
        )
        self._next_id += 1
        self._rows.append(row)
        return row

    def count_by_session(self, alumno_id: int, sesion_id: str) -> int:
        return len(
            [r for r in self._rows if r.alumno_id == alumno_id and r.sesion_id == sesion_id]
        )

    def find_by_session(self, alumno_id: int, sesion_id: str, limit: int = 100):
        rows = [r for r in self._rows if r.alumno_id == alumno_id and r.sesion_id == sesion_id]
        rows.sort(key=lambda r: r.turn_index)
        return rows[-limit:]


def _register_bitacora(fake_mcp):
    bitacora.register(fake_mcp)
    return fake_mcp.tools


def test_registrar_y_obtener_bitacora_sesion(monkeypatch, fake_mcp):
    fake_dao = _FakeBitacoraDAO()
    monkeypatch.setattr(bitacora, "_dao", lambda: fake_dao)
    tools = _register_bitacora(fake_mcp)

    registro = tools["registrar_bitacora_sesion"](
        alumno_id="101",
        sesion_id="math_2026_04_17",
        turn_index=5,
        timestamp="2026-04-17T17:34:00Z",
        actor="Lovelace_Tutor",
        text="Que pasaria si dividimos esa pizza en 8 partes...?",
        target_concept="fracciones_equivalentes",
        kolb_strategy="activo_experimental",
        scaffolding_level=2,
        detected_frustration=0.1,
        active_misconception="none",
        media_ref="v123_video_particion.mp4",
    )

    consulta = tools["obtener_bitacora_sesion"]("101", "math_2026_04_17")

    assert registro["ok"] is True
    assert consulta["total_entries"] == 1
    assert consulta["entries"][0]["data"]["pedagogical_context"]["kolb_strategy"] == "activo_experimental"


def test_registrar_bitacora_valida_campos(monkeypatch, fake_mcp):
    fake_dao = _FakeBitacoraDAO()
    monkeypatch.setattr(bitacora, "_dao", lambda: fake_dao)
    tools = _register_bitacora(fake_mcp)

    invalid_id = tools["registrar_bitacora_sesion"](
        alumno_id="luis navarro",
        sesion_id="math_2026_04_17",
        turn_index=0,
        timestamp="2026-04-17T17:34:00Z",
        actor="Tutor",
        text="hola",
        target_concept="fracciones",
        kolb_strategy="activo",
        scaffolding_level=0,
        detected_frustration=0.0,
    )
    invalid_frustration = tools["registrar_bitacora_sesion"](
        alumno_id="101",
        sesion_id="math_2026_04_17",
        turn_index=0,
        timestamp="2026-04-17T17:34:00Z",
        actor="Tutor",
        text="hola",
        target_concept="fracciones",
        kolb_strategy="activo",
        scaffolding_level=0,
        detected_frustration=1.5,
    )

    assert "error" in invalid_id
    assert "error" in invalid_frustration


def test_obtener_bitacora_limit_y_orden(monkeypatch, fake_mcp):
    fake_dao = _FakeBitacoraDAO()
    monkeypatch.setattr(bitacora, "_dao", lambda: fake_dao)
    tools = _register_bitacora(fake_mcp)

    for turn_index in [3, 1, 2]:
        tools["registrar_bitacora_sesion"](
            alumno_id="202",
            sesion_id="s1",
            turn_index=turn_index,
            timestamp=f"2026-04-17T17:3{turn_index}:00Z",
            actor="Tutor",
            text=f"turno {turn_index}",
            target_concept="concepto",
            kolb_strategy="reflexivo",
            scaffolding_level=1,
            detected_frustration=0.2,
        )

    result = tools["obtener_bitacora_sesion"]("202", "s1", limit=2)
    turnos = [entry["data"]["turn_index"] for entry in result["entries"]]

    assert result["returned_entries"] == 2
    assert turnos == [2, 3]


def test_resumir_bitacora_sesion_agrega_metricas(monkeypatch, fake_mcp):
    fake_dao = _FakeBitacoraDAO()
    monkeypatch.setattr(bitacora, "_dao", lambda: fake_dao)
    tools = _register_bitacora(fake_mcp)

    tools["registrar_bitacora_sesion"](
        alumno_id="303",
        sesion_id="s2",
        turn_index=1,
        timestamp="2026-04-17T17:30:00Z",
        actor="Tutor",
        text="texto 1",
        target_concept="fracciones_equivalentes",
        kolb_strategy="activo",
        scaffolding_level=2,
        detected_frustration=0.2,
        active_misconception="parte_todo",
    )
    tools["registrar_bitacora_sesion"](
        alumno_id="303",
        sesion_id="s2",
        turn_index=2,
        timestamp="2026-04-17T17:31:00Z",
        actor="Alumno",
        text="texto 2",
        target_concept="fracciones_equivalentes",
        kolb_strategy="reflexivo",
        scaffolding_level=1,
        detected_frustration=0.4,
        active_misconception="none",
    )

    resumen = tools["resumir_bitacora_sesion"]("303", "s2")
    summary = resumen["summary"]

    assert summary["total_turns"] == 2
    assert summary["main_concept"] == "fracciones_equivalentes"
    assert summary["average_scaffolding_level"] == 1.5
    assert summary["average_detected_frustration"] == 0.0
    assert summary["active_misconceptions"]["parte_todo"] == 1


def test_resumir_bitacora_sesion_vacia(monkeypatch, fake_mcp):
    fake_dao = _FakeBitacoraDAO()
    monkeypatch.setattr(bitacora, "_dao", lambda: fake_dao)
    tools = _register_bitacora(fake_mcp)

    resumen = tools["resumir_bitacora_sesion"]("404", "sin_datos")

    assert resumen["summary"]["total_turns"] == 0
    assert "message" in resumen["summary"]
