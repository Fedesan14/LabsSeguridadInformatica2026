# Informe — Laboratorio 05 · Reconocimiento

**Grupo:** 03
**Integrantes:**

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| Federico Sánchez | `13614` | @Fedesan14 |
| Elian Enria | `13245` | @elian-enria-id |
| Efraín Host | `18273` | @hostefrain |
| Lohana Rumis | `14646` | @Lohana-Rumis |

**Fecha:** 28-10-2026

Trabajo conjunto de los cuatro integrantes sobre un único objetivo
(`phantomcorp`, 172.18.0.3) levantado con Docker en la máquina del grupo. Todo
el recon se corrió desde la consola del atacante del lab (`make shell`); ningún
comando se ejecutó contra sistemas fuera del entorno de la cátedra.

---

## 0. Declaración de uso de IA

**¿El grupo usó asistentes de IA en este trabajo?** **Sí.**

| Herramienta | Para qué se usó | Qué partes afectó | Cómo se verificó |
|---|---|---|---|
| Claude Code (Anthropic, modelo Opus) | Operar las herramientas de recon dentro del contenedor, ordenar la evidencia y redactar informe y research | `informe.md`, `research.md`, archivos de `evidencia/` | Cada flag se validó contra el `sha256` publicado en `retos.manifest` y con `./ctf submit` (5/5). El CVE-2015-3306 y su CVSS se verificaron contra la API oficial de NVD, no contra lo que dijo la IA. Las versiones de la tabla salen de la salida real de `nmap -sV` y de los banners, guardados en `evidencia/` |

**Declaración.** Todo el contenido fue revisado y comprendido por los cuatro
integrantes. La IA se usó como apoyo, no como reemplazo del trabajo del grupo.

---

## 1. Parte práctica — flags capturadas

```
   ✓  R1     Puerto oculto en rango alto (barrido completo)
   ✓  R2     Banner grabbing del servicio FTP
   ✓  R3     Fuga de informacion en headers HTTP
   ✓  R4     Enumeracion de rutas via robots.txt
   ✓  R5     Servicio dev expuesto en produccion

  ██████████████████████████████  5/5 (100%)

[ OK ] ¡Lab 05 COMPLETO!
```

Salida completa en [`evidencia/ctf-status-05.txt`](evidencia/ctf-status-05.txt).

| Reto | Técnica | Dónde salió la flag |
|---|---|---|
| R1 | Barrido de puertos | banner del puerto 31337 |
| R2 | Banner grabbing | saludo del FTP (21) |
| R3 | Headers HTTP | cabecera `X-Backend-Flag` del puerto 80 |
| R4 | Enumeración de rutas | ruta `/panel-interno-9x2f` listada en `robots.txt` |
| R5 | Servicio dev expuesto | endpoint `/status` del puerto 8080 |

---

## 2. Mapa de superficie de ataque

Objetivo: `phantomcorp` (172.18.0.3). Base: `nmap -Pn -sV -p-`
([`evidencia/nmap-sV-p-.txt`](evidencia/nmap-sV-p-.txt)).

