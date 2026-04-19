"""Herramientas de consulta general del currículo."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def exportar_curriculo_db() -> dict:
        """Exporta el curriculo completo desde DB en formato compatible con resincronizar_curriculo_db."""
        try:
            curriculo_data = get_curriculo_dao().export_as_dict()
        except Exception as error:
            return {"error": f"No se pudo exportar el currículo desde DB: {error}"}

        return {
            "ok": True,
            "message": "Currículo exportado desde DB externa.",
            "total_nodes": len(curriculo_data),
            "curriculo_data": curriculo_data,
        }

    @mcp.tool()
    def resincronizar_curriculo_db(curriculo_data: dict[str, dict]) -> dict:
        """Resincroniza el curriculo completo en la DB externa usando upsert por nodo.

        Args:
            curriculo_data: Estructura de nodos curriculares con el mismo formato que usa la API.
        """
        if not isinstance(curriculo_data, dict) or not curriculo_data:
            return {"error": "'curriculo_data' debe ser un diccionario no vacío de nodos."}

        try:
            resultado = get_curriculo_dao().upsert_from_dict(curriculo_data)
            total = get_curriculo_dao().count_nodes()
        except Exception as error:
            return {"error": f"No se pudo resincronizar el currículo en DB: {error}"}

        return {
            "ok": True,
            "message": "Currículo resincronizado en DB externa.",
            "result": resultado,
            "total_nodes_in_db": total,
        }

    @mcp.tool()
    def listar_nodos() -> dict:
        """Devuelve un listado resumido de todos los nodos del currículo con su título y nivel."""
        try:
            return get_curriculo_dao().list_nodes_summary()
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

    @mcp.tool()
    def obtener_nodo(nodo_id: str) -> dict:
        """
        Devuelve la información completa de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_01', 'NODO_07').
        """
        nodo_id = nodo_id.strip().upper()
        try:
            nodo = get_curriculo_dao().get_node(nodo_id)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if nodo is None:
            return {"error": f"Nodo '{nodo_id}' no encontrado. Use listar_nodos() para ver los disponibles."}
        return nodo

    @mcp.tool()
    def buscar_por_nivel(nombre_nivel: str) -> dict:
        """
        Devuelve todos los nodos que pertenecen a un nivel específico del currículo.

        Args:
            nombre_nivel: Texto parcial del nivel a buscar (ej: 'NIVEL 3', 'Geometría', 'Algebraica').
        """
        try:
            resultado = get_curriculo_dao().search_nodes_by_level(nombre_nivel)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if not resultado:
            return {"error": f"No se encontraron nodos para el nivel '{nombre_nivel}'."}
        return resultado
