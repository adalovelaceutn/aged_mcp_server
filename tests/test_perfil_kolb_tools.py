from __future__ import annotations

from curriculo_matematica.tools import perfil_kolb


def _register_perfil(fake_mcp):
    perfil_kolb.register(fake_mcp)
    return fake_mcp.tools


def test_obtener_perfil_kolb_inexistente_retorna_error(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setenv("KOLB_STORAGE_BACKEND", "json")
    monkeypatch.setattr(perfil_kolb, "_PROFILE_BASE_DIR", tmp_path / "student_profiles")
    tools = _register_perfil(fake_mcp)

    result = tools["obtener_perfil_kolb"]("luis_navarro_001")

    assert result["not_found"] is True
    assert result["alumno_id"] == "luis_navarro_001"
    assert "error" in result
    assert not (tmp_path / "student_profiles" / "luis_navarro_001.json").exists()


def test_obtener_perfil_kolb_id_invalido(fake_mcp):
    tools = _register_perfil(fake_mcp)

    result = tools["obtener_perfil_kolb"]("luis navarro")

    assert "error" in result


def test_actualizar_perfil_kolb_normaliza_y_agrega_evidencia(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setenv("KOLB_STORAGE_BACKEND", "json")
    monkeypatch.setattr(perfil_kolb, "_PROFILE_BASE_DIR", tmp_path / "student_profiles")
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="luis_navarro_001",
        activo=0.6,
        reflexivo=0.2,
        teorico=0.1,
        pragmatico=0.1,
        evidencia_texto="Participa mejor en actividades practicas",
        origen="tutor_ai",
    )

    profile = result["profile"]

    assert result["ok"] is True
    assert profile["preferencia_principal"] == "activo"
    assert abs(sum(profile["kolb_profile"].values()) - 1.0) < 1e-9
    assert len(profile["evidencia"]) == 1
    assert profile["evidencia"][0]["origen"] == "tutor_ai"


def test_actualizar_perfil_kolb_score_fuera_de_rango(fake_mcp):
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="luis_navarro_001",
        activo=1.5,
        reflexivo=0.2,
        teorico=0.1,
        pragmatico=0.1,
    )

    assert "error" in result


def test_actualizar_perfil_kolb_empate_preferencia(tmp_path, monkeypatch, fake_mcp):
    monkeypatch.setenv("KOLB_STORAGE_BACKEND", "json")
    monkeypatch.setattr(perfil_kolb, "_PROFILE_BASE_DIR", tmp_path / "student_profiles")
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="ana_001",
        activo=0.4,
        reflexivo=0.4,
        teorico=0.1,
        pragmatico=0.1,
    )

    assert result["profile"]["preferencia_principal"] == "equilibrado"
