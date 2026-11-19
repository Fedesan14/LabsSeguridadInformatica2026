# Change 007 — Informe completo y DefectDojo

## Por qué
El generador de informes valida campos, pero falta armar el informe real desde la bitácora y los hallazgos, y entregarlo a una herramienta de gestión de vulnerabilidades.

## Qué cambia
- Construcción del informe desde `PrioritizedVuln` y `Evidence` (con referencias a bitácora).
- Cálculo/validación del vector CVSS v4.0 y presentación junto a EPSS.
- Exportación a DefectDojo (API) o, si no hay instancia, a su formato de importación.
- Entrega condicionada a la aprobación del Reviewer.

## Criterios de aceptación
1. Cada hallazgo incluye CWE, vector CVSS v4.0 válido y remediación; si falta algo, el informe **no se genera** y se indica el campo.
2. El informe distingue "validado en sandbox" de "no validado".
3. Sin aprobación del Reviewer, el estado queda en REPORT y no se entrega.
4. Todo lo exportado es reproducible a partir de la bitácora.

## Requisitos a escribir (semillas para `reporting`)
- Estructura PTES §7 y resumen ejecutivo para audiencia no técnica.
- Redacción de evidencia sin datos sensibles.
- Plantilla de divulgación (ISO/IEC 29147) para hallazgos del lab.
- Manejo de hallazgos duplicados entre ejecuciones.

## Preguntas abiertas (completar en design.md)
- ¿Cómo se versiona un informe si cambia un hallazgo después de generado?
- ¿Qué información NO debe salir del sistema hacia DefectDojo?
- ¿Cómo se trata un hallazgo "no validado" de severidad alta?
