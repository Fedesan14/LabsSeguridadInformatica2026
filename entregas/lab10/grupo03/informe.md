# Informe — Laboratorio 10 · Detección y evasión

**Grupo:** 03 · **Integrantes:** Federico Sánchez — @Fedesan14 · Elian Enria — @elian-enria-id · Efraín Host — @hostefrain · Lohana Rumis — @Lohana-Rumis

## 0. Declaración de uso de IA

Claude Code (Anthropic, modelo Opus 5) para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe.
GitHub Copilot con modelo Claude Sonnet 5 para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito.

## 1. Flags capturadas (salida de `./ctf status 10`)

```
  ╭────────────────────────────────────────────────────────────╮
  │                     PROGRESO · LAB 10                     │
  ╰────────────────────────────────────────────────────────────╯

   ✓  R1     Acceso a la vista del SOC
   ✓  R2     Disparar una deteccion (te vieron)
   ✓  R3     Conocer el ruleset del IDS
   ✓  R4     Evadir una firma de deteccion
   ✓  R5     Encontrar la intrusion en el ruido

  ██████████████████████████████  5/5 (100%)

[ OK ] ¡Lab 10 COMPLETO! Ponete las pilas con la próxima unidad.
```

## 2. Tabla de firmas

| Firma | Cómo se evade | Cómo se mejora la detección |
|---|---|---|
| **scanner-ua** | La firma es `re.search(r"sqlmap\|nikto\|nmap\|dirb", ua, re.I)` sobre el header `User-Agent`, un campo que el cliente declara libremente. `curl -A sqlmap http://phantomcorp/` dispara la alerta (`FLAG{detection_triggered}`); la **misma** request con `curl -A 'Mozilla/5.0'` (o sin `-A`) pasa como tráfico benigno sin tocar el payload. Herramientas reales como sqlmap traen incluso un flag (`--random-agent`) para automatizar esto. | No basar la detección en metadata que el atacante controla al 100%. Conviene mirar comportamiento difícil de falsear: volumen/dispersión de requests por IP en poco tiempo (un scan real toca decenas de rutas en segundos, un browser no), secuencias típicas de reconocimiento (`/admin`, `/.git`, `/wp-login` sin sesión previa ni referer), fingerprinting pasivo de la pila TCP/TLS (JA3/JA3S, orden de headers) y tratar la UA como **una señal más** dentro de un score combinado, no como la única condición de alerta. |
| **sqli-union** | La firma exige `union\s+select` (espacio **real**). Un comentario SQL vacío cumple la misma función para el motor de base de datos sin ser un carácter de `\s`: `GET /api?q=union/**/select+1` devolvió 200 con `FLAG{signature_evaded}`. Verificamos además que el **mismo payload con el espacio percent-encoded** (`%20`, como lo manda cualquier navegador real) *también* evade la firma, porque el servidor nunca decodifica el query antes de aplicar el regex (`\s` no matchea contra los caracteres literales `%`, `2`, `0`). Es decir: tal como está escrita, la regla ni siquiera detecta un `UNION SELECT` "normal" enviado por un cliente HTTP estándar, solo el caso en que alguien escribe el espacio literal, algo que ni el propio protocolo HTTP permite transmitir en la línea de request (lo confirmamos: un espacio crudo en la query rompe el parseo HTTP con `400 Bad request syntax`). | Parchear agregando `/\*.*?\*/` al regex solo tapa este caso puntual. Lo correcto es **normalizar antes de matchear**, no intentar que la regex prevea cada separador posible: `` `q = unquote_plus(q); q = re.sub(r"/\*.*?\*/", " ", q)` `` y recién ahí aplicar `union\s+select`. Es el mismo principio que usan motores reales como Suricata: reconstruir un buffer normalizado del protocolo (`http.uri`) y matchear ahí, en vez de sobre el byte crudo (ver `research.md`). Aun con ese fix, la regla sigue siendo evadible (paréntesis `union(select...)`, doble encoding `%2520`, fragmentar el payload en otro parámetro o en el body de un POST que el IDS no inspeccione) — por eso la mejora real no termina en "una regla mejor", sino en sumar una capa de anomalía/comportamiento y revisión humana del log, como en R5. |

## 3. Preguntas P1–P5

### P1. ¿Por qué la detección por firmas es evadible por diseño? ¿Qué la complementa?

Una firma codifica una representación sintáctica puntual de una intención maliciosa (un string, una regex), no la intención en sí: el motor no entiende SQL ni HTTP, solo compara patrones. Una misma intención (hacer un `UNION SELECT`) tiene infinitas representaciones sintácticas equivalentes para la base de datos (con espacio, con comentario, con paréntesis, con mayúsculas, con `%XX` sin decodificar…). Alcanza con que el atacante encuentre **una** representación que el autor de la regla no anticipó. No es un defecto de nuestra firma de juguete: NIST SP 800-94 (ver `research.md`) describe la detección por firmas precisamente así: el método más rápido y preciso contra lo *ya conocido*, pero estructuralmente incapaz de generalizar a variantes no vistas.

