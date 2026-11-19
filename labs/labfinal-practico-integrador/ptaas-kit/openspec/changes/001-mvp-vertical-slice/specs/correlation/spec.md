# Delta — correlation

## Requirement: Correlación sobre datos, sin tocar activos
La correlación DEBE operar solo sobre el `AssetGraph` y feeds de datos (CVE/NVD, EPSS, CWE); NO DEBE iniciar conexiones hacia los activos.

### Scenario: intento de sondeo en fase CORRELATE
- GIVEN un token de fase CORRELATE
- WHEN el agente intenta una acción que contacta un activo
- THEN el harness la bloquea y la registra

## Requirement: Candidato con evidencia
Todo `CandidateFinding` DEBE citar evidencia (activo, versión/tecnología detectada y fuente del dato).

### Scenario: candidato sin evidencia
- GIVEN un candidato sin `evidence_refs`
- WHEN se intenta persistir
- THEN se rechaza por schema inválido

## Requirement: Sin datos inventados
El sistema NO DEBE completar CVE, EPSS ni CWE inexistentes; los datos ausentes DEBEN marcarse como `unknown`/`null`.

### Scenario: tecnología sin CVE conocido
- GIVEN una tecnología sin entradas en el feed
- WHEN se enriquece el activo
- THEN `cve` es `null` y no se genera candidato por CVE

## Requirement: Deduplicación
El sistema DEBE deduplicar candidatos por (activo, CWE/CVE).

### Scenario: mismo hallazgo por dos fuentes
- GIVEN dos candidatos con igual activo y CVE
- WHEN termina la correlación
- THEN queda un único candidato con ambas evidencias

## Requirement: Normalización de taxonomías
Cada candidato DEBERÍA mapearse a CWE y, cuando aplique, a una técnica MITRE ATT&CK.

### Scenario: candidato sin CWE mapeable
- GIVEN un candidato sin CWE derivable
- WHEN se normaliza
- THEN se marca `cwe: unknown` y pasa a análisis con baja confianza
