"""
Punto de entrada del servidor MCP de currículo de matemática.
Registra todas las herramientas y recursos en la instancia FastMCP.
"""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.tools import consulta, didactica, navegacion
from curriculo_matematica.resources import curriculo as recurso_curriculo

mcp = FastMCP(
    name="curriculo-matematica",
    instructions=(
        "Servidor de datos curriculares de matemática. "
        "Proporciona información sobre nodos temáticos, capacidades, saberes, "
        "prerrequisitos, actividades y experiencias didácticas."
    ),
)

# Registro de módulos
consulta.register(mcp)
didactica.register(mcp)
navegacion.register(mcp)
recurso_curriculo.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
