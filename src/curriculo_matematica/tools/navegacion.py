"""Herramientas de navegación por la estructura del currículo (prerrequisitos y rutas)."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str


class NodoIdInput(BaseModel):
    nodo_id: str = Field(min_length=1)


class PrerrequisitoOut(BaseModel):
    id: str
    titulo: str
    nombre_nivel: str


class ObtenerPrerrequisitosOut(BaseModel):
    model_config = ConfigDict(extra="allow")

    nodo_id: str
    prerrequisitos: list[PrerrequisitoOut]


class ObtenerActividadesOut(BaseModel):
    nodo_id: str
    titulo: str
    lista_actividades: list[str]


class RutaNodoOut(BaseModel):
    id: str
    titulo: str
    nombre_nivel: str


class RutaAprendizajeOut(BaseModel):
    nodo_destino: str
    ruta_ordenada: list[RutaNodoOut]


def _error_response(message: str, **kwargs) -> dict:
    return ErrorResponse.model_validate({"error": message, **kwargs}).model_dump()


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_prerrequisitos(nodo_id: str) -> dict:
        """
        Devuelve los prerrequisitos de un nodo y la información resumida de cada uno.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_03').
        """
        try:
            payload = NodoIdInput.model_validate({"nodo_id": nodo_id})
            nodo_id = payload.nodo_id.strip().upper()
        except ValidationError as error:
            return _error_response(str(error))

        dao = get_curriculo_dao()
        try:
            nodo = dao.get_node(nodo_id)
        except Exception as error:
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

        if nodo is None:
            return _error_response(f"Nodo '{nodo_id}' no encontrado.")

        prereqs = nodo["prerrequisitos"]
        if not prereqs:
            return ObtenerPrerrequisitosOut.model_validate(
                {
                    "nodo_id": nodo_id,
                    "prerrequisitos": [],
                    "mensaje": "Este nodo no tiene prerrequisitos.",
                }
            ).model_dump()

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

        return ObtenerPrerrequisitosOut.model_validate(
            {
                "nodo_id": nodo_id,
                "prerrequisitos": prereqs_data,
            }
        ).model_dump()

    @mcp.tool()
    def obtener_actividades(nodo_id: str) -> dict:
        """
        Devuelve la lista de actividades asociadas a un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_09').
        """
        try:
            payload = NodoIdInput.model_validate({"nodo_id": nodo_id})
            nodo_id = payload.nodo_id.strip().upper()
        except ValidationError as error:
            return _error_response(str(error))

        try:
            nodo = get_curriculo_dao().get_node(nodo_id)
        except Exception as error:
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

        if nodo is None:
            return _error_response(f"Nodo '{nodo_id}' no encontrado.")
        return ObtenerActividadesOut.model_validate(
            {
                "nodo_id": nodo_id,
                "titulo": nodo["titulo"],
                "lista_actividades": nodo["lista_actividades"],
            }
        ).model_dump()

    @mcp.tool()
    def obtener_ruta_aprendizaje(nodo_id: str) -> dict:
        """
        Calcula la ruta completa de aprendizaje (cadena de prerrequisitos) necesaria
        para llegar a un nodo, ordenada desde el nodo más básico.

        Args:
            nodo_id: Identificador del nodo destino (ej: 'NODO_13').
        """
        try:
            payload = NodoIdInput.model_validate({"nodo_id": nodo_id})
            nodo_id = payload.nodo_id.strip().upper()
        except ValidationError as error:
            return _error_response(str(error))

        dao = get_curriculo_dao()
        try:
            root = dao.get_node(nodo_id)
        except Exception as error:
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

        if root is None:
            return _error_response(f"Nodo '{nodo_id}' no encontrado.")

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

        return RutaAprendizajeOut.model_validate(
            {
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
        ).model_dump()
