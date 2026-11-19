# Enunciado para alumnos — PTaaS con swarm de agentes

## Resumen
Construir un **pentest autorizado** de punta a punta sobre un laboratorio propio. Los alumnos **constituyen las especificaciones** (11 capabilities, 54 Scenarios), implementan el harness que las hace cumplir y demuestran un recorrido completo. La spec es la fuente de verdad: el código y los tests se derivan de ella.

## Qué deben entregar
1. **Specs** en `openspec/specs/` (las 11 capabilities de la tabla). Este kit trae una base de referencia; deben revisarla, discutirla y ampliarla.
2. **Harness** que haga cumplir las specs (guard, token, bitácora, estados, adaptadores).
3. **Tests**: al menos uno por Scenario.
4. **Al menos un loop agéntico** funcionando (A, B o C).
5. **Selección de herramientas** justificada (`docs/tool-selection.md`).
6. **Demo** contra el laboratorio aislado (DVWA o Juice Shop) con informe final.

## Specs y trazabilidad

| Capability | Scenarios | Tests que la verifican | Estado en el kit |
|---|---|---|---|
| authorization | 4 | `test_authorization.py` | Cubierta |
| engagement-lifecycle | 5 | `test_engagement_and_loops.py`, `test_models_and_terminal_states.py` | Cubierta |
| audit-log | 4 | `test_audit_and_policy.py`, `test_authorization.py` | Falta el Scenario "sin datos sensibles" |
| tool-adapters | 6 | `test_adapters.py`, `test_authorization.py`, `test_audit_and_policy.py` | Cubierta |
| asset-discovery | 6 | `test_engagement_and_loops.py` (loop A) | Faltan rate limit y orden pasivo/activo |
| correlation | 5 | `test_schemas.py` | Falta el bloqueo de sondeo con integración real |
| vuln-analysis | 6 | `test_schemas.py`, `test_engagement_and_loops.py`, `test_authorization.py` | Falta integración con ZAP |
| validation | 3 | `test_poc_catalog.py`, `test_authorization.py` | Falta sandbox real |
| poc-catalog | 7 | `test_poc_catalog.py` | Cubierta |
| reporting | 2 | `test_reporting.py` | Cubierta |
| agent-contracts | 6 | `test_schemas.py`, `test_evals.py`, `test_models_and_terminal_states.py` | Cubierta (evals en modo golden) |

## Ejercicios sugeridos para los alumnos
- Escribir el test que falta de cada fila marcada como pendiente.
- Proponer un nuevo Requirement con su Scenario negativo de seguridad.
- Probar `evals/run_evals.py --mode live` y analizar qué agente se desvía.
- Implementar `Sender` del sandbox efímero (contenedor con red aislada).
- Incorporar un adaptador nuevo (por ejemplo Trivy) siguiendo `mcp-tool-adapter`.

## Reglas
- Solo laboratorio propio. Nada contra sistemas de terceros.
- Sin acciones sin scope token vivo y sin bitácora.
- Sin generar exploits nuevos: solo verificaciones del catálogo.
- Sin saltear los gates humanos.
