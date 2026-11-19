# AGENTS.md — PTaaS (Pentest as a Service)

> Instrucciones para **cualquier** agente de codificación (opencode, Claude Code,
> Cursor, etc.). Es la fuente de verdad del proyecto. `CLAUDE.md` contiene lo
> mismo para Claude Code; si editás las reglas, actualizá ambos.

## Qué construimos
Plataforma de pentest **autorizado** basada en un swarm de agentes:
relevamiento → correlación → análisis → validación controlada → reporte.
Metodología PTES + NIST SP 800-115 + OWASP WSTG + CVSS v4 + CWE + ISO/IEC 29147/30111.

## Reglas duras (no negociables)
1. **La spec manda.** Antes de codear, leé `openspec/specs/` y el change activo.
   Cambios de comportamiento = nuevo delta de spec, no código suelto.
2. **Todo pasa por `Harness.invoke`.** Ningún agente ni módulo invoca herramientas
   de seguridad directamente.
3. **El Scope Guard es determinista** (sin LLM). Toda acción activa exige un
   `ScopeToken` vivo y queda en bitácora, incluso las bloqueadas.
4. **Validación = parametrizar PoCs del catálogo versionado en sandbox**, con gate
   humano (HITL). No se generan exploits nuevos.
5. **Targets solo de laboratorio** (DVWA / Juice Shop en red aislada) durante
   desarrollo y tests.
6. No hardcodear secretos. No ejecutar escaneos reales contra terceros.

## Stack
Python 3.12, Pydantic v2, pytest, LangGraph (orquestación), MCP (adaptadores),
SQLite/Postgres (estado), bitácora append-only con hash encadenado.

## Comandos
- Tests: `python -m pytest -q`  ·  Evals: `python evals/run_evals.py --mode golden`
- Lint/tipos: `ruff check .`  ·  `mypy harness`
- Avance del equipo: `python tools/progress.py`
- Antes de cerrar un change: tests verdes + revisión de seguridad.

## Flujo de trabajo (spec-driven / OpenSpec)
`propose → review → implement → archive`. Los Scenarios Given/When/Then son
criterios de aceptación **y** semillas de tests: **escribí el test primero**.

## Convenciones
- Tipado estricto (`mypy --strict`). Tests por Scenario:
  `tests/<capability>/test_<scenario>.py`.
- Commits chicos que referencian el task de `tasks.md`.
- Docs en español; código e identificadores en inglés.

---

## Este kit funciona con Claude Code **o** con opencode

Las reglas de arriba valen igual en los dos. Lo único que cambia es **de qué
archivo las lee el agente** y qué comodidades de desarrollo tenés.

| | **Claude Code** | **opencode** |
|---|---|---|
| Archivo de reglas | `CLAUDE.md` | `AGENTS.md` (este) |
| Config (modelos, MCP) | `.claude/settings.json` | `opencode.json` |
| Subagentes de desarrollo | `.claude/agents/*.md` | definilos en `opencode.json` → `agent`, o seguí su rol a mano |
| Skills | `.claude/skills/*/SKILL.md` | leelos como guía; opencode no los auto-carga |
| Hook anti-tool-directa | `.claude/hooks/block_direct_security_tools.py` | no aplica como hook |

**Lo importante:** la seguridad **no depende del agente**. El Scope Guard, el
`ScopeToken`, la bitácora y el gate HITL están en el **harness** (`harness/`),
que es código determinista. El hook de Claude Code es una comodidad de
desarrollo; la garantía real es el harness + el CI (`.github/workflows/ci.yml`
corre `pytest` y las evals). Por eso la plataforma es igual de segura la
construyas con el agente que la construyas.

### Arrancar con Claude Code
```bash
cd ptaas-kit && claude
#  "Implementá el change 001-mvp-vertical-slice siguiendo
#   openspec/changes/001-mvp-vertical-slice/tasks.md"
```

### Arrancar con opencode
```bash
cd ptaas-kit && opencode
#  opencode lee AGENTS.md solo. Pedile lo mismo:
#  "Implementá el change 001-mvp-vertical-slice siguiendo
#   openspec/changes/001-mvp-vertical-slice/tasks.md"
```
Si querés rutear modelos por agente como en `harness/models.yaml`, replicá esa
intención en `opencode.json` (ver `docs/model-routing.md`).
