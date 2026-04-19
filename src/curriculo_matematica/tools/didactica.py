"""Herramientas relacionadas con la experiencia didáctica y vocabulario."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_experiencia_didactica(nodo_id: str) -> dict:
        """
        Devuelve la experiencia didáctica (situación ancla, pregunta de indagación y andamiaje)
        de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_05').
        """
        nodo_id = nodo_id.strip().upper()
        try:
            nodo = get_curriculo_dao().get_node(nodo_id)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if nodo is None:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}
        return {
            "nodo_id": nodo_id,
            "titulo": nodo["titulo"],
            "experiencia_didactica": nodo["experiencia_didactica"],
        }

    @mcp.tool()
    def obtener_vocabulario(nodo_id: str) -> dict:
        """
        Devuelve el vocabulario clave de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_08').
        """
        nodo_id = nodo_id.strip().upper()
        try:
            nodo = get_curriculo_dao().get_node(nodo_id)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if nodo is None:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}
        return {
            "nodo_id": nodo_id,
            "titulo": nodo["titulo"],
            "vocabulario_clave": nodo["vocabulario_clave"],
        }
