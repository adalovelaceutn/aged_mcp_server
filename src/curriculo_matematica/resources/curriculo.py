"""Recursos MCP del currículo de matemática."""

from mcp.server.fastmcp import FastMCP

from curriculo_matematica.models.curriculo import curriculo_data


def register(mcp: FastMCP) -> None:

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
