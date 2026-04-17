# Servidor MCP — Currículo de Matemática

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) que expone datos curriculares de matemática para ser consumidos por un agente docente.

## Estructura del proyecto

```
aged_mcp_server/
├── server.py          # Servidor MCP principal
├── curriculo_data.py  # Datos curriculares (14 nodos)
├── mcp_config.json    # Configuración para cliente MCP
└── pyproject.toml     # Metadatos del proyecto
```

## Instalación

```bash
pip install "mcp[cli]>=1.6.0"
```

## Ejecución

### Modo stdio (para integración con agentes)
```bash
python server.py
```

### Modo de desarrollo (inspector MCP)
```bash
mcp dev server.py
```

## Herramientas disponibles

| Herramienta | Descripción |
|---|---|
| `listar_nodos` | Listado resumido de todos los nodos del currículo |
| `obtener_nodo` | Información completa de un nodo por su ID |
| `obtener_prerrequisitos` | Prerrequisitos de un nodo con su información resumida |
| `obtener_experiencia_didactica` | Situación ancla, pregunta de indagación y andamiaje |
| `obtener_vocabulario` | Vocabulario clave de un nodo |
| `obtener_actividades` | Lista de actividades asociadas a un nodo |
| `buscar_por_nivel` | Nodos que pertenecen a un nivel curricular |
| `obtener_ruta_aprendizaje` | Cadena completa de prerrequisitos hacia un nodo |

## Recursos disponibles

| URI | Descripción |
|---|---|
| `curriculo://nodos` | Currículo completo en formato texto |
| `curriculo://nodo/{nodo_id}` | Nodo específico en formato texto |

## Nodos curriculares

| ID | Título | Nivel |
|---|---|---|
| NODO_01 | Sistema de Numeración Decimal | Nivel 1 |
| NODO_02 | Conjuntos Numéricos: N y Z | Nivel 2 |
| NODO_03 | Números Racionales y Fracciones | Nivel 2 |
| NODO_04 | Operaciones en el Conjunto Q | Nivel 2 |
| NODO_05 | Expresiones Decimales y Porcentaje | Nivel 3 |
| NODO_06 | Razones y Proporciones | Nivel 3 |
| NODO_07 | Sistema de Referencia y Concepto de Función | Nivel 4 |
| NODO_08 | Funciones Lineales y Afines | Nivel 4 |
| NODO_09 | Función Cuadrática | Nivel 4 |
| NODO_10 | Ecuaciones e Inecuaciones | Nivel 4 |
| NODO_11 | Geometría: Semejanza y Triángulos | Nivel 5 |
| NODO_12 | Perímetro y Área | Nivel 5 |
| NODO_13 | Trigonometría | Nivel 5 |
| NODO_14 | Estadística y Probabilidad | Nivel 6 |

## Configuración con Claude Desktop

Agrega el contenido de `mcp_config.json` a tu archivo de configuración de Claude Desktop (`claude_desktop_config.json`).