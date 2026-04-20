from __future__ import annotations

import pytest

from curriculo_matematica.resources import curriculo as recurso_curriculo
from curriculo_matematica.tools import consulta, didactica, navegacion


CURRICULO_FAKE = {
    "NODO_01": {
        "nombre_nivel": "NIVEL 1",
        "titulo": "Sistema Decimal",
        "capacidad": "Capacidad N1",
        "saberes": ["S1"],
        "prerrequisitos": [],
        "lista_actividades": ["ACT_01"],
        "experiencia_didactica": {
            "situacion_anclaje": "A1",
            "pregunta_indagacion": "P1",
            "andamiaje": ["AN1"],
        },
        "vocabulario_clave": ["V1"],
    },
    "NODO_02": {
        "nombre_nivel": "NIVEL 2",
        "titulo": "Enteros",
        "capacidad": "Capacidad N2",
        "saberes": ["S2"],
        "prerrequisitos": ["NODO_01"],
        "lista_actividades": ["ACT_02"],
        "experiencia_didactica": {
            "situacion_anclaje": "A2",
            "pregunta_indagacion": "P2",
            "andamiaje": ["AN2"],
        },
        "vocabulario_clave": ["V2"],
    },
    "NODO_03": {
        "nombre_nivel": "NIVEL 2",
        "titulo": "Racionales",
        "capacidad": "Capacidad N3",
        "saberes": ["S3"],
        "prerrequisitos": ["NODO_02"],
        "lista_actividades": ["ACT_03"],
        "experiencia_didactica": {
            "situacion_anclaje": "A3",
            "pregunta_indagacion": "P3",
            "andamiaje": ["AN3"],
        },
        "vocabulario_clave": ["V3"],
    },
    "NODO_05": {
        "nombre_nivel": "NIVEL 3",
        "titulo": "Porcentaje",
        "capacidad": "Capacidad N5",
        "saberes": ["S5"],
        "prerrequisitos": ["NODO_03"],
        "lista_actividades": ["ACT_05"],
        "experiencia_didactica": {
            "situacion_anclaje": "A5",
            "pregunta_indagacion": "P5",
            "andamiaje": ["AN5"],
        },
        "vocabulario_clave": ["V5"],
    },
    "NODO_08": {
        "nombre_nivel": "NIVEL 4",
        "titulo": "Funciones Afines",
        "capacidad": "Capacidad N8",
        "saberes": ["S8"],
        "prerrequisitos": ["NODO_02"],
        "lista_actividades": ["ACT_08"],
        "experiencia_didactica": {
            "situacion_anclaje": "A8",
            "pregunta_indagacion": "P8",
            "andamiaje": ["AN8"],
        },
        "vocabulario_clave": ["V8"],
    },
    "NODO_09": {
        "nombre_nivel": "NIVEL 4",
        "titulo": "Función Cuadrática",
        "capacidad": "Capacidad N9",
        "saberes": ["S9"],
        "prerrequisitos": ["NODO_08"],
        "lista_actividades": ["ACT_C2_13", "ACT_C2_14"],
        "experiencia_didactica": {
            "situacion_anclaje": "A9",
            "pregunta_indagacion": "P9",
            "andamiaje": ["AN9"],
        },
        "vocabulario_clave": ["V9"],
    },
    "NODO_11": {
        "nombre_nivel": "NIVEL 5",
        "titulo": "Semejanza",
        "capacidad": "Capacidad N11",
        "saberes": ["S11"],
        "prerrequisitos": ["NODO_10"],
        "lista_actividades": ["ACT_11"],
        "experiencia_didactica": {
            "situacion_anclaje": "A11",
            "pregunta_indagacion": "P11",
            "andamiaje": ["AN11"],
        },
        "vocabulario_clave": ["V11"],
    },
    "NODO_10": {
        "nombre_nivel": "NIVEL 4",
        "titulo": "Ecuaciones",
        "capacidad": "Capacidad N10",
        "saberes": ["S10"],
        "prerrequisitos": ["NODO_08"],
        "lista_actividades": ["ACT_10"],
        "experiencia_didactica": {
            "situacion_anclaje": "A10",
            "pregunta_indagacion": "P10",
            "andamiaje": ["AN10"],
        },
        "vocabulario_clave": ["V10"],
    },
    "NODO_13": {
        "nombre_nivel": "NIVEL 5",
        "titulo": "Trigonometría",
        "capacidad": "Capacidad N13",
        "saberes": ["S13"],
        "prerrequisitos": ["NODO_11"],
        "lista_actividades": ["ACT_13"],
        "experiencia_didactica": {
            "situacion_anclaje": "A13",
            "pregunta_indagacion": "P13",
            "andamiaje": ["AN13"],
        },
        "vocabulario_clave": ["V13"],
    },
}


class _FakeCurriculoDAO:
    def __init__(self) -> None:
        self._data = dict(CURRICULO_FAKE)

    def list_nodes_summary(self) -> dict[str, dict]:
        return {
            nodo_id: {
                "nombre_nivel": datos["nombre_nivel"],
                "titulo": datos["titulo"],
            }
            for nodo_id, datos in self._data.items()
        }

    def get_node(self, nodo_id: str) -> dict | None:
        return self._data.get(nodo_id)

    def search_nodes_by_level(self, text: str) -> dict[str, dict]:
        q = text.lower()
        return {
            nodo_id: {
                "nombre_nivel": datos["nombre_nivel"],
                "titulo": datos["titulo"],
                "capacidad": datos["capacidad"],
            }
            for nodo_id, datos in self._data.items()
            if q in datos["nombre_nivel"].lower() or q in datos["titulo"].lower()
        }

    def upsert_from_dict(self, curriculo_data: dict[str, dict]) -> dict:
        self._data = dict(curriculo_data)
        return {"ok": True, "nodes_synced": len(curriculo_data)}

    def count_nodes(self) -> int:
        return len(self._data)

    def export_as_dict(self) -> dict[str, dict]:
        return dict(self._data)


