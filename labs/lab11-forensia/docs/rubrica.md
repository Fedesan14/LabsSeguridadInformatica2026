# Laboratorio 11 — Rúbrica

**Total:** 100 · **Aprobación:** 60 · **Promoción práctica:** 80

| Componente | Puntos |
|---|---:|
| Los 5 hallazgos (flags) | 15 |
| Línea de tiempo (correlación + evidencia) | 25 |
| IOCs (completos y correctos) | 20 |
| Cadena de custodia (verificación + hallazgo del tampering) | 15 |
| Alcance + contención/erradicación | 15 |
| Preguntas P1–P5 | 10 |

**Timeline (25):** cada evento con su hora Y su evidencia (archivo:línea). Se
evalúa la CORRELACIÓN entre log, disco y memoria, no una lista suelta.
**IOCs (20):** IP atacante, C2 (ip:puerto), webshell, usuario backdoor,
persistencia (cron). Inventar un IOC que no está en la evidencia baja fuerte.
**Custodia (15):** detectar el archivo alterado por hash y explicar por qué
importa.

**Causales de rechazo:** afirmar hallazgos sin evidencia que los respalde;
"contaminar" la evidencia (modificar los archivos del caso); IA no declarada.
