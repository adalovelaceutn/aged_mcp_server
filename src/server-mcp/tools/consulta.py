"""Herramientas de consulta general del currículo."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str


class NodoExperienciaDidactica(BaseModel):
    situacion_anclaje: str
    pregunta_indagacion: str
    andamiaje: list[str]


class NodoCurriculo(BaseModel):
    nombre_nivel: str
    titulo: str
    capacidad: str
    saberes: list[str] = []
    prerrequisitos: list[str] = []
    nodos_requeridos: list[str] = []
    lista_actividades: list[str]
    experiencia_didactica: NodoExperienciaDidactica
    vocabulario_clave: list[str]


class ListarNodosOut(RootModel[dict[str, dict[str, str]]]):
    pass


class ExportarCurriculoOut(BaseModel):
    ok: bool
    message: str
    total_nodes: int
    nodos: list[NodoCurriculo]


class ResincronizarCurriculoIn(BaseModel):
    curriculo_data: dict[str, dict]


class ResincronizarCurriculoOut(BaseModel):
    ok: bool
    message: str
    result: dict
    total_nodes_in_db: int


class BuscarPorNivelIn(BaseModel):
    nombre_nivel: str = Field(min_length=1)


def _error_response(message: str, **kwargs) -> dict:
    return ErrorResponse.model_validate({"error": message, **kwargs}).model_dump()


def _normalizar_nodo_curriculo(nodo: dict) -> dict:
    """Garantiza claves esperadas por clientes sin romper compatibilidad."""
    normalizado = dict(nodo)
    normalizado.setdefault("saberes", [])

    nodos_requeridos = normalizado.get("nodos_requeridos")
    if nodos_requeridos is None:
        nodos_requeridos = normalizado.get("prerrequisitos", [])

    normalizado["nodos_requeridos"] = list(nodos_requeridos)
    normalizado["prerrequisitos"] = list(normalizado.get("prerrequisitos", nodos_requeridos))
    return normalizado


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def exportar_curriculo_db() -> dict:
        """Exporta el curriculo completo desde DB como lista de nodos."""
        try:
            curriculo_data = get_curriculo_dao().export_as_dict()
        except Exception as error:
            return _error_response(f"No se pudo exportar el currículo desde DB: {error}")

        nodos = [_normalizar_nodo_curriculo(datos) for _, datos in sorted(curriculo_data.items())]

        return ExportarCurriculoOut.model_validate(
            {
                "ok": True,
                "message": "Currículo exportado desde DB externa.",
                "total_nodes": len(nodos),
                "nodos": nodos,
            }
        ).model_dump()

    @mcp.tool()
    def resincronizar_curriculo_db(curriculo_data: dict[str, dict]) -> dict:
        """Resincroniza el curriculo completo en la DB externa usando upsert por nodo.

        Args:
            curriculo_data: Estructura de nodos curriculares con el mismo formato que usa la API.
        """
        try:
            payload = ResincronizarCurriculoIn.model_validate(
                {"curriculo_data": curriculo_data}
            )
            curriculo_data = payload.curriculo_data
        except ValidationError as error:
            return _error_response(str(error))

        if not curriculo_data:
            return _error_response("'curriculo_data' debe ser un diccionario no vacío de nodos.")

        curriculo_data_normalizado = {
            nodo_id: _normalizar_nodo_curriculo(datos)
            for nodo_id, datos in curriculo_data.items()
        }

        try:
            resultado = get_curriculo_dao().upsert_from_dict(curriculo_data_normalizado)
            total = get_curriculo_dao().count_nodes()
        except Exception as error:
            return _error_response(f"No se pudo resincronizar el currículo en DB: {error}")

        return ResincronizarCurriculoOut.model_validate(
            {
                "ok": True,
                "message": "Currículo resincronizado en DB externa.",
                "result": resultado,
                "total_nodes_in_db": total,
            }
        ).model_dump()

    @mcp.tool()
    def listar_nodos() -> dict:
        """Devuelve un listado resumido de todos los nodos del currículo con su título y nivel."""
        try:
            data = get_curriculo_dao().list_nodes_summary()
            return ListarNodosOut.model_validate(data).model_dump()
        except Exception as error:
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

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
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

        if nodo is None:
            return _error_response(
                f"Nodo '{nodo_id}' no encontrado. Use listar_nodos() para ver los disponibles."
            )
        return NodoCurriculo.model_validate(_normalizar_nodo_curriculo(nodo)).model_dump()

    @mcp.tool()
    def buscar_por_nivel(nombre_nivel: str) -> dict:
        """
        Devuelve todos los nodos que pertenecen a un nivel específico del currículo.

        Args:
            nombre_nivel: Texto parcial del nivel a buscar (ej: 'NIVEL 3', 'Geometría', 'Algebraica').
        """
        try:
            payload = BuscarPorNivelIn.model_validate({"nombre_nivel": nombre_nivel})
            nombre_nivel = payload.nombre_nivel
        except ValidationError as error:
            return _error_response(str(error))

        try:
            resultado = get_curriculo_dao().search_nodes_by_level(nombre_nivel)
        except Exception as error:
            return _error_response(f"No se pudo consultar el currículo en DB: {error}")

        if not resultado:
            return _error_response(f"No se encontraron nodos para el nivel '{nombre_nivel}'.")
        return resultado
