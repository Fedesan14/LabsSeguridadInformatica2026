# Entregable — Lab Extra 3: Defendé PhantomCorp

**Grupo:** 03 · **Integrantes:** Sánchez, Federico — @Fedesan14 · Enria, Elian — @elian-enria-id · Host, Efraín — @hostefrain · Rumis, Lohana — @Lohana-Rumis

**Declaración de uso de IA:** Claude Code (Anthropic, modelo Opus 5) para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe.
GitHub Copilot con modelo Claude Sonnet 5 para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito.

---

## 1. Tabla de defensas (antes → después)

Diff completo contra el original: `evidencia/salidas/08-diff-server.py.diff`.

| Defensa | Ataque que funcionaba | Fix aplicado (resumen + diff) | Verificación (salida del ataque bloqueado) |
|---|---|---|---|
| **D1** | El header `Server` de toda respuesta devolvía `PhantomServer/2.4.1-debug`, identificando producto, versión exacta y hasta que es un build de *debug*. Un escáner automatizado (o un humano con `curl`) puede buscar CVEs específicos de esa versión sin tocar nada más. Evidencia: `04b-d1-header-server-original.txt` → `Server: PhantomServer/2.4.1-debug`. | Se sobreescribió `version_string()` para devolver `""` **y** se reescribió `send_response()` para no emitir el header `Server` en absoluto. No alcanza con vaciar `server_version`: la clase base (`BaseHTTPRequestHandler.send_response`) arma igual el header llamando a `version_string()`, así que hubo que pisar ese método. | `GET /` ya no trae header `Server` (solo `Date` y `Content-Type`). Evidencia: `04-d1-header-server.txt`. Verificador: `FLAG{def_banner_neutralizado}` en `02-verificador-final-5de5.txt`. |
| **D2** | `GET /api/status` devolvía JSON con `"debug": true`, el path absoluto de la base (`/tmp/phantom_hardening.db`) y el PID del proceso: reconocimiento interno gratis para un atacante. Evidencia: `00-verificador-inicial-1de5-falso-positivo-d5.txt`, línea D2 (`'{"debug": true, "env": "produccion", "db": "/tmp/phantom_har'`). | Se **eliminó por completo** la rama `elif path == "/api/status":` de `do_GET`. El endpoint de debug no se esconde ni se protege con una condición: no existe más en el código de producción, como pide la consigna ("ese endpoint no existe o no expone nada sensible"). | `GET /api/status` → `404` (cae en el mismo `else` que cualquier ruta inexistente). `FLAG{def_debug_apagado}` en `02-verificador-final-5de5.txt`. |
| **D3** | `robots.txt` listaba `/backup` (y `/api/status`) como `Disallow`, delatando su existencia a cualquiera que lo leyera (un bot "educado" no la pisa, pero nada impide que un atacante la lea igual). `/backup` respondía `200` sin autenticación con un dump "pre-migración". Evidencia: `00-verificador-inicial-1de5-falso-positivo-d5.txt`, línea D3 (`GET /backup -> 200; robots menciona /backup: True`). | Se **eliminó la ruta `/backup`** (el propio comentario del código original decía *"BORRAR ESTE ENDPOINT"*: no había ninguna razón de negocio para mantenerla). `robots.txt` quedó sin ningún `Disallow`, porque ya no hay nada sensible que listar. | `GET /backup` → `404`; `robots.txt` ya no menciona `/backup`. `FLAG{def_rutas_blindadas}` en `02-verificador-final-5de5.txt`. |
| **D4** | `/login` armaba el SQL concatenando strings. `user=admin'--&pass=x` comenta el resto de la query y entra sin contraseña válida; `pass=' OR 1=1 --` fuerza que la condición sea siempre verdadera. Evidencia: `00-verificador-inicial-1de5-falso-positivo-d5.txt`, línea D4 (`bypass admin'--: FUNCIONA (vulnerable)`). | Consulta **parametrizada**, con placeholders `?` y una tupla de parámetros: `db.execute("SELECT user FROM usuarios WHERE user = ? AND password = ?", (user, pwd))`. El driver `sqlite3` manda el texto de la consulta y los valores por canales separados: lo que venga en `user`/`pwd` nunca se interpreta como SQL, sea lo que sea que contenga. | Los mismos dos payloads devuelven `"Credenciales inválidas"` (401), en vez de `"Bienvenido"`. Evidencia: `05-d4-sqli-bloqueado.txt`. `FLAG{def_sqli_parametrizado}` en `02-verificador-final-5de5.txt`. |
| **D5** | `/descargar?archivo=` concatenaba `DESCARGAS + "/" + nombre` y abría ese path tal cual, sin validar nada. `archivo=../../../../etc/passwd` sube lo necesario y lee cualquier archivo del sistema. **Nota de entorno:** en Windows el payload exacto del verificador (`/etc/passwd`) no existe, así que el verificador contra el *original* lo marcaba como "bloqueado" por accidente. Confirmamos la vulnerabilidad real contra un archivo que **sí** existe en Windows: `archivo=../../Windows/win.ini` devolvió el contenido completo de `win.ini` desde el servidor sin parchar. Evidencia: `01-d5-original-vulnerable-windows.txt`. | Se resuelve el path pedido a su forma canónica real con `os.path.realpath(os.path.join(DESCARGAS, nombre))` y se verifica que ese resultado quede **dentro** de `DESCARGAS_REAL` (comparación de *paths ya resueltos*, no de substrings del string pedido). Cualquier forma de escribir la subida de directorio (`../`, `%2e%2e%2f` ya decodificado por `parse_qs` antes de llegar a este código, `....//`, una ruta absoluta) termina resolviendo a un path real fuera de `DESCARGAS_REAL`, y se rechaza igual, sin necesitar una regla por cada variante. | Las 4 variantes de traversal (`etc/passwd`, `win.ini` real, `%2e%2e%2f`, `....//`) dan `404`; `manual.txt` legítimo sigue dando `200`. Evidencia: `06-d5-variantes-bloqueadas.txt`. `FLAG{def_traversal_bloqueado}` en `02-verificador-final-5de5.txt`. |

