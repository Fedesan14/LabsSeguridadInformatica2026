# Delta — vuln-analysis

Tests: tests/test_schemas.py, tests/test_engagement_and_loops.py, tests/test_authorization.py

## Requirement: Análisis no destructivo
El análisis DEBE usar solo capabilities marcadas `destructive: false`.

### Scenario: capability destructiva
- GIVEN un adaptador con `destructive: true`
- WHEN el agente intenta usarlo en fase ANALYZE
- THEN el harness lo bloquea y lo registra

## Requirement: Análisis no valida explotabilidad
El análisis NO DEBE ejecutar PoCs ni acciones de fase VALIDATE.

### Scenario: acción de validación en ANALYZE
- GIVEN un token de fase ANALYZE
- WHEN se invoca `poc_catalog.run_parametrized`
- THEN la acción es bloqueada por fase y registrada

## Requirement: Estado explícito por hallazgo
Cada candidato analizado DEBE resolverse como `confirmed`, `discarded` o `inconclusive`, con justificación y referencias de evidencia.

### Scenario: resultado sin justificación
- GIVEN un `PrioritizedVuln` sin `rationale`
- WHEN se intenta persistir
- THEN se rechaza por schema inválido

## Requirement: Priorización con CVSS v4, EPSS y contexto
La prioridad DEBE derivarse de CVSS v4.0, EPSS (si existe) y el contexto del activo, de forma reproducible.

### Scenario: mismos insumos, misma prioridad
- GIVEN dos corridas con idénticos insumos
- WHEN se calcula la prioridad
- THEN el resultado es idéntico

## Requirement: Loop de detección acotado
El loop B DEBE detenerse con hallazgo resuelto, tras dos iteraciones sin información nueva, o al alcanzar el tope.

### Scenario: sin ganancia de información
- GIVEN dos iteraciones consecutivas sin evidencia nueva
- WHEN el agente evalúa continuar
- THEN `LoopDecision` es `stop` y el hallazgo queda `inconclusive`

## Requirement: Reintento y escalado
Ante dos salidas con schema inválido, el sistema DEBE escalar a HITL.

### Scenario: schema inválido repetido
- GIVEN dos respuestas consecutivas que no validan
- WHEN se procesa la tercera solicitud
- THEN el estado pasa a PENDING_HITL y no se reintenta
