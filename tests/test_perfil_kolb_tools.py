from __future__ import annotations

from dataclasses import dataclass

from curriculo_matematica.tools import perfil_kolb


@dataclass
class _FakeProfileRow:
    alumno_id: str
    updated_at: str
    kolb_profile: dict[str, float]
    preferencia_principal: str
    evidencia: list[dict]

    def to_profile_dict(self) -> dict:
        return {
            "alumno_id": self.alumno_id,
            "updated_at": self.updated_at,
            "kolb_profile": self.kolb_profile,
            "preferencia_principal": self.preferencia_principal,
            "evidencia": self.evidencia,
        }


class _FakeStudentProfileDAO:
    def __init__(self) -> None:
        self._rows: dict[str, _FakeProfileRow] = {}

    def get_by_alumno_id(self, alumno_id: str):
        return self._rows.get(alumno_id)

    def upsert_profile(
        self,
        alumno_id: str,
        updated_at,
        kolb_profile: dict[str, float],
        preferencia_principal: str,
        evidencia: list[dict],
    ):
        row = _FakeProfileRow(
            alumno_id=alumno_id,
            updated_at=updated_at.isoformat().replace("+00:00", "Z"),
            kolb_profile=kolb_profile,
            preferencia_principal=preferencia_principal,
            evidencia=evidencia,
        )
        self._rows[alumno_id] = row
        return row


def _register_perfil(fake_mcp):
    perfil_kolb.register(fake_mcp)
    return fake_mcp.tools


def test_obtener_perfil_kolb_inexistente_retorna_error(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["obtener_perfil_kolb"]("luis_navarro_001")

    assert result["not_found"] is True
    assert result["alumno_id"] == "luis_navarro_001"
    assert "error" in result


def test_obtener_perfil_kolb_id_invalido(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["obtener_perfil_kolb"]("luis navarro")

    assert "error" in result


def test_actualizar_perfil_kolb_normaliza_y_agrega_evidencia(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
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


def test_actualizar_perfil_kolb_score_fuera_de_rango(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="luis_navarro_001",
        activo=1.5,
        reflexivo=0.2,
        teorico=0.1,
        pragmatico=0.1,
    )

    assert "error" in result


def test_actualizar_perfil_kolb_empate_preferencia(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="ana_001",
        activo=0.4,
        reflexivo=0.4,
        teorico=0.1,
        pragmatico=0.1,
    )

    assert result["profile"]["preferencia_principal"] == "equilibrado"
