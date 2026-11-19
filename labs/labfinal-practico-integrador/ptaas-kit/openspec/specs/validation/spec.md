# Delta — validation

Tests: tests/test_poc_catalog.py, tests/test_authorization.py

## Requirement: Solo catálogo curado
La validación DEBE limitarse a PoCs del catálogo versionado y aprobado, ajustando solo parámetros del activo.

### Scenario: PoC fuera del catálogo
- GIVEN un hallazgo priorizado sin PoC en el catálogo
- WHEN el agente de validación intenta proceder
- THEN la validación no se ejecuta y el hallazgo queda "no validado"

## Requirement: Gate humano por hallazgo
La validación DEBE requerir aprobación del Reviewer por cada hallazgo.

### Scenario: sin aprobación
- GIVEN un hallazgo sin aprobación del Reviewer
- WHEN se invoca la validación
- THEN el resultado es PENDING_HITL y no se ejecuta nada

## Requirement: Sandbox efímero
La validación DEBE ejecutarse en un sandbox aislado, sin persistencia ni acceso a datos reales.

### Scenario: fin de la validación
- GIVEN una validación finalizada
- WHEN el sandbox termina
- THEN el entorno es destruido y solo queda la evidencia en la bitácora