La complementan: **(a)** detección por anomalía, que mira desvíos de un perfil estadístico de lo "normal" en vez de patrones puntuales, y por eso puede atrapar variantes nunca vistas; **(b)** análisis de protocolo con estado, que valida que el tráfico respete el RFC del protocolo en lugar de buscar un string; y **(c)**, lo que demostró R5, el analista humano leyendo logs, capaz de reconocer intención maliciosa en tráfico que ninguna regla marcó como `ALERT`.

### P2. Reescribí la regla de `sqli-union` para que no se evada con `/**/`. ¿Se puede hacer una firma "perfecta"?

```python
from urllib.parse import unquote_plus

def _normalizar(q: str) -> str:
    q = unquote_plus(q)                  # %20, +, %0a, %09 -> espacio real
    return re.sub(r"/\*.*?\*/", " ", q)  # /**/ (comentario SQL) -> espacio real

FIRMAS = [
    # ...
    ("sqli-union", lambda path, q, ua:
        bool(re.search(r"union\s+select", _normalizar(q), re.I))),
]
```

Esta versión tapa **las dos** evasiones que encontramos en la tabla (comentario SQL y percent-encoding), porque normaliza el dato antes de decidir, en vez de intentar enumerar separadores dentro del regex.

**¿Firma perfecta? No.** Esta versión mejorada sigue cayendo ante, por ejemplo: `union(select 1)` (en varios motores SQL el paréntesis es un separador válido sin que haga falta ningún espacio ni comentario); doble encoding (`%2520`, que tras un solo `unquote_plus` queda como `%20` literal, no como espacio); partir el payload entre dos parámetros distintos del query, o mandarlo en el body de un `POST` que esta firma no inspecciona; variantes de la propia sentencia (`UNION ALL SELECT`, `INTERSECT`) que ni siquiera usan la palabra `SELECT` pegada a `UNION`. Cada arreglo cierra un camino conocido y dejé abiertos los que el autor de la regla todavía no imaginó: por diseño, un patrón finito nunca puede cubrir un espacio infinito de representaciones equivalentes. Por eso ninguna firma es "perfecta"; lo que existe es una firma razonable **más** otras capas (normalización de protocolo, límites de tasa, anomalía, revisión humana) que hacen que, en conjunto, sea cada vez más caro para el atacante encontrar el próximo hueco.

### P3. Detectar por User-Agent: ¿por qué es una detección débil? ¿Qué mirarías en lugar de "quién decís ser"?

Es débil porque el `User-Agent` es un dato que el **cliente** declara y que el servidor nunca verifica contra nada: no hay ninguna garantía criptográfica ni de comportamiento detrás de ese string, cambiarlo es un flag de línea de comandos (`curl -A`, `sqlmap --random-agent`). Detectar por UA es, literalmente, preguntarle al atacante "¿sos un atacante?" y confiar en la respuesta. Lo demostramos en R2/R4: la misma herramienta, el mismo payload, distinto header, resultado opuesto.

En lugar de "quién decís ser", miraría **qué hacés**: volumen y velocidad de requests por origen (un humano con navegador no pide 40 rutas por segundo), la forma de las rutas solicitadas (secuencias de reconocimiento: `/admin`, `/.git/config`, `/wp-login.php`, `/phpmyadmin`, sin que medie nunca un link previo ni una sesión), ausencia de las señales que un navegador real sí deja (sin `Accept-Language`, sin `Referer`, sin ejecutar JavaScript/cargar assets de la página), y fingerprinting de la conexión TCP/TLS (orden de los headers HTTP, JA3/JA3S de la negociación TLS), que es mucho más caro de falsificar de forma consistente que un string.

### P4. El R5: la intrusión estaba en el log. ¿Qué habría hecho que se detecte automáticamente y no dependiera de que alguien la mire?

La intrusión de R5 **ya fue detectada automáticamente**: la línea del log dice explícitamente `ALERT[path-traversal]` — la firma `path-traversal` (`"../" in path`) se disparó en el momento del ataque real contra `/admin/../../etc/passwd`. El problema no fue la detección, fue la **respuesta**: esa única línea quedó mezclada entre 120 líneas `BENIGN` de tráfico de catálogo, logueada de forma pasiva, sin que nadie la mirara hasta que nosotros hicimos `grep ALERT`. Es exactamente el Ejemplo C del README: "la herramienta no falló; faltó el analista".

