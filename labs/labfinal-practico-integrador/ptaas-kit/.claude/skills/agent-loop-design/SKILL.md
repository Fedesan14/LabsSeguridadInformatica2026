---
name: agent-loop-design
description: Usar al diseñar o implementar los loops agénticos de PTaaS (relevamiento, correlación/detección, validación) con plan-act-observe-reflect, topes y condiciones de parada.
---

# Diseño de loops agénticos

Estructura común: **plan → act (vía Harness.invoke) → observe → reflect → ¿parar?**

| Loop | Agentes | Parada | Tope (policy.yaml) |
|---|---|---|---|
| A. Relevamiento | Recon ↔ Correlation | 0 activos nuevos en scope | 5 |
| B. Detección | Correlation ↔ Vuln Analysis | hallazgo confirmado/descartado o sin ganancia de información | 4 |
| C. Validación | Validation (con HITL) | evidencia suficiente o intentos agotados | 2 |

## Reglas
- Cada `act` es una llamada al harness; el loop nunca ejecuta directo.
- Estado del loop persistido (reanudable) y registrado en bitácora.
- La reflexión produce un objeto tipado (`LoopDecision{continue|stop, reason}`), no texto libre.
- Detectar no-progreso: si dos iteraciones no agregan activos/evidencia nuevos → parar.
- Loop C: solo `poc_catalog.run_parametrized`; el modelo elige PoC del catálogo y completa parámetros (host, puerto, endpoint), sin escribir código de explotación.
- Ante schema inválido 2 veces → escalar a HITL.
