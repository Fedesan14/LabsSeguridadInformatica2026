# Delta — reporting

## Requirement: Hallazgo completo
Cada hallazgo del informe DEBE incluir CWE, CVSS v4.0 y recomendación de remediación.

### Scenario: hallazgo sin CWE
- GIVEN un hallazgo sin CWE asignado
- WHEN se genera el informe
- THEN la generación falla con error indicando el campo faltante

## Requirement: Entrega con aprobación
El informe NO DEBE entregarse sin aprobación del Reviewer.

### Scenario: entrega sin aprobación
- GIVEN un informe generado y sin aprobación
- WHEN se intenta entregar
- THEN el estado permanece en REPORT y se registra PENDING_HITL