## 2. Regresión funcional

Demostración de que la app **sigue funcionando** después del parche (evidencia cruda en `evidencia/salidas/03-regresion-funcional.txt`):

```bash
$ curl -s -o /dev/null -w 'status=%{http_code}\n' http://127.0.0.1:8080/
status=200

$ curl -s 'http://127.0.0.1:8080/login?user=admin&pass=sup3r-s3cr3t0'
<h1>Bienvenido, admin</h1>

$ curl -s 'http://127.0.0.1:8080/login?user=admin&pass=incorrecta'
<h1>Credenciales inválidas</h1>

$ curl -s 'http://127.0.0.1:8080/descargar?archivo=manual.txt'
Manual de la intranet PhantomCorp.
```

`GET /` responde 200, el login legítimo (`admin` / `sup3r-s3cr3t0`) sigue entrando, el login con contraseña incorrecta sigue dando 401 (no "silenciosamente OK"), y `/descargar?archivo=manual.txt` sigue descargando el archivo real. El parche no rompió nada de lo que la app hacía antes, salvo lo que tenía que dejar de hacer.

## 3. Evidencia de progreso

**Salida del verificador inicial** (contra el `objetivo/` **original**, sin tocar — `evidencia/salidas/00-verificador-inicial-1de5-falso-positivo-d5.txt`):

```
  ✗ D1 — todavía vulnerable  (header Server: 'PhantomServer/2.4.1-debug ')
  ✗ D2 — todavía vulnerable  (GET /api/status -> 200 '{"debug": true, "env": "produccion", "db": "/tmp/phantom_har')
  ✗ D3 — todavía vulnerable  (GET /backup -> 200; robots menciona /backup: True)
  ✗ D4 — todavía vulnerable  (bypass admin'--: FUNCIONA (vulnerable); OR 1=1: FUNCIONA (vulnerable))
  ✓ D5 — ataque BLOQUEADO   (traversal /etc/passwd -> 404 (bloqueado))

1/5 defensas correctas.
```

