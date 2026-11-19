# Plan de 15 días — de un núcleo verificado a un PTaaS que funciona de punta a punta

## Resumen
En 15 días cada equipo pasa de un **núcleo determinista ya testeado** (guard, token, bitácora, estados, loops, adaptadores acotados, catálogo de verificaciones inertes) a un **recorrido completo sobre un laboratorio aislado**: RoE → recon → correlación → análisis → validación con gate humano → informe. Se avanza en **3 sprints de 5 días** con un checkpoint al final de cada uno. Todo cambio pasa por OpenSpec: spec primero, test segundo, código tercero.

**Supuestos (ajustables):** equipos de 3–4 personas · ~2 h por día · trabajo autónomo con Claude Code · un checkpoint de 20 minutos con el docente al final de cada sprint.

## Reglas que no cambian en ningún día
1. Solo laboratorio propio (`lab/`). Nada contra sistemas de terceros.
2. Toda acción pasa por `Harness.invoke`; sin scope token vivo no hay acción; todo queda en bitácora.
3. La validación solo parametriza el catálogo de verificaciones inertes; ampliarlo exige change + revisión + aprobación humana registrada.
4. Un día termina cuando `python tools/progress.py` y `python -m pytest -q` están verdes y hay commit.

## Roles del equipo (rotan cada sprint)
| Rol | Responsabilidad |
|---|---|
| **Spec lead** | Mantiene `openspec/`; no entra código sin Scenario |
| **Harness lead** | Guard, token, bitácora, estados |
| **Agents lead** | Prompts, schemas, loops, evals |
| **Tools & QA lead** | Adaptadores, laboratorio, tests adversariales |

## Los 6 changes que evolucionan el MVP
| Change | Qué agrega | Sprint |
|---|---|---|
| `002-audit-persistence` | Bitácora en SQLite + verificador de integridad por CLI | 1 |
| `003-roe-and-tokens` | Parser de RoE y emisor de scope tokens con validaciones | 1 |
| `004-recon-loop-a` | Adaptadores de recon reales y loop A integrado | 2 |
| `005-correlation-analysis-loop-b` | Feeds NVD/EPSS offline, ZAP y Nuclei, loop B | 2 |
| `006-sandbox-validation-loop-c` | Sandbox efímero que implementa `Sender` y loop C | 3 |
| `007-reporting-defectdojo` | Informe completo y exportación a DefectDojo | 3 |

Cada uno trae `proposal.md` y `tasks.md` de partida en `openspec/changes/`. **`design.md` y los deltas de spec los escriben los alumnos**: es parte de lo evaluado.

---

## Sprint 1 · Días 1–5 — Dominar y endurecer el núcleo

| Día | Objetivo | Tareas | Terminado cuando… |
|---|---|---|---|
| **1** | Poner todo a andar | Instalar, correr tests y evals, levantar `lab/`, repartir roles, leer `CLAUDE.md` y las 11 specs | 77 tests verdes · el lab responde desde el contenedor `runner` · cada integrante explica el flujo de `Harness.invoke` |
| **2** | Spec sprint | Revisar las specs; proponer **≥ 6 Requirements nuevos** (al menos 3 con Scenario negativo de seguridad); cerrar las "Preguntas abiertas" de `001` | Deltas en `openspec/changes/` aprobados por el equipo y revisados por el `spec-author` |
| **3** | `002-audit-persistence` | Escribir `design.md` y deltas; implementar persistencia SQLite append-only; comando `python -m harness.audit verify` | Scenarios nuevos con test · alterar una fila en la base hace fallar el verificador |
| **4** | `003-roe-and-tokens` | Definir formato de RoE (YAML); parser con validación; emisor de tokens con TTL de `policy.yaml` | RoE sin alcance, con ventana invertida o con CIDR público **se rechaza** · token emitido solo para fase autorizada |
| **5** | **Red team del guard** + Checkpoint 1 | Escribir ≥ 10 tests adversariales (ver `desafios-extension.md`, bloque A) | Todo bypass encontrado queda como test + corrección · demo de 5 min: RoE → token → acción bloqueada y permitida |

