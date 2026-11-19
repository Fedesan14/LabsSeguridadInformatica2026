# Change 005 — Correlación, análisis y loop B

## Por qué
La correlación y el análisis existen como reglas (schemas, dedupe, priorización, parada), pero no hay fuentes de datos ni herramientas de análisis reales conectadas.

## Qué cambia
- Clientes de **snapshots offline** de NVD y EPSS (sin llamadas a internet en tests).
- Mapeo a CWE y deduplicación de candidatos.
- Adaptadores `zap.baseline_scan` y `nuclei.safe_templates` contra el laboratorio.
- Curación de templates en `templates/allowlist/` con registro en `MANIFEST.md`.
- Loop B integrado con `decide_detection`.

## Criterios de aceptación
1. Cada candidato cita evidencia; sin evidencia no hay candidato.
2. Un dato ausente queda como `null`/`unknown`; **no se inventan CVE ni puntajes** (verificado por eval).
3. Solo se usan templates presentes en `templates/allowlist/` y registrados.
4. El loop B termina con hallazgo resuelto, sin ganancia de información o por tope.

## Requisitos a escribir (semillas para `correlation` y `vuln-analysis`)
- Formato y actualización de los snapshots; qué pasa si están desactualizados.
- Criterio de confianza de un candidato.
- Reglas para registrar un template en el manifiesto (revisión y fecha).
- Tratamiento de resultados contradictorios entre ZAP y Nuclei.

## Preguntas abiertas (completar en design.md)
- ¿Cómo se pondera EPSS frente a CVSS y criticidad del activo?
- ¿Qué hace el análisis ante un falso positivo conocido del lab?
- ¿Quién aprueba la incorporación de un template nuevo?
