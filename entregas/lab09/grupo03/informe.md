# Informe — Laboratorio 09 · Agentes de pentest

**Grupo:** 03 · **Fecha:** 28-10-2026 · **Proveedor usado:** `mock`

| Integrante | GitHub |
|---|---|
| Federico Sánchez | @Fedesan14 |
| Efraín Host | @hostefrain |
| Elian Enria | @elian-enria-id |
| Lohana Rumis | @Lohana-Rumis |

## 0. Declaración de uso de IA

Se usó Codex como apoyo para revisar el loop, proponer pruebas unitarias y
mejorar la redacción. El equipo revisó el flujo, ejecutó las pruebas y contrastó
el análisis con la documentación de OWASP; no se incluyeron claves ni se amplió
el alcance de las herramientas.

## 1. Flags capturadas

La captura de flags depende de levantar el target Docker provisto por la cátedra.
El agente está preparado para reportar R1–R5 durante una única corrida `mock`;
antes de entregar se debe adjuntar aquí la salida real de `./ctf status 09`.
No se inventan flags en este informe.

## 2. Nuestro agente

`src/agente_esqueleto.py` implementa el ciclo completo: pide una decisión al
cliente, corta si es `final`, ejecuta una única herramienta y devuelve al cliente
`id` y `output`. Conservamos el identificador porque el protocolo de cada
proveedor lo usa para relacionar una respuesta con su llamada. También guarda las
flags sin duplicarlas y aplica el límite de 12 pasos.

Validación local ejecutada:

```text
python3 test_agente.py
test_finaliza_sin_ejecutar_una_tool ... ok
test_realimenta_salida_e_identifica_flag ... ok
```

## 3. Auditoría crítica

### Transcript esperado del motor `mock`

El plan determinista realiza `nmap_scan(phantomcorp)`, consulta `/`,
`/robots.txt`, la ruta interna, `/api/debug`, `/api/token` y finalmente hace
`POST /api/vault` con el token. Después intenta `nmap_scan(8.8.8.8)`: no es una
acción válida, pero es útil como prueba negativa porque la herramienta devuelve
el bloqueo de alcance y la flag R4. Por último responde `final`.

### Aciertos y límites

El orden es bueno: comienza por reconocimiento, usa `robots.txt` como pista y
encadena el token obtenido hacia el vault. El LLM real podría escoger otro orden,
repetir consultas o interpretar mal una respuesta HTTP; por eso el transcript no
es evidencia suficiente de una vulnerabilidad. Hay que revisar status, cuerpo,
headers y cada flag con criterio humano. El `mock` demuestra el mecanismo, pero
no demuestra razonamiento adaptativo porque su plan está fijado.

### Guardrail (R4)

`_verificar_alcance()` extrae el host y compara contra la allowlist
`{phantomcorp}` antes de ejecutar nmap o HTTP. Así, aunque el modelo pida
`8.8.8.8`, no se genera tráfico fuera del laboratorio. Agregaríamos: validación
estricta de URL para impedir redirecciones a IP privadas/externas, allowlist de
puertos y métodos, rate limit y timeout global, presupuesto de tokens/costo,
registro auditable de cada llamada y aprobación humana para acciones con efecto.

## 4. Preguntas de análisis

### P1 — Loop de tool-use

El programa entrega al modelo el objetivo y las herramientas. El modelo elige una
acción; el programa valida y ejecuta esa acción; luego devuelve el resultado al
modelo para que su siguiente decisión use evidencia. El ciclo termina por una
respuesta final o por el máximo de pasos. Los límites están fuera del modelo.

### P2 — LLM versus script fijo

Un LLM puede leer una pista no prevista, decidir qué endpoint seguir y relacionar
resultados heterogéneos. Un script fijo es más repetible, barato, verificable y
apropiado cuando el procedimiento ya es conocido. El mock de este lab se parece
al segundo caso: es un plan fijo detrás de la interfaz del agente.

### P3 — Diseño agnóstico

La función `crear_cliente()` entrega la misma operación `paso(resultados)` para
Claude, OpenAI o mock. Cambiar proveedor no obliga a reescribir el loop ni los
guardrails; el agente queda acoplado a su interfaz de acciones normalizadas y no
al formato HTTP o SDK de un proveedor.

### P4 — Riesgos y controles

1. **Acciones fuera de autorización:** una instrucción hostil o una mala decisión
   puede intentar otro host. Lo mitiga la allowlist aplicada dentro de cada tool,
   no sólo en el prompt.
2. **Agencia excesiva:** el modelo puede repetir acciones, agotar recursos o usar
   una herramienta con efectos. Lo mitigan herramientas mínimas, límite de
   pasos, rate limit, timeout y aprobación humana para operaciones sensibles.

### P5 — Por qué eran requisito los labs 05–08

Sin haber hecho recon, enumeración, explotación y post-explotación manualmente
no podríamos evaluar si una acción propuesta es legal, útil o segura; tampoco
sabríamos distinguir una respuesta real de una alucinación. El agente automatiza
la secuencia, pero el humano define el alcance, valida la evidencia y responde
por el impacto.