@pytest.fixture(autouse=True)
def _mock_curriculo_dao(monkeypatch):
    fake = _FakeCurriculoDAO()
    monkeypatch.setattr(consulta, "get_curriculo_dao", lambda: fake)
    monkeypatch.setattr(didactica, "get_curriculo_dao", lambda: fake)
    monkeypatch.setattr(navegacion, "get_curriculo_dao", lambda: fake)
    monkeypatch.setattr(recurso_curriculo, "get_curriculo_dao", lambda: fake)


def _register_all_curriculo_tools(fake_mcp):
    consulta.register(fake_mcp)
    didactica.register(fake_mcp)
    navegacion.register(fake_mcp)
    return fake_mcp.tools


def test_listar_nodos_retorna_resumen(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["listar_nodos"]()

    assert len(result) == len(CURRICULO_FAKE)
    assert "NODO_01" in result
    assert set(result["NODO_01"].keys()) == {"nombre_nivel", "titulo"}


def test_obtener_nodo_valido_normaliza_id(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_nodo"](" nodo_03 ")

    assert result["titulo"] == CURRICULO_FAKE["NODO_03"]["titulo"]
    assert "saberes" in result
    assert "nodos_requeridos" in result
    assert result["nodos_requeridos"] == CURRICULO_FAKE["NODO_03"]["prerrequisitos"]


def test_resincronizar_curriculo_db_ok(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    payload = {
        "NODO_X": {
            "nombre_nivel": "NIVEL X",
            "titulo": "Nuevo Nodo",
            "capacidad": "Capacidad X",
            "saberes": ["SX"],
            "prerrequisitos": [],
            "lista_actividades": ["ACT_X"],
            "experiencia_didactica": {
                "situacion_anclaje": "AX",
                "pregunta_indagacion": "PX",
                "andamiaje": ["ANX"],
            },
            "vocabulario_clave": ["VX"],
        }
    }

    result = tools["resincronizar_curriculo_db"](payload)
    listado = tools["listar_nodos"]()

    assert result["ok"] is True
    assert result["result"]["nodes_synced"] == 1
    assert result["total_nodes_in_db"] == 1
    assert "NODO_X" in listado


def test_exportar_curriculo_db_ok(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["exportar_curriculo_db"]()

    assert result["ok"] is True
    assert result["total_nodes"] == len(CURRICULO_FAKE)
    assert "NODO_01" in result["curriculo_data"]
    assert "saberes" in result["curriculo_data"]["NODO_01"]
    assert "nodos_requeridos" in result["curriculo_data"]["NODO_01"]


def test_obtener_nodo_invalido(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_nodo"]("NODO_X")

    assert "error" in result
    assert "no encontrado" in result["error"].lower()


def test_buscar_por_nivel_por_texto_de_titulo(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["buscar_por_nivel"]("NIVEL 5")

    assert "NODO_13" in result


def test_buscar_por_nivel_sin_resultados(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["buscar_por_nivel"]("nivel inexistente")

    assert "error" in result


def test_obtener_experiencia_didactica_ok(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_experiencia_didactica"]("NODO_05")

    assert result["nodo_id"] == "NODO_05"
    assert "experiencia_didactica" in result
    assert "pregunta_indagacion" in result["experiencia_didactica"]


def test_obtener_vocabulario_invalido(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_vocabulario"]("invalido")

    assert "error" in result


def test_obtener_prerrequisitos_con_y_sin_prerreqs(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    sin_prerreqs = tools["obtener_prerrequisitos"]("NODO_01")
    con_prerreqs = tools["obtener_prerrequisitos"]("NODO_03")

    assert sin_prerreqs["prerrequisitos"] == []
    assert "mensaje" in sin_prerreqs
    assert len(con_prerreqs["prerrequisitos"]) >= 1
    assert con_prerreqs["prerrequisitos"][0]["id"] == "NODO_02"


def test_obtener_actividades_ok(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_actividades"]("NODO_09")

    assert result["nodo_id"] == "NODO_09"
    assert isinstance(result["lista_actividades"], list)
    assert len(result["lista_actividades"]) > 0


def test_obtener_ruta_aprendizaje_ordenada(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_ruta_aprendizaje"]("NODO_13")
    ruta_ids = [item["id"] for item in result["ruta_ordenada"]]

    assert ruta_ids[-1] == "NODO_13"
    assert "NODO_11" in ruta_ids


def test_obtener_ruta_aprendizaje_invalido(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_ruta_aprendizaje"]("NODO_99")

    assert "error" in result


def test_recurso_todos_los_nodos(fake_mcp):
    recurso_curriculo.register(fake_mcp)

    result = fake_mcp.resources["curriculo://nodos"]()

    assert "# Currículo de Matemática" in result
    assert "## NODO_01" in result


def test_recurso_nodo_ok_e_invalido(fake_mcp):
    recurso_curriculo.register(fake_mcp)
    recurso = fake_mcp.resources["curriculo://nodo/{nodo_id}"]

    ok = recurso("nodo_08")
    invalido = recurso("nodo_999")

    assert ok.startswith("# NODO_08")
    assert "Vocabulario clave" in ok
    assert "no encontrado" in invalido.lower()
