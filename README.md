# Servidor MCP — Currículo de Matemática

Servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) que expone datos curriculares de matemática para ser consumidos por un agente docente.

## Estructura del proyecto

```
aged_mcp_server/
├── server.py                   # Servidor MCP principal (compatibilidad)
├── src/server_mcp/
│   ├── app.py                  # Punto de entrada principal del paquete
│   ├── models/
│   │   └── curriculo.py        # Modelo de datos curriculares
│   ├── schemas/
│   │   ├── bitacora.py         # Esquemas para registros de sesion
│   │   └── perfil_kolb.py      # Esquemas para perfil de aprendizaje
│   ├── tools/                  # Herramientas MCP
│   └── resources/              # Recursos MCP
├── mcp_config.json             # Configuración para cliente MCP
└── pyproject.toml              # Metadatos del proyecto
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
| `registrar_bitacora_sesion` | Registra un turno de sesion con contexto pedagogico |
| `obtener_bitacora_sesion` | Consulta la bitacora de una sesion por alumno |
| `resumir_bitacora_sesion` | Resume progreso, andamiaje y frustracion de la sesion |
| `obtener_perfil_kolb` | Obtiene o inicializa el perfil Kolb de un alumno |
| `actualizar_perfil_kolb` | Actualiza el perfil Kolb y agrega evidencia pedagogica |

## Perfil Kolb del alumno

El servidor guarda el perfil de cada alumno en la tabla PostgreSQL `student_profile` (Neon).

Variables de entorno relevantes:

- `KOLB_STORAGE_BACKEND`: `postgres` (default) o `json`
- `NEON_DATABASE_URL`: cadena de conexión PostgreSQL para Neon

Si `KOLB_STORAGE_BACKEND=json`, se usa almacenamiento local en `student_profiles/{alumno_id}.json`.

Estructura base:

```json
{
	"alumno_id": "luis_navarro_001",
	"updated_at": "2026-04-17T18:10:00Z",
	"kolb_profile": {
		"activo": 0.35,
		"reflexivo": 0.25,
		"teorico": 0.20,
		"pragmatico": 0.20
	},
	"preferencia_principal": "activo",
	"evidencia": [
		{
			"timestamp": "2026-04-17T18:10:00Z",
			"origen": "docente",
			"texto": "Participa mejor con ejercicios de exploracion guiada"
		}
	]
}
```

## Bitacora de sesion

El servidor guarda registros en `session_logs/{alumno_id}/{sesion_id}.jsonl`, una linea JSON por turno.

Estructura registrada:

```json
{
	"alumno_id": "luis_navarro_001",
	"sesion_id": "math_2026_04_17",
	"data": {
		"turn_index": 5,
		"timestamp": "2026-04-17T17:34:00Z",
		"actor": "Lovelace_Tutor",
		"payload": {
			"text": "Que pasaria si dividimos esa pizza en 8 partes...?",
			"media_ref": "v123_video_particion.mp4"
		},
		"pedagogical_context": {
			"target_concept": "fracciones_equivalentes",
			"kolb_strategy": "activo_experimental",
			"scaffolding_level": 2,
			"detected_frustration": 0.1,
			"active_misconception": "none"
		}
	}
}
```

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
