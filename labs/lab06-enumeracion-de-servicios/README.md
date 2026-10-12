# Laboratorio 06 — Enumeración de servicios

**Unidad 6** · Enumeración: directorios, repositorios expuestos, métodos HTTP y APIs
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab06/grupoXX/`
**Entorno:** Docker (se levanta solo)

> **Continúa el engagement del Lab 05.** Ya hiciste el recon de PhantomCorp:
> tenés el mapa. Ahora **enumerás**. Si no hiciste el Lab 05, hacelo primero —
> este lab asume que entendés recon.

---

## El escenario

Tu recon reveló la intranet de PhantomCorp corriendo en el puerto 80. El mapa
dice "hay un servidor web PhantomCMS 3.7". Bien. ¿Y ahora qué? Un servidor web
no es una cosa: es **decenas** de rutas, archivos, endpoints y métodos, la
mayoría no listados en ningún lado. Tu trabajo en esta fase es **sacarle todo lo
que esconde**: directorios olvidados, archivos de backup, un `.git` expuesto, una
API interna, métodos peligrosos habilitados.

Enumerar es la diferencia entre "hay un web server" y "hay un web server con un
`/backup` accesible, el código fuente filtrado por un `.git`, una API que lista
usuarios y `PUT` habilitado". Lo segundo es un plan de ataque. Lo primero es una
observación inútil.

---

## Por qué este laboratorio

Recon y enumeración se confunden, pero no son lo mismo:

| | **Reconocimiento** (Lab 05) | **Enumeración** (este lab) |
|---|---|---|
| Pregunta | ¿Qué hay? | ¿Qué esconde cada cosa? |
| Alcance | Amplio (puertos, hosts, servicios) | Profundo (dentro de un servicio) |
| Salida | El mapa | El inventario detallado |
| Ejemplo | "puerto 80 abierto, PhantomCMS" | "/backup, /.git, /api/users, PUT on" |

En MITRE ATT&CK esto es la táctica **Discovery** (`TA0007`) sobre un servicio ya
identificado. Es la fase que **más determina** por dónde vas a atacar después.

La regla mental de la enumeración:

> **Todo servicio esconde más de lo que muestra.** El index dice "bienvenido".
> Vos preguntás por lo que NO está en el index: los directorios que nadie linkeó,
> los archivos que quedaron, los métodos que nadie deshabilitó.

---

## Objetivos de aprendizaje

Al terminar deberías poder:

1. Distinguir **enumeración** de **reconocimiento** y ubicar cada una en el flujo.
2. Ejecutar **enumeración de directorios/archivos** con fuerza bruta de rutas
   (`dirb`/`gobuster`) y entender qué es una wordlist y cómo se lee la salida.
3. Hacer **fingerprinting** de la tecnología web (`whatweb`, `nmap -sC`) y usarlo
   para dirigir la enumeración a los archivos default conocidos de ese producto.
4. Identificar **malas configuraciones** enumerables: `.git` expuesto, métodos
   HTTP peligrosos, endpoints de API que filtran datos.
5. Consolidar los hallazgos en un **inventario** priorizado que alimente la fase
   de explotación (Lab 07).

Tributa a la Unidad 6 y a la táctica *Discovery* de ATT&CK.

---

## Requisitos y preparación

Igual que el Lab 05: Docker. Las tools de enumeración ya vienen en la consola.

```bash
make setup            # si no lo corriste antes (ahora suma dirb, gobuster, whatweb, wfuzz)
./ctf lab 06          # levanta la intranet PhantomCorp y abre esta guía
make shell            # entrás a la consola del atacante
```

> Si ya habías hecho el Lab 05, corré `make setup` igual: la consola incorporó
> herramientas nuevas para enumerar.

> **Regla de oro.** Solo `phantomcorp` y los contenedores de la cátedra. Ley 26.388.

---

## Cómo se juega

**5 flags**, una por técnica de enumeración. Se descubren enumerando y se
entregan con `./ctf submit 06 R1 'FLAG{...}'`. El **informe** (inventario +
análisis) es lo que evalúa la rúbrica.

---

## Parte 1 · TEORÍA — enumerar es preguntar por lo oculto

Un servidor web responde distinto según lo que le pidas:

- **200 OK** → existe y te lo da.
- **403 Forbidden** → existe pero no te deja (¡existe! eso ya es información).
- **404 Not Found** → no existe.
- **301/302** → te redirige (a veces a un login que confirma que hay algo).

La **enumeración de directorios** explota esto: probás miles de rutas de una
**wordlist** (lista de nombres comunes: `admin`, `backup`, `api`, `.git`...) y
mirás cuáles NO dan 404. Cada 200 o 403 es un hallazgo.

El **fingerprinting** identifica el producto y versión exactos del servicio. ¿Por
qué importa para enumerar? Porque cada producto tiene **archivos default
conocidos**: si sabés que es WordPress, sabés que existe `/wp-login.php`. Si es
PhantomCMS, sabés dónde mirar. Fingerprint → enumeración dirigida.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — El `.git` que filtró todo.** Un `/.git/` accesible por HTTP permite
reconstruir el **código fuente completo** de la aplicación, con su historia y a
veces credenciales commiteadas por error. Herramientas como `git-dumper` bajan
todo el repo. Un directorio de más = el código entero en manos del atacante.

**Ejemplo B — El backup que nadie borró.** `config.php.bak`, `db.sql.gz`,
`.env.old`. Los editores y despliegues dejan copias. Una enumeración de archivos
con extensiones comunes (`.bak`, `.old`, `.zip`) las encuentra, y adentro suele
haber credenciales de base de datos en claro.

**Ejemplo C — El `PUT` habilitado.** Si un servidor acepta el método `PUT`, un
atacante puede **subir** un archivo (por ejemplo, un webshell) directo al server.
Un `OPTIONS` que responde `Allow: GET, POST, PUT, DELETE` es una alarma roja.

---

## Parte 3 · TOOLS

### 3.1 `dirb` / `gobuster` — enumeración de directorios

Prueban una wordlist de rutas contra el server y reportan las que existen.

```bash
dirb http://phantomcorp/                       # usa la wordlist common.txt por defecto
dirb http://phantomcorp/ -X .bak,.old,.txt      # probar también estas extensiones
# alternativa moderna:
# gobuster dir -u http://phantomcorp -w /usr/share/dirb/wordlists/common.txt
```

**Cómo leer la salida:** `dirb` lista cada ruta encontrada con su código
(`CODE:200`). Ordená mentalmente: los `200` son accesibles, los `403` existen
pero están protegidos (igual son hallazgos: sabés que están ahí).

### 3.2 `whatweb` — fingerprinting web

Identifica CMS, framework, lenguaje, servidor, versiones — todo de las respuestas
HTTP.

```bash
whatweb http://phantomcorp
whatweb -a 3 http://phantomcorp                # -a 3 = agresivo, más pruebas
```

**Cómo leer la salida:** te tira el stack (`HTTPServer`, `X-Powered-By`,
`MetaGenerator`...). Con el producto+versión, buscá sus archivos default y sus
CVEs (eso lo clasificás como en el Lab 05).

### 3.3 `nmap` con scripts (NSE)

nmap no es solo puertos: sus scripts enumeran a fondo.

```bash
nmap -sV -sC phantomcorp                        # -sC = scripts default (incluye http-*)
nmap --script http-methods,http-enum phantomcorp
```

`http-methods` te dice qué métodos acepta el server. `http-enum` prueba rutas
conocidas. **Es enumeración automatizada** — pero tenés que entender qué te dice.

### 3.4 `curl` — el bisturí

Para confirmar y afinar lo que las tools automáticas encuentran:

```bash
curl -s http://phantomcorp/backup/              # ver una ruta puntual
curl -s http://phantomcorp/.git/config          # ¿hay un repo expuesto?
curl -X OPTIONS -i http://phantomcorp/          # ¿qué métodos acepta? mirá el header Allow
curl -s http://phantomcorp/api/users | jq       # enumerar una API y parsear el JSON
```

---

## Parte 4 · PRÁCTICA — enumerá PhantomCorp

Consola (`make shell`). Cada reto, una técnica. La pista te da la técnica, no el
comando.

| Reto | Técnica | Pista |
|---|---|---|
| **R1** | Enumeración de directorios | Corré `dirb` contra el server. Uno de los directorios que encuentre no debería estar accesible y tiene lo que buscás. |
| **R2** | Repositorio Git expuesto | Los desarrolladores despliegan con `git` y a veces se olvidan el `.git`. ¿Qué archivo de configuración de git podrías pedir por HTTP? |
| **R3** | Métodos HTTP peligrosos | ¿Qué método HTTP le preguntás a un server para que te diga TODOS los métodos que acepta? Mirá bien la respuesta, no solo el cuerpo. |
| **R4** | Enumeración de usuarios | Hay una API interna que no debería estar expuesta y lista personal. Probá rutas tipo `/api/...`. |
| **R5** | Fingerprinting de tecnología | Identificá el CMS y su versión con `whatweb`. Ese CMS tiene un archivo default; pedilo. |

```bash
./ctf submit 06 R1 'FLAG{...}'
./ctf status 06
```

---

## Parte 5 · INVENTARIO — el entregable (esto es la nota)

En `entregable.md`, consolidá un **inventario de enumeración** de PhantomCorp:

| Hallazgo | Ruta/Método | Técnica usada | Evidencia | Riesgo | ¿Qué habilita para el Lab 07? |
|---|---|---|---|---|---|
| Backup accesible | `/backup/` | dirb | *(pegá la línea)* | | |
| ... | | | | | |

### Preguntas de análisis

1. **P1.** Diferenciá enumeración de reconocimiento con dos cosas concretas que
   hiciste en el Lab 05 y en este.
2. **P2.** El `.git` expuesto: explicá qué podría reconstruir un atacante con él y
   por qué es más grave que "un archivo de más".
3. **P3.** El método `PUT` habilitado: describí un ataque concreto que lo use.
4. **P4.** La API de usuarios: ¿por qué enumerar usuarios válidos es un problema
   aunque no muestre contraseñas? Pensá en la fase siguiente.
5. **P5.** Sos el defensor: para **tres** de tus hallazgos, dá la mitigación
   concreta.

---

## Qué se entrega

En `entregas/lab06/grupoXX/`: `informe.md` (inventario + P1–P5 + captura de
`./ctf status 06`) y `research.md`. Fecha límite: antes del Lab 07.
Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Enumeración = acceso no autorizado si es contra sistemas ajenos. Solo el lab.
Ley 26.388.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
