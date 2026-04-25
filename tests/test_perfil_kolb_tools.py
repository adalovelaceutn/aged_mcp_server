from __future__ import annotations

from dataclasses import dataclass

from curriculo_matematica.tools import perfil_kolb


@dataclass
class _FakeProfileRow:
    student_id: str
    assessment_name: str
    model_name: str
    status: str
    style: str
    confidence: float
    updated_at: str
    kolb_vector: dict[str, float]
    source: str
    summary: str
    assessment_answers: list[dict]
    scenarios_completed: list[int]

    def to_profile_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "assessment_name": self.assessment_name,
            "model_name": self.model_name,
            "status": self.status,
            "style": self.style,
            "confidence": self.confidence,
            "updated_at": self.updated_at,
            "kolb_vector": self.kolb_vector,
            "source": self.source,
            "summary": self.summary,
            "assessment_answers": self.assessment_answers,
            "scenarios_completed": self.scenarios_completed,
        }


class _FakeStudentProfileDAO:
    def __init__(self) -> None:
        self._rows: dict[str, _FakeProfileRow] = {}

    def get_by_student_id(self, student_id: int):
        row = self._rows.get(str(student_id))
        return row.to_profile_dict() if row else None

    def get_by_alumno_id(self, alumno_id: str):
        return self.get_by_student_id(int(alumno_id))

    def upsert_profile(
        self,
        student_id: int,
        status: str,
        style: str,
        confidence: float,
        kolb_vector: dict[str, float],
        source: str,
        summary: str,
        assessment_answers: list[dict],
        scenarios_completed: list[int],
        assessment_name: str,
        model_name: str,
    ):
        row = _FakeProfileRow(
            student_id=str(student_id),
            assessment_name=assessment_name,
            model_name=model_name,
            status=status,
            style=style,
            confidence=confidence,
            updated_at="2026-01-01T00:00:00Z",
            kolb_vector=kolb_vector,
            source=source,
            summary=summary,
            assessment_answers=assessment_answers,
            scenarios_completed=scenarios_completed,
        )
        self._rows[str(student_id)] = row
        return row.to_profile_dict()


def _register_perfil(fake_mcp):
    perfil_kolb.register(fake_mcp)
    return fake_mcp.tools


def test_obtener_perfil_kolb_inexistente_retorna_error(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["obtener_perfil_kolb"]("123")

    assert result["not_found"] is True
    assert result["student_id"] == "123"
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
        alumno_id="101",
        ae_score=0.6,
        ro_score=0.2,
        ac_score=0.1,
        ce_score=0.1,
        evidencia_texto="Participa mejor en actividades practicas",
        origen="tutor_ai",
    )

    profile = result["profile"]

    assert result["ok"] is True
    assert profile["style"] == "Converging"
    assert abs(sum(profile["kolb_vector"].values()) - 1.0) < 1e-9
    assert len(profile["assessment_answers"]) == 1
    assert profile["assessment_answers"][0]["dimension"] == "RO"