**Esto no es "D5 ya venía arreglado".** Es un falso positivo del entorno: en Windows no existe el archivo `/etc/passwd` que usa el payload del verificador, así que el `open()` del código *original* (sin ninguna protección) falla igual, pero por "no encuentro el archivo", no porque el traversal esté bloqueado. Lo comprobamos atacando el original con un archivo que sí existe en Windows (`../../Windows/win.ini`) y la lectura arbitraria funcionó completa (`evidencia/salidas/01-d5-original-vulnerable-windows.txt`). El objetivo real de partida es **0/5 vulnerabilidades reales**, aunque el marcador automático diga 1/5 en esta plataforma concreta.

**Salida del verificador final** (contra `entregas/labextra3/grupo03/objetivo/`, parchado — `evidencia/salidas/02-verificador-final-5de5.txt`):

```
  ✓ D1 — ataque BLOQUEADO  (header Server: '')
      flag: FLAG{def_banner_neutralizado}
  ✓ D2 — ataque BLOQUEADO  (GET /api/status -> 404 '404 - no existe')
      flag: FLAG{def_debug_apagado}
  ✓ D3 — ataque BLOQUEADO  (GET /backup -> 404; robots menciona /backup: False)
      flag: FLAG{def_rutas_blindadas}
  ✓ D4 — ataque BLOQUEADO  (bypass admin'--: bloqueado; OR 1=1: bloqueado)
      flag: FLAG{def_sqli_parametrizado}
  ✓ D5 — ataque BLOQUEADO  (traversal /etc/passwd -> 404 (bloqueado))
      flag: FLAG{def_traversal_bloqueado}

5/5 defensas correctas.
Objetivo endurecido. Entregá las 5 flags y escribí el informe.
```

**Captura de `./ctf status extra3`** (`evidencia/salidas/07-ctf-status-extra3.txt`):

```
  ╭────────────────────────────────────────────────────────────╮
  │                   PROGRESO · LAB extra3                   │
  ╰────────────────────────────────────────────────────────────╯

   ✓  D1     Banner neutralizado (info leak de version)
   ✓  D2     Endpoint de debug apagado en produccion
   ✓  D3     Rutas sensibles blindadas (backup + robots)
   ✓  D4     Login parametrizado (SQLi bloqueado)
   ✓  D5     Path traversal bloqueado en /descargar

  ██████████████████████████████  5/5 (100%)

[ OK ] ¡Lab extra3 COMPLETO! Ponete las pilas con la próxima unidad.
```

## 4. Preguntas P1–P5

**P1. Antes/después completo de una defensa (elegimos D5, path traversal).**

*Ataque que funcionaba* (contra el original, archivo real en Windows para que el ataque sea demostrable en este entorno):

```
$ curl -s "http://127.0.0.1:8080/descargar?archivo=../../Windows/win.ini"
; for 16-bit app support
[fonts]
[extensions]
[mci extensions]
[files]
[Mail]
MAPI=1
[ResponseResult]
ResultCode=0
```

*Parche* (diff real, `evidencia/salidas/08-diff-server.py.diff`):

```diff
-            nombre = params.get("archivo", [""])[0]
-            ruta = DESCARGAS + "/" + nombre
-            try:
-                with open(ruta, "rb") as fh:
+            nombre = params.get("archivo", [""])[0]
+            destino = os.path.realpath(os.path.join(DESCARGAS, nombre))
+            dentro = (
+                destino == DESCARGAS_REAL
+                or destino.startswith(DESCARGAS_REAL + os.sep)
+            )
+            if not dentro:
+                self._txt(404, "no encontrado")
+                return
+            try:
+                with open(destino, "rb") as fh:
```