**Checkpoint 1 (docente, 20 min):** specs, changes 002 y 003, lista de bypass encontrados y corregidos.

## Sprint 2 · Días 6–10 — Conectar el swarm

| Día | Objetivo | Tareas | Terminado cuando… |
|---|---|---|---|
| **6** | `004-recon-loop-a` (1/2) | Adaptadores `subfinder.enum` y `httpx.probe` con salida validada por schema; fixtures grabadas de salidas reales | Tests con fixtures · argv sin shell · ningún target fuera de lab |
| **7** | `004-recon-loop-a` (2/2) | Conectar loop A: Recon ↔ Correlación con `decide_recon`; persistir `AssetGraph` | Loop A corre contra el lab y se detiene por "grafo estabilizado" o tope · bitácora completa |
| **8** | `005` (1/2) — correlación | Cliente de **snapshots offline** de NVD y EPSS; `cwe.map`; `dedupe` y priorización | Candidatos con evidencia · dato ausente = `null`/`unknown` · cero CVE inventados (eval) |
| **9** | `005` (2/2) — análisis | `zap.baseline_scan` y `nuclei.safe_templates` reales contra el lab; curar **≥ 5 templates** en `templates/allowlist/` | Cada template revisado y registrado en `MANIFEST.md` · `PrioritizedVuln` con `rationale` |
| **10** | Prompts y evals en vivo + Checkpoint 2 | Correr `evals/run_evals.py --mode live`; analizar desvíos; ajustar prompts; ampliar casos a **≥ 20** | Informe de evals (qué falló, por qué, qué cambió) · demo hasta la fase ANALYZE |

**Checkpoint 2:** demo de recon → correlación → análisis sobre el lab, con bitácora verificable y resultados de evals.

## Sprint 3 · Días 11–15 — Validar, reportar y defender

| Día | Objetivo | Tareas | Terminado cuando… |
|---|---|---|---|
| **11** | `006` (1/2) — sandbox | Contenedor efímero en red aislada que implementa `Sender`; se destruye al terminar | Prueba: el sandbox no puede salir a internet · no queda estado |
| **12** | `006` (2/2) — loop C | Orquestar elección de verificación + parámetros con gate humano por hallazgo | Sin aprobación → `PENDING_HITL` · verificación fuera del catálogo → no se ejecuta · evidencia en bitácora |
| **13** | `007-reporting-defectdojo` | Informe completo; exportar a DefectDojo (o a su formato de importación); CLI de gates humanos | Cada hallazgo con CWE + CVSS v4 + remediación · entrega bloqueada sin aprobación |
| **14** | Integración y endurecimiento | Ejecución end-to-end; pasada del `security-reviewer`; mutation checks sobre guard y reporting; documentar | Recorrido completo repetible con un comando · hallazgos del reviewer resueltos o justificados |
| **15** | **Demo final** + Checkpoint 3 | Demo de 10 min; informe técnico de 3–5 páginas; retrospectiva | Entregables completos (ver abajo) |

## Entregables finales
1. Repositorio con `openspec/specs/` actualizado (changes 002–007 archivados).
2. `python tools/progress.py` con **100 %** de tasks de 002–007 y todas las specs con test.
3. Demo end-to-end grabada o en vivo contra el laboratorio.
4. Informe técnico: arquitectura, decisiones, riesgos, resultados de evals y hallazgos del red team del guard.
5. Retrospectiva: qué hizo bien y mal el trabajo con Claude Code (con ejemplos).

## Qué hacer si te atrasás
- **1 día de atraso:** recortá el alcance del día (no el control). Ejemplo: 3 templates en vez de 5.
- **2 o más días:** el orden de prioridad es **harness y guard > loops > herramientas reales > reporting**. DefectDojo se puede reemplazar por exportar JSON.
- **Nunca se recorta:** token vivo, bitácora, gates humanos, catálogo inerte.

## Dónde buscar ayuda
`docs/guia-claude-code-alumnos.md` (cómo trabajar con el agente), `docs/rubrica-evaluacion.md` (cómo se evalúa), `docs/desafios-extension.md` (si te sobra tiempo).