def test_insertar_perfil_kolb_mock_db_student_id_35(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    guardar = tools["actualizar_perfil_kolb"](
        alumno_id="35",
        ae_score=0.2,
        ro_score=0.4,
        ac_score=0.3,
        ce_score=0.1,
        evidencia_texto="Perfil inicial mock para alumno 35",
        origen="test_suite",
    )
    consultar = tools["obtener_perfil_kolb"]("35")

    assert guardar["ok"] is True
    assert "35" in fake_dao._rows
    assert consultar["student_id"] == "35"
    assert consultar["style"] == "Assimilating"
    assert len(consultar["assessment_answers"]) == 1
    assert consultar["source"] == "test_suite"


def test_actualizar_perfil_kolb_score_fuera_de_rango(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="123",
        ae_score=1.5,
        ro_score=0.2,
        ac_score=0.1,
        ce_score=0.1,
    )

    assert "error" in result


def test_actualizar_perfil_kolb_empate_confianza_baja(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    result = tools["actualizar_perfil_kolb"](
        alumno_id="202",
        ae_score=0.4,
        ro_score=0.4,
        ac_score=0.1,
        ce_score=0.1,
    )

    assert result["profile"]["confidence"] == 0.0


def test_persistir_perfil_kolb_desde_payload_agente(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 123,
        "kolb_style": "Converging",
        "confidence": 0.89,
        "answered_scenarios": 9,
        "kolb_profile": {
            "student_id": 123,
            "assessment_name": "Lovelace Everyday Life Profiling",
            "model_name": "Kolb Cycle",
            "current_vector": {
                "AE": 0.42,
                "RO": 0.31,
                "AC": 0.72,
                "CE": 0.55,
            },
            "style": "Converging",
            "confidence": 0.89,
            "answered_scenarios": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "answers": [
                {
                    "scenario_id": 1,
                    "dimension": "AC",
                    "answer": "...",
                }
            ],
            "source": "generated_via_guided_interview",
            "summary": "...",
        },
    }

    result = tools["persistir_perfil_kolb"](payload)

    assert result["ok"] is True
    assert result["profile"]["student_id"] == "123"
    assert result["profile"]["style"] == "Converging"
    assert result["profile"]["confidence"] == 0.89
    assert result["profile"]["source"] == "generated_via_guided_interview"
    assert result["profile"]["assessment_answers"][0]["dimension"] == "AC"
    assert result["profile"]["scenarios_completed"] == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_persistir_perfil_kolb_payload_invalido(monkeypatch, fake_mcp):
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: _FakeStudentProfileDAO())
    tools = _register_perfil(fake_mcp)

    result = tools["persistir_perfil_kolb"]({"student_id": 1})

    assert "error" in result


def test_persistir_perfil_kolb_payload_plano_tipo_kolbprofile(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 123,
        "current_vector": {"AE": 0.42, "RO": 0.31, "AC": 0.72, "CE": 0.55},
        "style": "Converging",
        "confidence": 0.89,
        "answered_scenarios": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "answers": [
            {
                "scenario_id": 1,
                "dimension": "AC",
                "answer": "Mock answer para validacion en Neon",
            }
        ],
        "source": "integration_test_mock",
        "summary": "Resumen mock",
    }

    result = tools["persistir_perfil_kolb"](payload)

    assert result["ok"] is True
    assert result["profile"]["student_id"] == "123"
    assert result["profile"]["source"] == "integration_test_mock"
    assert result["profile"]["scenarios_completed"] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert len(result["profile"]["assessment_answers"]) == 1
    assert result["profile"]["assessment_answers"][0]["answer_text"].startswith("Mock answer")


def test_persistir_perfil_kolb_admite_answer_text(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 456,
        "current_vector": {"AE": 0.4, "RO": 0.2, "AC": 0.3, "CE": 0.1},
        "answers": [
            {
                "scenario_id": 7,
                "dimension": "RO",
                "answer_text": "Respuesta en campo answer_text",
            }
        ],
    }

    result = tools["persistir_perfil_kolb"](payload)

    assert result["ok"] is True
    assert result["profile"]["assessment_answers"][0]["answer_text"] == "Respuesta en campo answer_text"
    assert result["profile"]["scenarios_completed"] == [7]


def test_persistir_perfil_kolb_mock_alumno_35(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 35,
        "current_vector": {"AE": 0.42, "RO": 0.31, "AC": 0.72, "CE": 0.55},
        "style": "Converging",
        "confidence": 0.89,
        "answered_scenarios": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "answers": [
            {
                "scenario_id": 1,
                "dimension": "AC",
                "answer": "Mock answer para alumno 35",
            }
        ],
        "source": "integration_test_mock",
        "summary": "Perfil mock persistido para alumno 35",
    }

    guardar = tools["persistir_perfil_kolb"](payload)
    consultar = tools["obtener_perfil_kolb"]("35")

    assert guardar["ok"] is True
    assert "35" in fake_dao._rows
    assert consultar["student_id"] == "35"
    assert consultar["style"] == "Converging"
    assert consultar["source"] == "integration_test_mock"
    assert consultar["scenarios_completed"] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert consultar["assessment_answers"][0]["answer_text"] == "Mock answer para alumno 35"


def test_persistir_perfil_kolb_payload_agente_con_aliases_de_salida(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 789,
        "source": "integration_agent",
        "kolb_profile": {
            "student_id": 789,
            "assessment_name": "Lovelace Everyday Life Profiling",
            "model_name": "Kolb Cycle",
            "kolb_vector": {
                "ae_score": 0.42,
                "ro_score": 0.31,
                "ac_score": 0.72,
                "ce_score": 0.55,
            },
            "assessment_answers": [
                {
                    "scenario_id": 2,
                    "dimension": "RO",
                    "answer_text": "Respuesta desde alias assessment_answers",
                }
            ],
            "scenarios_completed": [2, 4, 6],
        },
    }

    result = tools["persistir_perfil_kolb"](payload)

    assert result["ok"] is True
    assert result["profile"]["student_id"] == "789"
    assert result["profile"]["source"] == "integration_agent"
    assert result["profile"]["scenarios_completed"] == [2, 4, 6]
    assert result["profile"]["assessment_answers"][0]["answer_text"] == "Respuesta desde alias assessment_answers"


def test_persistir_perfil_kolb_payload_agente_con_typos_y_camelcase(monkeypatch, fake_mcp):
    fake_dao = _FakeStudentProfileDAO()
    monkeypatch.setattr(perfil_kolb, "_dao", lambda: fake_dao)
    tools = _register_perfil(fake_mcp)

    payload = {
        "status": "completed",
        "student_id": 790,
        "source": "integration_agent",
        "kolb_profile": {
            "student_id": 790,
            "current_vector": {
                "AE": 0.42,
                "RO": 0.31,
                "AC": 0.72,
                "CE": 0.55,
            },
            "assesment_answers": [
                {
                    "scenarioId": 3,
                    "dimension": "CE",
                    "answerText": "Respuesta con typo en la clave principal",
                }
            ],
            "scenariosCompleted": "3,5,7",
        },
    }

    result = tools["persistir_perfil_kolb"](payload)

    assert result["ok"] is True
    assert result["profile"]["student_id"] == "790"
    assert result["profile"]["scenarios_completed"] == [3, 5, 7]
    assert len(result["profile"]["assessment_answers"]) == 1
    assert result["profile"]["assessment_answers"][0]["scenario_id"] == 3
    assert result["profile"]["assessment_answers"][0]["answer_text"] == "Respuesta con typo en la clave principal"
