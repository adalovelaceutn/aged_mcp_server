"""Herramientas de consulta general del currículo."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.models.curriculo import curriculo_data


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def listar_nodos() -> dict:
        """Devuelve un listado resumido de todos los nodos del currículo con su título y nivel."""
        return {
            nodo_id: {
                "nombre_nivel": datos["nombre_nivel"],
                "titulo": datos["titulo"],
            }
            for nodo_id, datos in curriculo_data.items()
        }

    @mcp.tool()
    def obtener_nodo(nodo_id: str) -> dict:
        """
        Devuelve la información completa de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_01', 'NODO_07').
        """
        nodo_id = nodo_id.strip().upper()
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado. Use listar_nodos() para ver los disponibles."}
        return curriculo_data[nodo_id]

    @mcp.tool()
    def buscar_por_nivel(nombre_nivel: str) -> dict:
        """
        Devuelve todos los nodos que pertenecen a un nivel específico del currículo.

        Args:
            nombre_nivel: Texto parcial del nivel a buscar (ej: 'NIVEL 3', 'Geometría', 'Algebraica').
        """
        nombre_nivel_lower = nombre_nivel.lower()
        resultado = {
            nodo_id: {
                "nombre_nivel": datos["nombre_nivel"],
                "titulo": datos["titulo"],
                "capacidad": datos["capacidad"],
            }
            for nodo_id, datos in curriculo_data.items()
            if nombre_nivel_lower in datos["nombre_nivel"].lower()
            or nombre_nivel_lower in datos["titulo"].lower()
        }

        if not resultado:
            return {"error": f"No se encontraron nodos para el nivel '{nombre_nivel}'."}
        return resultado
