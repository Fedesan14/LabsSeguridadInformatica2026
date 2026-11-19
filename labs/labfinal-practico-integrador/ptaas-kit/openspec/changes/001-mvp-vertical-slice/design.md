# Design — Change 001

## Decisiones
1. **Control plane separado del swarm.** `harness/` no depende de ningún LLM; los agentes dependen del harness.
2. **Guard determinista** (CIDR/dominio/ventana/fase + allow-list de `policy.yaml`).
3. **Orquestación:** LangGraph para la máquina de estados (persistencia y reanudación por fase). Alternativa descartada por ahora: grafo propio (más control, más costo).
4. **Bitácora:** append-only con hash encadenado (SHA-256 del registro + hash previo); verificación de integridad en CI.
5. **Salida de agentes:** schemas Pydantic; 2 fallos → HITL.
6. **Sandbox:** contenedor efímero con red aislada para el loop C.
7. **Ruteo de modelos:** ver `harness/models.yaml` y `docs/model-routing.md`.

## Máquina de estados
`CREATED → AUTHORIZED → RECON → CORRELATE → ANALYZE → [HITL] → VALIDATE → [HITL] → REPORT → DELIVERED`
`KILL_SWITCH → ABORTED` desde cualquier estado.

## Riesgos
- Deriva de prompts → evals por agente en CI.
- Alcance mal cargado en el RoE → validación del RoE en el Agente 1 + gate HITL previo a la primera acción activa.
