---
name: harness-invariants
description: Usar al escribir o modificar código del harness, guard, scope tokens, bitácora, gates HITL, sandbox o cualquier ejecución de herramientas de seguridad en PTaaS.
---

# Invariantes del harness

Antes de cerrar cualquier cambio, verificar que se cumplan:

- **I1 — Único camino:** toda acción sobre un activo pasa por `Harness.invoke`. Prohibido `subprocess`/`os.system` a herramientas de seguridad fuera de un `ToolAdapter`.
- **I2 — Guard determinista:** `Guard` no usa LLM ni heurísticas probabilísticas. Decide por token (fase, ventana, CIDR/dominio) y allow-list de `harness/policy.yaml`.
- **I3 — Bitácora total:** se registran OK, BLOCKED, PENDING_HITL y ABORTED; append-only con hash encadenado.
- **I4 — Menor privilegio:** el token es por fase y de corta vida; un agente de ANALYZE no puede ejecutar acciones de VALIDATE.
- **I5 — HITL:** gates antes de la primera acción activa, por hallazgo antes de validar, y antes de entregar.
- **I6 — Kill switch:** chequeado primero en `invoke`; estado ABORTED congela el engagement.
- **I7 — Sandbox efímero:** validación sin red hacia afuera, sin persistencia, sin datos de cliente.
- **I8 — Sin armas nuevas:** el validador solo parametriza PoCs del catálogo versionado.

## Checklist de revisión
- [ ] ¿Hay Scenario negativo (bloqueo) por cada nueva capability?
- [ ] ¿El adaptador declara `allowed_phases` y `destructive`?
- [ ] ¿La salida del adaptador es JSON validado por schema?
- [ ] ¿Los tests corren solo contra el laboratorio aislado?
