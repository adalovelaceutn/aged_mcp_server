"""Herramientas relacionadas con la experiencia didáctica y vocabulario."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from curriculo_matematica.dao.curriculo_gateway import get_curriculo_dao


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str


class NodoIdInput(BaseModel):
    nodo_id: str = Field(min_length=1)


class ExperienciaDidacticaOut(BaseModel):
    nodo_id: str
    titulo: str
    experiencia_didactica: dict


class VocabularioOut(BaseModel):
    nodo_id: str
    titulo: str
    vocabulario_clave: list[str]


def _error_response(message: str, **kwargs) -> dict:
    return ErrorResponse.model_validate({"error": message, **kwargs}).model_dump()


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def obtener_experiencia_didactica(nodo_id: str) -> dict:
        """
        Devuelve la experiencia didáctica (situación ancla, pregunta de indagación y andamiaje)
        de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_05').
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
        return ExperienciaDidacticaOut.model_validate(
            {
                "nodo_id": nodo_id,
                "titulo": nodo["titulo"],
                "experiencia_didactica": nodo["experiencia_didactica"],
            }
        ).model_dump()

    @mcp.tool()
    def obtener_vocabulario(nodo_id: str) -> dict:
        """
        Devuelve el vocabulario clave de un nodo curricular.

        Args:
            nodo_id: Identificador del nodo (ej: 'NODO_08').
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
        return VocabularioOut.model_validate(
            {
                "nodo_id": nodo_id,
                "titulo": nodo["titulo"],
                "vocabulario_clave": nodo["vocabulario_clave"],
            }
        ).model_dump()