Para que no dependiera de que alguien abriera el log a mano, haría falta cerrar el círculo detección → acción: **(a)** alerting activo en vez de logueo pasivo (un webhook/ticket automático cuando se escribe un `ALERT`, no un archivo de texto que alguien tiene que decidir abrir); **(b)** clasificar severidad por firma (un `path-traversal` contra `/etc/passwd` es mucho más grave que un `scanner-ua`, y no debería quedar en la misma lista plana sin prioridad); **(c)** modo IPS y no solo IDS para firmas de alta confianza, bloqueando la request en vez de solo registrarla; **(d)** separar la señal del ruido en la presentación del log (vista filtrada de `ALERT`, o no loguear lo benigno con el mismo detalle), para que una sola línea real no se diluya entre 120 idénticas.

### P5. Cierre del curso: ¿por qué un buen atacante tiene que entender al defensor, y viceversa?

Porque las dos caras, explotar y defender, comparten el mismo modelo mental: *¿qué comportamiento o patrón delata esto, y cómo lo evito o lo detecto?* Lo vimos de las dos maneras en el mismo lab: para evadir `sqli-union` (R4) tuvimos que pensar como el autor de la regla (¿qué exige exactamente el regex, y qué no cubre?) y encontrar el hueco; para proponer una regla mejor (P2) tuvimos que pensar como atacante (¿qué otra forma de escribir lo mismo no cubre mi regla?) antes de poder escribirla. Y al revés: entender que el `User-Agent` es falsificable (P3) es la misma observación que necesita un atacante para evadir esa detección y que necesita un analista para dejar de confiar en ella.

El recorrido del curso (05–08 ataque, 09 agentes, 10 defensa) cierra ese círculo: no hay "conocimiento ofensivo" y "conocimiento defensivo" como dos disciplinas separadas, hay un único modelo de amenaza visto desde los dos lados de la misma mesa. Un pentester que no entiende cómo loguea y correlaciona un SOC deja evidencia obvia sin darse cuenta de que la deja; un analista que no entiende técnicas de evasión escribe reglas tan frágiles como la `sqli-union` original, esquivables con un truco de sintaxis de un párrafo. Red y Blue no son dos carreras distintas: son la misma pregunta, hecha desde los dos lados.

## 4. Bitácora

Entorno levantado localmente ejecutando `labs/lab10-deteccion-evasion/entorno/phantomcorp/server.py` directamente con Python 3.12 (mismo código que corre el `Dockerfile` del lab; no había Docker disponible en esta máquina, así que se corrió el target tal cual, sin modificarlo, fuera del
contenedor). Todo el tráfico se mandó **solo** contra este target, según la regla de oro del lab.

```bash
$ curl -s http://phantomcorp/soc
=== PhantomCorp SOC · vista de eventos ===
Acceso a la consola del SOC concedido. FLAG{soc_log_access}
Tip: filtrá por ALERT. Hay UNA intrusion real que no disparaste vos.
------------------------------------------------------------
10.0.1.21 - GET /catalogo?item=1 200 BENIGN
...

$ curl -s -A sqlmap http://phantomcorp/
🚨 ALERTA IDS · firma 'scanner-ua' disparada.
Tu request fue DETECTADA y logueada. FLAG{detection_triggered}
Para ver todas las reglas: GET /soc/reglas

$ curl -s http://phantomcorp/soc/reglas
=== Ruleset del IDS (firmas activas) ===
Conocer las reglas es el primer paso para evadirlas. FLAG{signature_ruleset}
  scanner-ua      User-Agent contiene sqlmap|nikto|nmap|dirb
  path-traversal  la ruta contiene '../'
  git-probe       la ruta contiene '/.git'
  sqli-union      el query matchea /union\s+select/  (OJO: exige un ESPACIO)

$ curl -s "http://phantomcorp/api?q=union/**/select+1"
200 OK (procesado como benigno)
Tu request ERA maliciosa pero NINGUNA firma la detectó. FLAG{signature_evaded}

$ curl -s http://phantomcorp/soc | grep ALERT
185.220.101.42 - GET /admin/../../etc/passwd 200 ALERT[path-traversal] # intrusion no atribuida -> FLAG{intrusion_in_the_noise}

$ ./ctf submit 10 R1 'FLAG{soc_log_access}'
$ ./ctf submit 10 R2 'FLAG{detection_triggered}'
$ ./ctf submit 10 R3 'FLAG{signature_ruleset}'
$ ./ctf submit 10 R4 'FLAG{signature_evaded}'
$ ./ctf submit 10 R5 'FLAG{intrusion_in_the_noise}'
$ ./ctf status 10          # ver sección 1 de este informe
```

**Verificación adicional (relevante para la tabla de firmas):**
confirmamos que la secuencia `union%20select` (espacio percent-encoded, como lo manda cualquier cliente HTTP real) evade la firma por la misma razón estructural que `/**/` — el servidor no decodifica el query antes de aplicar el regex — y que un espacio **literal** sin codificar ni siquiera es transmisible en una línea de request HTTP válida (`400 Bad request syntax` al probarlo con un socket crudo).
