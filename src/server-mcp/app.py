"""
Punto de entrada del servidor MCP de currículo de matemática.
Registra todas las herramientas y recursos en la instancia FastMCP.
"""

import os

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.tools import bitacora, consulta, didactica, navegacion, perfil_kolb
from curriculo_matematica.resources import curriculo as recurso_curriculo

mcp = FastMCP(
    name="curriculo-matematica",
    instructions=(
        "Servidor de datos curriculares de matemática. "
        "Proporciona información sobre nodos temáticos, capacidades, saberes, "
        "prerrequisitos, actividades y experiencias didácticas. "
        "Además, permite registrar, consultar y resumir bitácoras de sesión por alumno, "
        "y obtener/actualizar el perfil de aprendizaje Kolb con evidencia pedagógica "
        "para personalizar el acompañamiento."
    ),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", "8000")),
    sse_path=os.getenv("MCP_SSE_PATH", "/sse"),
)

# Registro de módulos
consulta.register(mcp)
didactica.register(mcp)
navegacion.register(mcp)
bitacora.register(mcp)
perfil_kolb.register(mcp)
recurso_curriculo.register(mcp)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    if transport not in {"stdio", "sse", "streamable-http"}:
        raise ValueError(
            "MCP_TRANSPORT invalido. Use 'stdio', 'sse' o 'streamable-http'."
        )
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