*Ataque bloqueado* (contra la copia parchada, cuatro variantes distintas de la misma técnica):

```
$ curl -s -o /dev/null -w 'status=%{http_code}\n' "http://127.0.0.1:8080/descargar?archivo=../../../../etc/passwd"
status=404
$ curl -s -o /dev/null -w 'status=%{http_code}\n' "http://127.0.0.1:8080/descargar?archivo=../../Windows/win.ini"
status=404
$ curl -s -o /dev/null -w 'status=%{http_code}\n' "http://127.0.0.1:8080/descargar?archivo=%2e%2e%2f%2e%2e%2fWindows%2fwin.ini"
status=404
$ curl -s -o /dev/null -w 'status=%{http_code}\n' "http://127.0.0.1:8080/descargar?archivo=....//....//Windows/win.ini"
status=404
```

**P2. D3: diferencia entre sacar la ruta del `robots.txt` y proteger la ruta. ¿Cuál es la defensa real?**

Sacar (o nunca haber puesto) `/backup` en `robots.txt` solo evita que un escaneo "educado" —que respeta la convención `robots.txt`— la descubra listada ahí. Pero la ruta **sigue existiendo y sigue respondiendo 200 sin autenticación**: cualquiera que la adivine, la encuentre por fuerza bruta de directorios (`gobuster`/`dirb`, exactamente como en los labs 05–07, que no respetan `robots.txt` para nada), o simplemente la conozca (un ex-empleado, un `git log`, código fuente filtrado), accede igual. Retirarla del `robots.txt` es seguridad por oscuridad en su peor forma: ni siquiera protege, solo deja de anunciarla activamente a los bots que eligen portarse bien.

La defensa real es la que aplicamos: **eliminar la ruta** (porque el propio código decía que había que borrarla y no tenía ninguna función de negocio vigente). Si por algún motivo tuviera que seguir existiendo, la defensa real sería autenticación/autorización efectiva en el servidor (devolver 401/403 sin credenciales válidas), no su ausencia del `robots.txt`. El `robots.txt` es, como mucho, una capa cosmética adicional una vez que la ruta ya está protegida o eliminada — nunca el control en sí.

**P3. D1 es solo ocultar información. ¿Es una defensa "real"? Seguridad por oscuridad: cuándo ayuda, cuándo engaña.**

Sí, ocultar el banner de versión es seguridad por oscuridad en sentido estricto: no cierra ninguna vulnerabilidad, solo dificulta que alguien la encuentre.

*Cuándo ayuda:* reduce el *fingerprinting* automatizado y masivo (escáneres tipo Shodan/censys, bots que buscan versiones específicas con CVEs públicos conocidos). Sube el costo de un ataque oportunista genérico que recorre internet buscando versiones vulnerables, y es gratis de implementar — no hay razón para **no** hacerlo como capa adicional (*defense in depth*).

*Cuándo engaña:* si se usa como **única** defensa, o peor, como excusa para no parchear vulnerabilidades reales ("total no saben qué versión es, no hace falta actualizar"), es seguridad falsa. Un atacante dirigido (no oportunista) puede identificar el producto por otras huellas que no dependen del banner: comportamiento de endpoints, formato exacto de los mensajes de error, timing, orden de los headers HTTP. Si la organización confía en el ocultamiento en vez de en el parche, la vulnerabilidad real sigue intacta y además hay una falsa sensación de estar cubiertos.

Conclusión: D1 es una mitigación legítima **como complemento**, nunca como sustituto de arreglar D2–D5.

**P4. Por qué `user.replace("'", "")` no alcanza, y por qué la consulta parametrizada sí es la solución estructural.**

`replace("'", "")` es un filtro de lista negra sobre **un carácter específico**, basado en cómo el atacante escribió el payload *hoy*. Se puede evadir de formas estructuralmente distintas, no solo con otro string "más raro":