| Puerto | Servicio | Versión (evidencia) | ¿Cómo lo identificamos? | CVE relevante | CVSS | Criticidad | Justificación (contra ESTE caso) |
|---|---|---|---|---|---|---|---|
| 21 | FTP | **ProFTPD 1.3.5** — banner `220 ProFTPD 1.3.5 Server (PhantomCorp FTP)` y línea nmap `21/tcp open ftp ProFTPD 1.3.5` | banner grabbing con `ncat` + `nmap -sV` | **CVE-2015-3306** (módulo `mod_copy`, `SITE CPFR/CPTO`) | **10.0** (v3.1 `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`; v2 10.0) | **Crítica** | La versión exacta es la única afectada por el CVE: permite a un atacante **no autenticado** leer y escribir archivos arbitrarios y, encadenándolo, ejecución remota de código. No es "FTP viejo" en abstracto: es esta versión puntual con un exploit público y sin necesidad de credenciales |
| 80 | HTTP | **PhantomServer/2.4.1**, `X-Powered-By: PhantomCMS 2.4.1` — headers de `curl -I` | análisis de headers HTTP | Sin CVE público (producto ficticio del lab) | — | **Media** | No hallamos CVE para este producto, y **no inventamos uno**. El problema concreto es fuga de información: el server publica producto y versión en los headers, trae `X-Backend-Flag` (una cabecera que no debería existir) y el HTML tiene un comentario `TODO(infra): sacar el panel interno de produccion`. Cada dato le ahorra trabajo de recon al atacante |
| 8080 | HTTP (API dev) | **Werkzeug 2.0.1 / Python 3.9.2**; app `phantom-dev-api` **0.9.3-DEV** con **`debug:true`** — `nmap -sV` + `curl /status` | fingerprinting de versión + enumeración de endpoint | Sin CVE puntual; es una **mala configuración** | — | **Alta** | Werkzeug es el **servidor de desarrollo** de Flask, no apto para producción, y corre con `debug:true`. Si el debugger interactivo de Werkzeug está activo, su consola permite **ejecutar código Python en el server**. Aun sin eso, `/status` filtra versión y estado interno. Un servicio `-DEV` colgado en producción es superficie que no debería existir |
| 31337 | "maintenance shell" (banner custom) | Banner `PhantomCorp maintenance shell v0.1 -- acceso no autorizado prohibido` — nmap lo marca `Elite?` sin reconocer el servicio | banner grabbing | — (no determinable) | — | **Media/Indeterminada** | **No pudimos determinar producto ni versión**: nmap no lo reconoce y el banner no delata software concreto. Lo honesto es dejarlo así. Igual es un hallazgo: un servicio de "mantenimiento" en un puerto no estándar, alcanzable desde la red, es exactamente el tipo de acceso lateral olvidado que conviene investigar en fases posteriores |

**Nota de método.** Donde no hay evidencia de versión o no hay CVE aplicable lo
decimos explícitamente. Según la rúbrica, inventar un CVE es causal de rechazo;
"no pude determinar" es una respuesta válida.

Evidencia de respaldo (archivos completos en `evidencia/`):

```
# nmap -Pn -sV -p- phantomcorp   (extracto)
PORT      STATE SERVICE VERSION
21/tcp    open  ftp     ProFTPD 1.3.5
80/tcp    open  http    PhantomServer/2.4.1
8080/tcp  open  http    Werkzeug httpd 2.0.1 (Python 3.9.2)
31337/tcp open  Elite?

# ncat phantomcorp 21
220 ProFTPD 1.3.5 Server (PhantomCorp FTP) [::ffff:0.0.0.0]

# curl -I phantomcorp
Server: PhantomServer/2.4.1
X-Powered-By: PhantomCMS 2.4.1
X-Backend-Flag: FLAG{http_headers_leak_info}

# curl phantomcorp/robots.txt
Disallow: /panel-interno-9x2f

# curl phantomcorp:8080/status
{"service":"phantom-dev-api","version":"0.9.3-DEV","debug":true, ...}
```

---

## 3. Preguntas de análisis

**P1 — El puerto que el escaneo default se perdió.**
Honestamente, en **nuestra** corrida el escaneo de los 1000 puertos más comunes
**ya encontró los cuatro**, 31337 incluido: ese número está en la lista de
puertos frecuentes de nmap (es un puerto "famoso" de backdoors históricos), así
que el default lo cubre por casualidad. El `-p-` confirmó que no había nada por
encima (`Not shown: 65531 closed`). La lección operativa es justamente esa: que
el default lo haya agarrado fue **suerte**. Si el servicio hubiera estado en un
puerto arbitrario como el 54321, el escaneo común lo habría pasado por alto. Por
eso `-p-` no es opcional: es el seguro contra el servicio colgado en un puerto
que a nadie se le ocurre mirar. Nunca se cierra un recon con solo los 1000
default.

