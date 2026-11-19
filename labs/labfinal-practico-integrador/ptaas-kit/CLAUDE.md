# CLAUDE.md — PTaaS (Pentest as a Service)

> **¿Usás opencode u otro agente?** Las mismas reglas están en [`AGENTS.md`](AGENTS.md).
> Este archivo es la copia que lee Claude Code.


## Qué construimos
Plataforma de pentest autorizado basada en un swarm de agentes: relevamiento → correlación → análisis → validación controlada → reporte. Metodología PTES + NIST SP 800-115 + OWASP WSTG + CVSS v4 + CWE + ISO/IEC 29147/30111.

## Reglas duras (no negociables)
1. **La spec manda.** Antes de codear, leer `openspec/specs/` y el change activo. Cambios de comportamiento = nuevo delta de spec, no código suelto.
2. **Todo pasa por `Harness.invoke`.** Ningún agente ni módulo invoca herramientas de seguridad directamente.
3. **El Scope Guard es determinista** (sin LLM). Toda acción activa exige `ScopeToken` vivo y queda en bitácora, incluso las bloqueadas.
4. **Validación = parametrizar PoCs del catálogo versionado en sandbox**, con gate HITL. No se generan exploits nuevos.
5. **Targets solo de laboratorio** (DVWA / Juice Shop en red aislada) durante desarrollo y tests.
6. No hardcodear secretos. No ejecutar escaneos reales contra terceros desde esta sesión.

## Stack
Python 3.12, Pydantic v2, pytest, LangGraph (orquestación), MCP (adaptadores), SQLite/Postgres (estado), bitácora append-only con hash encadenado.

## Comandos
- Tests: `python -m pytest -q` · Evals: `python evals/run_evals.py --mode golden`
- Lint/tipos: `ruff check .` · `mypy harness`
- Antes de cerrar un change: tests verdes + `security-reviewer`.

## Flujo de trabajo
Usar el skill `openspec-workflow`: propose → review → implement → archive. Los Scenarios Given/When/Then son criterios de aceptación y semillas de tests (escribir el test primero).

## Convenciones
- Tipado estricto, `mypy --strict`. Tests por Scenario: `tests/<capability>/test_<scenario>.py`.
- Commits pequeños referenciando el task de `tasks.md`.
- Idioma de docs: español. Código e identificadores: inglés.
