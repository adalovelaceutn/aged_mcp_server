"""
Servidor MCP para datos curriculares de matemática.
Expone herramientas para que un agente docente consulte el currículo.
"""

from mcp.server.fastmcp import FastMCP
from curriculo_data import curriculo_data

mcp = FastMCP(
    name="curriculo-matematica",
    instructions=(
        "Servidor de datos curriculares de matemática. "
        "Proporciona información sobre nodos temáticos, capacidades, saberes, "
        "prerrequisitos, actividades y experiencias didácticas."
    ),
)


# ---------------------------------------------------------------------------
# Herramientas
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Recursos
# ---------------------------------------------------------------------------


@mcp.resource("curriculo://nodos")
def recurso_todos_los_nodos() -> str:
    """Recurso que expone el currículo completo como texto estructurado."""
    lineas = ["# Currículo de Matemática\n"]
    for nodo_id, datos in curriculo_data.items():
        lineas.append(f"## {nodo_id} — {datos['titulo']}")
        lineas.append(f"**Nivel:** {datos['nombre_nivel']}")
        lineas.append(f"**Capacidad:** {datos['capacidad']}")
        lineas.append(f"**Prerrequisitos:** {', '.join(datos['prerrequisitos']) or 'Ninguno'}")
        lineas.append(f"**Actividades:** {', '.join(datos['lista_actividades'])}")
        lineas.append("")
    return "\n".join(lineas)


@mcp.resource("curriculo://nodo/{nodo_id}")
def recurso_nodo(nodo_id: str) -> str:
    """Recurso que expone un nodo curricular completo como texto."""
    nodo_id = nodo_id.strip().upper()
    if nodo_id not in curriculo_data:
        return f"Nodo '{nodo_id}' no encontrado."

    datos = curriculo_data[nodo_id]
    ed = datos["experiencia_didactica"]
    saberes = "\n".join(f"  - {s}" for s in datos["saberes"])
    andamiaje = "\n".join(f"  {i+1}. {a}" for i, a in enumerate(ed["andamiaje"]))

    return (
        f"# {nodo_id}: {datos['titulo']}\n\n"
        f"**Nivel:** {datos['nombre_nivel']}\n\n"
        f"**Capacidad:** {datos['capacidad']}\n\n"
        f"## Saberes\n{saberes}\n\n"
        f"## Experiencia Didáctica\n"
        f"**Situación ancla:** {ed['situacion_anclaje']}\n\n"
        f"**Pregunta de indagación:** {ed['pregunta_indagacion']}\n\n"
        f"**Andamiaje:**\n{andamiaje}\n\n"
        f"## Vocabulario clave\n{', '.join(datos['vocabulario_clave'])}\n\n"
        f"**Prerrequisitos:** {', '.join(datos['prerrequisitos']) or 'Ninguno'}\n"
        f"**Actividades:** {', '.join(datos['lista_actividades'])}\n"
    )


if __name__ == "__main__":
    mcp.run()
