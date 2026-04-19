"""Herramientas de navegación por la estructura del currículo (prerrequisitos y rutas)."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_prerrequisitos(nodo_id: str) -> dict:
        """
        Devuelve los prerrequisitos de un nodo y la información resumida de cada uno.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_03').
        """
        nodo_id = nodo_id.strip().upper()
        dao = get_curriculo_dao()
        try:
            nodo = dao.get_node(nodo_id)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if nodo is None:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        prereqs = nodo["prerrequisitos"]
        if not prereqs:
            return {"nodo_id": nodo_id, "prerrequisitos": [], "mensaje": "Este nodo no tiene prerrequisitos."}

        prereqs_data: list[dict] = []
        for pid in prereqs:
            pnode = dao.get_node(pid)
            if pnode is not None:
                prereqs_data.append(
                    {
                        "id": pid,
                        "titulo": pnode["titulo"],
                        "nombre_nivel": pnode["nombre_nivel"],
                    }
                )

        return {
            "nodo_id": nodo_id,
            "prerrequisitos": prereqs_data,
        }

    @mcp.tool()
    def obtener_actividades(nodo_id: str) -> dict:
        """
        Devuelve la lista de actividades asociadas a un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_09').
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
            "lista_actividades": nodo["lista_actividades"],
        }

    @mcp.tool()
    def obtener_ruta_aprendizaje(nodo_id: str) -> dict:
        """
        Calcula la ruta completa de aprendizaje (cadena de prerrequisitos) necesaria
        para llegar a un nodo, ordenada desde el nodo más básico.

        Args:
            nodo_id: Identificador del nodo destino (ej: 'NODO_13').
        """
        nodo_id = nodo_id.strip().upper()
        dao = get_curriculo_dao()
        try:
            root = dao.get_node(nodo_id)
        except Exception as error:
            return {"error": f"No se pudo consultar el currículo en DB: {error}"}

        if root is None:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        visitados: list[str] = []

        def _resolver(nid: str) -> None:
            if nid in visitados:
                return
            node = dao.get_node(nid)
            if node is None:
                return
            for prereq in node.get("prerrequisitos", []):
                _resolver(prereq)
            if nid not in visitados:
                visitados.append(nid)

        _resolver(nodo_id)

        nodos_cache = {nid: dao.get_node(nid) for nid in visitados}

        return {
            "nodo_destino": nodo_id,
            "ruta_ordenada": [
                {
                    "id": nid,
                    "titulo": nodos_cache[nid]["titulo"],
                    "nombre_nivel": nodos_cache[nid]["nombre_nivel"],
                }
                for nid in visitados
                if nodos_cache[nid] is not None
            ],
        }