- No todos los motores/dialectos necesitan la comilla simple: hay vectores sin comillas en absoluto si el campo no está entre comillas en la query original, o usando codificaciones alternativas de caracteres según el motor.
- El reemplazo no es recursivo: según el orden de aplicación, un string como `''--` podría dejar restos utilizables si el filtro no se aplica de forma exhaustiva.
- Es el mismo argumento de "no hay firma perfecta" del Lab 10: estás tratando de **adivinar y bloquear cada forma** en que el dato puede parecerse a código SQL. Es un juego de lista negra que siempre va un paso atrás del próximo truco de encoding o sintaxis.

La consulta parametrizada no filtra nada, y por eso no tiene ese problema: **separa estructuralmente el código SQL (fijo, parte del programa) de los datos (variables, enviados aparte al motor)**. `cur.execute("... WHERE user = ? AND password = ?", (user, pwd))` le dice al driver "esto es la consulta" y "esto son datos" por canales distintos del protocolo con la base; el motor nunca interpreta el contenido de `user`/`pwd` como sintaxis SQL, sea lo que sea que traigan. No hay "carácter peligroso" que filtrar porque el dato nunca se pega al texto de la consulta. Es un fix estructural (elimina la clase entera de vulnerabilidad), no un parche sobre síntomas puntuales.

**P5. Ranking de los cinco problemas por impacto, con el #1 justificado como para gerencia.**

1. **D4 — SQLi en `/login` (el más grave).** Compromete la autenticación completa: un atacante entra como cualquier usuario sin ninguna credencial real, y la misma técnica de inyección puede extenderse más allá del login para leer o alterar cualquier dato de la base. Es la puerta de entrada más directa a todo el sistema.
2. **D5 — path traversal en `/descargar`.** Lectura arbitraria de archivos del servidor (configuración, código fuente, potencialmente credenciales o claves) sin necesitar autenticarse primero.
3. **D3 — `/backup` sin autenticación.** Exposición directa de un dump de datos, pero acotada a lo que ese endpoint puntual expone, y requiere conocer o adivinar la ruta.
4. **D2 — endpoint de debug en producción.** No expone datos de negocio directamente, pero el PID y la ruta de la base de datos son inteligencia útil para encadenar otros ataques (reconocimiento interno).
5. **D1 — banner de versión (el menos grave).** No compromete nada por sí solo; solo facilita el reconocimiento inicial de un atacante oportunista.

*Para gerencia:* "El problema #1 (D4) es el único de los cinco que podría dejar a un atacante entrar como cualquier empleado —incluido un administrador— sin necesitar ninguna contraseña real, y desde ahí, con la misma técnica, potencialmente leer o alterar cualquier dato de la base, no solo el login. Es la única falla que compromete directamente la confidencialidad e integridad de los datos del negocio (clientes, empleados). Por eso es la prioridad número uno de remediación, por encima de las demás, que exponen información pero no entregan control total del sistema."

## 5. Conclusión

Arreglar fue más difícil que romper, y no por el volumen de código (los cinco fixes son relativamente cortos), sino porque romper necesita encontrar **una** forma de entrar, mientras que defender obliga a razonar sobre **todas** las formas de volver a entrar antes de dar el problema por cerrado. Lo vivimos en carne propia con D5: no alcanzaba con bloquear el string `"../"`; hubo que preguntarse qué pasa con `%2e%2e%2f`, con `....//`, con una ruta absoluta, y —de la forma más dura, por accidente de entorno— qué pasa cuando el payload de ejemplo del propio verificador (`/etc/passwd`) ni siquiera existe en el sistema operativo donde corremos la prueba, lo que casi nos hace creer que una vulnerabilidad real estaba arreglada cuando no lo estaba. Romper es encontrar la excepción que confirma que hay una puerta abierta; defender es argumentar la regla general y después demostrar, con evidencia, que no le quedaron excepciones. Es mucho más trabajo intelectual que ofensivo, aunque el diff final entre quien ataca y quien defiende sea, línea por línea, sorprendentemente corto.