"""Herramientas relacionadas con la experiencia didáctica y vocabulario."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.data.curriculo import curriculo_data


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
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        nodo = curriculo_data[nodo_id]
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
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        nodo = curriculo_data[nodo_id]
        return {
            "nodo_id": nodo_id,
            "titulo": nodo["titulo"],
            "vocabulario_clave": nodo["vocabulario_clave"],
        }
