# PTaaS Kit — Skills, subagentes, harness y ruteo de modelos

Kit para construir la plataforma **Pentest as a Service** (pentest *autorizado*) con Claude Code y desarrollo spec-driven (OpenSpec).

## Contenido

| Ruta | Qué es |
|---|---|
| `CLAUDE.md` | Contexto permanente del proyecto para Claude Code |
| `.claude/settings.json` | Permisos y hooks (guardrails en tiempo de desarrollo) |
| `.claude/agents/` | Subagentes de **desarrollo** (quienes construyen la plataforma) |
| `.claude/skills/` | Skills reutilizables: OpenSpec, invariantes del harness, adaptadores MCP, loops, reporting |
| `openspec/` | `project.md` + change `001-mvp-vertical-slice` (proposal, design, tasks, deltas) |
| `harness/contracts.py` | Contratos tipados del harness (ScopeToken, Guard, invoke, audit) |
| `harness/policy.yaml` | Allow-list de acciones por fase y gates HITL |
| `harness/models.yaml` | **Ruteo de modelos** por agente de runtime |
| `harness/tools.yaml` | Catálogo de capabilities/herramientas (MVP, post-MVP, descartadas) |
| `docs/tool-selection.md` | Selección de herramientas: criterios, matriz por fase, decisiones |
| `prompts/` | System prompts de los 8 agentes de **runtime** del swarm |
| `docs/model-routing.md` | Justificación del ruteo y parámetros por modelo |
| `harness/*.py`, `harness/adapters/`, `harness/poc/` | Núcleo determinista implementado: guard, bitácora, estados, loops, schemas, adaptadores, catálogo de verificaciones inertes, reporte |
| `harness/profiles.yaml` | Perfiles acotados de nmap y Nuclei + hosts de laboratorio permitidos |
| `templates/allowlist/` | Templates de Nuclei curados (vacía: se llena por revisión) |
| `openspec/specs/` | **11 specs estables, 54 Scenarios** (6 capabilities + 5 transversales) |
| `docs/enunciado-alumnos.md` | Enunciado para alumnos y matriz spec → tests |
| `docs/marco-teorico.md` | **Marco teórico y guía de construcción de punta a punta** (20 secciones: teoría, porqués, paso a paso, decisiones, amenazas, plan) |
| `docs/publicar-repositorio.md` | Cómo subir el kit a un repositorio y dejarlo listo para los equipos |
| `CONTRIBUTING.md`, `.github/` | Flujo de ramas, plantillas de PR e issues y CI (pytest, evals, progress) |
| `docs/plan-15-dias.md` | **Plan día por día de 15 días** (3 sprints, checkpoints, qué hacer si te atrasás) |
| `docs/rubrica-evaluacion.md` | Rúbrica con 4 niveles por criterio, evidencia y descalificantes |
| `docs/guia-claude-code-alumnos.md` | Rutina diaria, plantillas de prompts y cómo verificar a la IA |
| `docs/desafios-extension.md` | Red team del guard y desafíos de calidad, ingeniería y gobernanza |
| `openspec/changes/002…007` | Proposal y tasks de partida de los 6 changes que evolucionan el MVP |
| `tools/progress.py` | Autoevaluación: tasks por change, Scenarios por spec, tests |
| `lab/docker-compose.yml` | Laboratorio aislado (DVWA y Juice Shop en red interna) — no probado aquí |
| `presentacion/` | PPT del desafío (`ptaas-desafio.pptx`) y su script generador |
| `tests/` | 77 tests pytest, uno o más por Scenario de las specs |
| `evals/` | Casos golden por agente + rúbrica + runner (`--mode golden` / `live`) |

## Verificar

```bash
pip install pyyaml pytest
python -m pytest -q                      # 77 tests
python evals/run_evals.py --mode golden  # 10 casos
python tools/progress.py                 # avance del equipo
```

## Dos grupos de agentes (no confundir)

1. **Agentes de desarrollo** (`.claude/agents/`): Claude Code los usa para *escribir* la plataforma.
2. **Agentes de runtime** (`prompts/` + `harness/models.yaml`): el swarm que *ejecuta* el engagement dentro de la plataforma.

## Uso — con Claude Code **o** con opencode

El kit funciona con cualquiera de los dos agentes. Las reglas del proyecto están
en [`AGENTS.md`](AGENTS.md) (opencode y otros) y en [`CLAUDE.md`](CLAUDE.md)
(Claude Code) — son el mismo contenido. El mapeo completo está en `AGENTS.md`.

```bash
cd ptaas-kit

# Opción A — Claude Code
claude
#   "Implementá el change 001-mvp-vertical-slice siguiendo
#    openspec/changes/001-mvp-vertical-slice/tasks.md"

# Opción B — opencode  (lee AGENTS.md + opencode.json)
opencode
#   misma consigna que arriba
```

> La seguridad no depende del agente: el Scope Guard, el token de alcance, la
> bitácora y el gate humano viven en el **harness** (código determinista) y los
> valida el CI. Ver `AGENTS.md` § "Este kit funciona con Claude Code o opencode".

## Premisa no negociable

Sin RoE vigente no hay fase activa. El Scope Guard es **código determinista**, nunca un LLM. La validación solo parametriza PoCs de un catálogo curado, en sandbox, con gate humano.
