"""Herramientas de navegación por la estructura del currículo (prerrequisitos y rutas)."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.data.curriculo import curriculo_data


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_prerrequisitos(nodo_id: str) -> dict:
        """
        Devuelve los prerrequisitos de un nodo y la información resumida de cada uno.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_03').
        """
        nodo_id = nodo_id.strip().upper()
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        prereqs = curriculo_data[nodo_id]["prerrequisitos"]
        if not prereqs:
            return {"nodo_id": nodo_id, "prerrequisitos": [], "mensaje": "Este nodo no tiene prerrequisitos."}

        return {
            "nodo_id": nodo_id,
            "prerrequisitos": [
                {
                    "id": pid,
                    "titulo": curriculo_data[pid]["titulo"],
                    "nombre_nivel": curriculo_data[pid]["nombre_nivel"],
                }
                for pid in prereqs
                if pid in curriculo_data
            ],
        }

    @mcp.tool()
    def obtener_actividades(nodo_id: str) -> dict:
        """
        Devuelve la lista de actividades asociadas a un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_09').
        """
        nodo_id = nodo_id.strip().upper()
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        nodo = curriculo_data[nodo_id]
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
        if nodo_id not in curriculo_data:
            return {"error": f"Nodo '{nodo_id}' no encontrado."}

        visitados: list[str] = []

        def _resolver(nid: str) -> None:
            if nid in visitados:
                return
            for prereq in curriculo_data.get(nid, {}).get("prerrequisitos", []):
                _resolver(prereq)
            if nid not in visitados:
                visitados.append(nid)

        _resolver(nodo_id)

        return {
            "nodo_destino": nodo_id,
            "ruta_ordenada": [
                {
                    "id": nid,
                    "titulo": curriculo_data[nid]["titulo"],
                    "nombre_nivel": curriculo_data[nid]["nombre_nivel"],
                }
                for nid in visitados
            ],
        }
