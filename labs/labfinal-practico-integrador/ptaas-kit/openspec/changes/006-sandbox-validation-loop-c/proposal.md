# Change 006 — Sandbox efímero y loop C

## Por qué
El catálogo de verificaciones inertes evalúa respuestas, pero falta el componente que **envía la solicitud de forma aislada** (`Sender`) y el orquestador del loop C con gate humano por hallazgo.

## Qué cambia
- Sandbox efímero (contenedor, red aislada) que implementa `Sender` y se destruye al terminar.
- Orquestación del loop C: el agente de validación **elige una entrada del catálogo y completa sus parámetros**; el resto es determinista.
- Interfaz de línea de comandos para aprobar o rechazar hallazgos.

## Criterios de aceptación
1. Sin aprobación del Reviewer para ese hallazgo, no se envía tráfico (`PENDING_HITL`).
2. Una verificación fuera del catálogo no se ejecuta y el hallazgo queda "no validado".
3. El sandbox no tiene salida a internet y no deja estado al terminar.
4. La evidencia (qué verificación, qué versión, qué parámetros, qué resultado) queda en bitácora.

## Requisitos a escribir (semillas para `validation` y `poc-catalog`)
- Ciclo de vida del sandbox y qué ocurre ante un fallo a mitad de ejecución.
- Límites de tiempo, tamaño de respuesta y cantidad de solicitudes.
- Qué se guarda como evidencia y cómo se redacta para no exponer datos del lab innecesarios.
- Proceso para proponer una **nueva** verificación inerte (change + revisión + aprobación).

## Preguntas abiertas (completar en design.md)
- ¿Cómo se prueba que el sandbox no puede salir a internet?
- ¿Cómo se maneja una verificación que arroja resultados distintos entre corridas?
- ¿Qué pasa si el Reviewer no responde? (timeout y política)
