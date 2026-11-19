# Change 001 — MVP vertical slice

## Por qué
Demostrar end-to-end el swarm + harness + loops sobre un laboratorio propio, como base del trabajo práctico y del desarrollo posterior.

## Qué cambia
- Nuevo harness con Guard determinista, scope tokens, bitácora hash-encadenada, kill switch y gates HITL.
- Seis capabilities mínimas (authorization → reporting) sobre un target de laboratorio.
- Tres loops con tope y condición de parada.

## Fuera de alcance
Multi-tenant, post-explotación, generación de exploits, targets que no sean el laboratorio.

## Criterios de aceptación
1. Toda acción activa tiene scope token vivo y queda en bitácora.
2. Todo intento fuera de alcance se bloquea y se registra.
3. El informe mapea cada hallazgo a CWE + CVSS v4 + remediación.

## Preguntas abiertas
- Runtime de orquestación: LangGraph vs. grafo propio (decidir en `design.md`).
- Catálogo inicial de PoCs aprobados para el laboratorio.
- Almacenamiento de la bitácora (tabla append-only vs. archivo firmado).