**P2 — El servicio dev en producción (8080).**
La evidencia es directa: `nmap -sV` lo identifica como **Werkzeug httpd 2.0.1**
—el servidor de desarrollo de Flask, que el propio proyecto advierte que no se
use en producción— y su `/status` devuelve `"version":"0.9.3-DEV"` y
`"debug":true`. Tres señales de que no era para producción: el stack de
desarrollo, el sufijo `-DEV` y el modo debug activo. Es un problema aunque no
tenga un CVE con nombre porque `debug:true` en Flask/Werkzeug habilita el
**debugger interactivo**: ante un error, expone una consola que ejecuta código
Python en el servidor. La mala configuración es la vulnerabilidad; no hace falta
un CVE para que un atacante termine con RCE.

**P3 — La ironía de `robots.txt`.**
`robots.txt` se creó para **SEO**: le pide a los buscadores que no indexen
ciertas rutas. Pero es un archivo público y de lectura libre, así que termina
siendo un **índice de las rutas que el dueño quiere esconder**. Para un atacante
es un mapa regalado. En PhantomCorp el `Disallow: /panel-interno-9x2f` nos llevó
directo a un panel interno que, de otro modo, habría costado adivinar; encima el
archivo traía un comentario (`Migrar a VPN`) confirmando que la ruta sigue
expuesta. Un control pensado para una cosa (indexación) filtra información para
otra (reconocimiento).

**P4 — Pasivo vs. activo.**
Todo lo que hicimos en este lab fue recon **activo**: cada `nmap`, cada `ncat`
al 21 y al 31337, cada `curl` al 80 y al 8080 **abrió una conexión TCP contra
PhantomCorp**, y eso queda en sus logs (el `/panel-interno-9x2f` quedaría como
un GET en el access log del server). El recon **pasivo** sería reunir
información **sin tocar** el objetivo: `whois`, DNS público, certificados,
buscadores. En este lab `phantomcorp` es un host interno sin presencia pública,
así que no hubo pasivo real. De nuestras acciones, el barrido `-p-` es la más
ruidosa: 65535 intentos de conexión son un patrón imposible de confundir con
tráfico legítimo.

**P5 — Ahora somos el defensor.**
Dos hallazgos, dos medidas concretas para PhantomCorp:

1. **FTP ProFTPD 1.3.5 (puerto 21).** Actualizar ProFTPD a una versión con el
   `mod_copy` corregido (≥ 1.3.5a / 1.3.6) o deshabilitar `mod_copy` si no se
   usa, y —si el FTP no es imprescindible— sacarlo de la cara pública y dejarlo
   solo detrás de la VPN. Cierra un RCE no autenticado con CVSS 10.
2. **API dev en 8080.** Bajar el servicio `phantom-dev-api 0.9.3-DEV` de
   producción: apagar `debug`, no publicar el servidor de desarrollo de
   Werkzeug de cara a la red y, si el entorno de dev tiene que existir,
   restringirlo por firewall/VPN a IPs internas. Elimina el riesgo de RCE por el
   debugger y deja de filtrar estado interno por `/status`.

---

## 4. Bitácora de comandos

```bash
# Entorno (desde la raíz del repo, en la máquina del grupo)
make lab N=05
make shell                      # consola del atacante; todo lo de abajo corre acá dentro
ping -c1 phantomcorp            # confirmar alcance (172.18.0.3)

# Descubrir
nmap -Pn phantomcorp            # top-1000: 21, 80, 8080, 31337
nmap -Pn -sV -p- phantomcorp    # 65535 puertos + versiones (la base del mapa)

# Identificar / clasificar
ncat -w3 phantomcorp 21         # banner FTP -> ProFTPD 1.3.5   (R2)
ncat -w3 phantomcorp 31337      # banner maintenance shell      (R1)
curl -I phantomcorp             # headers -> X-Backend-Flag      (R3)
curl -s phantomcorp/robots.txt  # Disallow: /panel-interno-9x2f (R4)
curl -s phantomcorp/panel-interno-9x2f
curl -s phantomcorp:8080/status # phantom-dev-api debug:true     (R5)

# Entregar
./ctf submit 05 R1 'FLAG{...}'  # ... R1..R5
./ctf status 05                 # 5/5
```
