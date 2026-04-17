from __future__ import annotations

from curriculo_matematica.tools import bitacora


def _register_bitacora(fake_mcp):
    bitacora.register(fake_mcp)
    return fake_mcp.tools


def test_registrar_y_obtener_bitacora_sesion(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setattr(bitacora, "_DEFAULT_BASE_DIR", tmp_path / "session_logs")
    tools = _register_bitacora(fake_mcp)

    registro = tools["registrar_bitacora_sesion"](
        alumno_id="luis_navarro_001",
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

    consulta = tools["obtener_bitacora_sesion"]("luis_navarro_001", "math_2026_04_17")

    assert registro["ok"] is True
    assert consulta["total_entries"] == 1
    assert consulta["entries"][0]["data"]["pedagogical_context"]["kolb_strategy"] == "activo_experimental"


def test_registrar_bitacora_valida_campos(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setattr(bitacora, "_DEFAULT_BASE_DIR", tmp_path / "session_logs")
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
        alumno_id="luis_navarro_001",
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


def test_obtener_bitacora_limit_y_orden(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setattr(bitacora, "_DEFAULT_BASE_DIR", tmp_path / "session_logs")
    tools = _register_bitacora(fake_mcp)

    for turn_index in [3, 1, 2]:
        tools["registrar_bitacora_sesion"](
            alumno_id="ana_001",
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

    result = tools["obtener_bitacora_sesion"]("ana_001", "s1", limit=2)
    turnos = [entry["data"]["turn_index"] for entry in result["entries"]]

    assert result["returned_entries"] == 2
    assert turnos == [1, 2]


def test_resumir_bitacora_sesion_agrega_metricas(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setattr(bitacora, "_DEFAULT_BASE_DIR", tmp_path / "session_logs")
    tools = _register_bitacora(fake_mcp)

    tools["registrar_bitacora_sesion"](
        alumno_id="ana_001",
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
        alumno_id="ana_001",
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

    resumen = tools["resumir_bitacora_sesion"]("ana_001", "s2")
    summary = resumen["summary"]

    assert summary["total_turns"] == 2
    assert summary["main_concept"] == "fracciones_equivalentes"
    assert summary["average_scaffolding_level"] == 1.5
    assert summary["average_detected_frustration"] == 0.3
    assert summary["active_misconceptions"]["parte_todo"] == 1


def test_resumir_bitacora_sesion_vacia(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setattr(bitacora, "_DEFAULT_BASE_DIR", tmp_path / "session_logs")
    tools = _register_bitacora(fake_mcp)

    resumen = tools["resumir_bitacora_sesion"]("ana_001", "sin_datos")

    assert resumen["summary"]["total_turns"] == 0
    assert "message" in resumen["summary"]
