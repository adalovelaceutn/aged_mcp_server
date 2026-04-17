from __future__ import annotations

from curriculo_matematica.models.curriculo import curriculo_data
from curriculo_matematica.resources import curriculo as recurso_curriculo
from curriculo_matematica.tools import consulta, didactica, navegacion


def _register_all_curriculo_tools(fake_mcp):
    consulta.register(fake_mcp)
    didactica.register(fake_mcp)
    navegacion.register(fake_mcp)
    return fake_mcp.tools


def test_listar_nodos_retorna_resumen(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["listar_nodos"]()

    assert len(result) == len(curriculo_data)
    assert "NODO_01" in result
    assert set(result["NODO_01"].keys()) == {"nombre_nivel", "titulo"}


def test_obtener_nodo_valido_normaliza_id(fake_mcp):
    tools = _register_all_curriculo_tools(fake_mcp)

    result = tools["obtener_nodo"](" nodo_03 ")

    assert result["titulo"] == curriculo_data["NODO_03"]["titulo"]
    assert "saberes" in result


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
