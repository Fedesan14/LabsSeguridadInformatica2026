# Laboratorio 05 — Reconocimiento

**Unidad 5** · Vulnerabilidades: identificación, clasificación y explotación
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab05/grupoXX/`
**Entorno:** Docker (se levanta solo — no instalás ninguna tool en tu máquina)

> Este es el **primer laboratorio ofensivo** de la asignatura. Cambia la
> mecánica: además del informe, vas a **operar herramientas reales contra un
> objetivo real** (deliberadamente vulnerable, dentro de tu propia máquina).
> Leé entero este README **antes** de tirar un solo comando.

---

## El escenario

**PhantomCorp S.A.** te contrató. Sos el pentester junior de la consultora y te
toca la **fase 1 de un engagement**: el reconocimiento del perímetro. Todavía no
tenés que romper nada. Tu trabajo es **descubrir y clasificar** qué tiene
PhantomCorp expuesto: qué servicios corren, en qué puertos, con qué versiones, y
qué de eso es un problema.

Un buen recon es el 80% de un pentest. El que escanea a lo bruto y no entiende lo
que ve, después dispara exploits al azar. Vos no. Vos vas a mapear la superficie
como un profesional y a **fundamentar** cada hallazgo.

A lo largo del engagement (labs 05 a 09) vas a volver sobre PhantomCorp:
enumerar, explotar, escalar y, al final, automatizar todo con un agente. Pero
todo arranca **acá**, entendiendo el terreno.

---

## Por qué este laboratorio

El reconocimiento es la **primera fase de cualquier ataque** (y de cualquier
defensa: no podés proteger lo que no sabés que tenés expuesto). Está en la base
de todos los marcos: es *Reconnaissance* en la Cyber Kill Chain de Lockheed
Martin, es `TA0043` en MITRE ATT&CK, es la fase 1 del PTES.

La idea central es simple y potente:

> **Antes de tocar nada, entendé qué hay.** Un puerto abierto no es un hallazgo.
> Un puerto abierto **identificado y clasificado** — "el 21 corre ProFTPD 1.3.5,
> que tiene el CVE-2015-3306 de ejecución remota" — eso sí es un hallazgo.

Este laboratorio ataca esa idea con las cuatro partes de siempre: primero el
**concepto**, después **ejemplos**, después las **herramientas** una por una, y
recién al final vos con las manos en el teclado. Si saltás a la Parte 4 sin
haber leído las Partes 1 a 3, vas a estar copiando comandos sin entender la
salida. Y eso no es pentesting: es adivinar.

---

## Objetivos de aprendizaje

Al terminar deberías poder:

1. Distinguir **reconocimiento pasivo** de **activo**, y justificar cuándo se usa
   cada uno y qué huella deja cada uno.
2. Ejecutar un **barrido de puertos** con `nmap` entendiendo la diferencia entre
   los tipos de escaneo (`-sS`, `-sT`, `-sV`, `-p-`) y **leer** su salida.
3. Hacer **banner grabbing** y **fingerprinting** de servicios para identificar
   producto y versión.
4. **Clasificar** un servicio identificado contra fuentes de vulnerabilidades
   (CVE / CVSS) y estimar su criticidad.
5. Construir un **mapa de superficie de ataque** defendible, con evidencia
   concreta de cada hallazgo.

Tributa al **Objetivo 5** del Diseño Curricular y a los resultados de
aprendizaje de la Unidad 5.

---

## Requisitos

- **Docker** y **Docker Compose** (Docker Desktop en Mac/Windows; `docker` +
  plugin `compose` en Linux). Verificá:

  ```bash
  docker --version
  docker compose version
  ```

- Git y una cuenta de GitHub por integrante.
- Haber leído [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

No hace falta instalar `nmap` ni nada: **todas las tools vienen dentro del
contenedor atacante**. Tu máquina queda limpia.

---

## Preparación del entorno

Desde la raíz del repo, la **primera vez** construí la consola del atacante
(tarda unos minutos, baja las herramientas):

```bash
make setup
```

Después, arrancá el laboratorio. Esto levanta la consola + el target PhantomCorp
y te muestra los próximos pasos:

```bash
./ctf lab 05
```

Entrá a la consola del atacante (desde ahí operás TODO):

```bash
make shell
```

Adentro vas a ver el objetivo disponible con el nombre `phantomcorp`. Probá que
lo alcanzás:

```bash
ping -c1 phantomcorp
```

Para bajar todo cuando termines: `make down`.

> **Regla de oro, sin excepciones.** Solo escaneás `phantomcorp` y los
> contenedores de este lab. Correr estas técnicas contra cualquier sistema que
> no sea tuyo o de la cátedra es **delito** (Ley 26.388). Ver
> [Uso responsable](../../CONTRIBUTING.md).

---

## Cómo se juega

Este lab tiene **dos entregas que se complementan**:

1. **Los retos (flags).** Hay **5 flags** escondidas en los servicios de
   PhantomCorp. Cada una premia una técnica de recon distinta. Las descubrís
   operando las tools y las entregás para llevar el progreso:

   ```bash
   ./ctf submit 05 R1 'FLAG{...}'
   ./ctf status 05
   ```

   Las flags **no se leen de ningún archivo**: se ganan haciendo. Son el motor
   que te mantiene enganchado, pero **no son la nota**.

2. **El informe (`entregable.md`).** Acá va lo que evalúa la rúbrica: tu mapa de
   superficie, la clasificación de cada servicio y tu razonamiento. Las flags
   demuestran que *pudiste*; el informe demuestra que *entendiste*.

---

## Parte 1 · TEORÍA — qué es reconocer

### 1.1 Pasivo vs. activo

| | **Pasivo** | **Activo** |
|---|---|---|
| Qué es | Recolectar info **sin tocar** el objetivo | **Interactuar** con el objetivo |
| Ejemplos | Google dorks, `whois`, DNS público, certificados, LinkedIn | `nmap`, `curl` al server, banner grabbing |
| Huella | Casi indetectable | Queda en los logs del objetivo |
| Riesgo legal | Bajo (info pública) | Alto (requiere autorización) |

En un engagement real empezás **pasivo** (no alertás a nadie) y recién con
autorización pasás a **activo**. En este lab, como PhantomCorp es tuyo, vamos
directo al recon activo — pero tenés que entender que **el orden importa**.

### 1.2 Dónde encaja en la cadena de ataque

```
[ RECON ] → Armado → Entrega → Explotación → Instalación → C2 → Acciones
    ▲
    estás acá. Todo lo demás depende de qué tan bien hagas esto.
```

### 1.3 El bucle mental del recon

Recon no es "correr nmap". Es un **bucle**:

```
   descubrir  →  identificar  →  clasificar  →  priorizar
       (¿qué   )   (¿qué es    )   (¿es un      )   (¿por dónde
        hay?   )    exactamente?)   problema?   )    empiezo?  )
```

`nmap` te resuelve el "descubrir". El "identificar", "clasificar" y "priorizar"
los ponés **vos**. Ahí está el laburo intelectual, y ahí evalúa la rúbrica.

---

## Parte 2 · EJEMPLOS — cómo se ve en la vida real

**Ejemplo A — El puerto que nadie recordaba.** Una empresa expone el 22 (SSH) y
el 443 (HTTPS), todo prolijo. Pero un `nmap -p-` encuentra el **8081** con un
Jenkins viejo sin auth que un dev levantó "un ratito" en 2019. Ese Jenkins
ejecuta comandos en el server. **El hallazgo no estaba en los puertos obvios: estaba en el barrido completo.** Por eso nunca se escanean solo los 1000 puertos default.

**Ejemplo B — La versión que canta.** Un banner devuelve
`Apache/2.4.49`. Esa versión concreta tiene el **CVE-2021-41773** (path
traversal → RCE). El servicio "andaba bien"; el problema era la **versión**. Sin
fingerprinting de versión, ese hallazgo no existe.

**Ejemplo C — El `robots.txt` bocón.** Un `robots.txt` dice
`Disallow: /backup-db`. El archivo pensado para *ocultar* rutas a Google es un
**mapa de rutas sensibles** para el atacante. La info "pública" filtra estructura
interna.

Los tres casos son la misma lección: **lo grave casi nunca está a la vista.**
Está en el puerto alto, en la versión exacta, en el detalle que el defensor pasó
por alto. En PhantomCorp vas a encontrar los tres patrones.

---

## Parte 3 · TOOLS — el arsenal, una por una

Para cada herramienta: **qué hace**, **anatomía del comando**, **cómo leer la
salida** y **cómo clasificar** lo que encontrás. Practicá cada una contra
`phantomcorp` a medida que leés.

### 3.1 `nmap` — el mapeador

Descubre hosts, puertos abiertos, servicios y versiones. Es LA herramienta de
recon activo.

```bash
nmap -Pn phantomcorp              # escaneo básico (1000 puertos más comunes)
nmap -Pn -p- phantomcorp          # TODOS los 65535 puertos (¡acá aparecen los ocultos!)
nmap -Pn -sV phantomcorp          # detecta VERSIÓN de cada servicio
nmap -Pn -sV -p- phantomcorp      # el combo: todos los puertos + versiones
```

**Anatomía:**

| Flag | Qué hace | Por qué importa |
|---|---|---|
| `-Pn` | No hace ping previo, asume que el host está vivo | Muchos hosts bloquean ping; sin `-Pn` nmap los da por "caídos" |
| `-p-` | Escanea del puerto 1 al 65535 | El default son 1000. **Los servicios interesantes se esconden arriba** |
| `-sV` | Sondea cada puerto para identificar producto y versión | Sin esto tenés "abierto"; con esto tenés "ProFTPD 1.3.5" |
| `-sS` | SYN scan (sigiloso, no completa la conexión) | Más rápido y discreto. Necesita privilegios (por eso el `NET_RAW`) |

**Cómo leer la salida:**

```
PORT      STATE  SERVICE   VERSION
21/tcp    open   ftp       ProFTPD 1.3.5
80/tcp    open   http      PhantomServer 2.4.1
```

- `STATE open` = hay algo escuchando. `filtered` = un firewall te tapa la vista.
- La columna `SERVICE` es el **adivine** de nmap por número de puerto. La columna
  `VERSION` (solo con `-sV`) es lo que **de verdad** respondió. **Confiá en
  VERSION, no en SERVICE.**

**Cómo clasificar:** con producto+versión en mano, buscá en fuentes de CVE
(NVD, `searchsploit` offline, Exploit-DB). "ProFTPD 1.3.5" → CVE-2015-3306.
Anotá el CVE, su score CVSS y qué habilita.

### 3.2 `ncat` / `nc` — el navaja suiza de TCP

Abre una conexión TCP cruda a un puerto y te muestra **exactamente** lo que el
servicio dice al conectarse. Eso es **banner grabbing**.

```bash
ncat phantomcorp 21               # conectate al FTP y mirá su saludo
ncat -w2 phantomcorp 31337 </dev/null   # -w2 = timeout 2s; útil en puertos raros
```

**Cómo leer la salida:** el servicio te "saluda" con un banner. Ese texto suele
delatar producto, versión y a veces hasta información que no debería estar ahí.

### 3.3 `curl` — interrogar HTTP

Habla HTTP. Para recon web te importan los **headers** (metadata del server) y
rutas conocidas.

```bash
curl -I phantomcorp                 # -I = solo HEADERS (no el cuerpo)
curl -s phantomcorp/robots.txt      # rutas que el server "pide no indexar"
curl -sv phantomcorp 2>&1 | head    # -v = verbose, ves toda la conversación
```

**Cómo leer la salida:** headers como `Server:`, `X-Powered-By:` filtran qué
software y versión corre. Un `robots.txt` te lista rutas — muchas veces las
*sensibles*, porque el que lo escribió quería esconderlas.

### 3.4 `whois` y `dig` — recon pasivo de dominios

En un engagement real, **antes** de tocar nada:

```bash
whois phantomcorp.com             # dueño, contactos, fechas del dominio
dig phantomcorp.com ANY           # registros DNS: A, MX, TXT, NS...
dig +short TXT phantomcorp.com     # los TXT filtran SPF, verificaciones, a veces secretos
```

> En este lab `phantomcorp` es un host interno sin DNS público, así que `whois`
> y `dig` los practicás contra dominios reales de tu elección (los tuyos, o
> `scanme.nmap.org`, que Nmap habilita explícitamente para pruebas). El
> **concepto** de recon pasivo se evalúa igual en el informe.

---

## Parte 4 · PRÁCTICA — cazá las 5 flags en PhantomCorp

Ahora sí. Consola del atacante (`make shell`) y a operar. Cada reto entrena una
técnica de la Parte 3. **No te doy el comando exacto**: te doy la pista y la
técnica. Descubrir el "cómo" es parte del ejercicio.

| Reto | Técnica | Pista |
|---|---|---|
| **R1** | Barrido completo de puertos | El servicio más interesante **no** está en los 1000 puertos default. ¿Con qué flag ves los 65535? Conectate a ese puerto alto. |
| **R2** | Banner grabbing FTP | El puerto 21 te saluda apenas te conectás. Leé **todo** lo que dice. |
| **R3** | Análisis de headers HTTP | El server web filtra algo en sus **cabeceras**. `curl -I` y mirá con atención. |
| **R4** | Enumeración de rutas | ¿Qué rutas te pide el server que *no* mires? Seguí esa pista y entrá. |
| **R5** | Servicio dev expuesto | Hay un HTTP en un puerto que no es el 80. Tiene un endpoint de estado que no debería estar en producción. |

Entregá cada una:

```bash
./ctf submit 05 R1 'FLAG{...}'
```

Cuando tengas las 5, `./ctf status 05` te lo celebra. Pero no terminaste: falta
lo que vale la nota.

---

## Parte 5 · CLASIFICACIÓN — el mapa de superficie (esto es la nota)

En `entregable.md` construí el **mapa de superficie de ataque** de PhantomCorp.
Una fila por servicio descubierto:

| Puerto | Servicio | Versión (evidencia) | ¿Cómo lo identificaste? | CVE relevante | CVSS | Criticidad | Justificación |
|---|---|---|---|---|---|---|---|
| 21 | FTP | ProFTPD 1.3.5 | banner grabbing con ncat | *completar* | *completar* | *completar* | *completar* |
| ... | | | | | | | |

Reglas de esta tabla (léelas, son las de la rúbrica):

- **"Versión (evidencia)"**: no vale "creo que es FTP". Pegá el banner o la línea
  de nmap que lo prueba.
- **"Criticidad"**: fundamentá contra **este** caso, no en general. Un servicio
  dev con `debug:true` expuesto no es crítico "porque sí": explicá qué habilita.
- Si un puerto **no** tenés cómo clasificarlo, decilo. **"No pude determinar la
  versión" es una respuesta honesta y válida.** Inventar un CVE es causal de
  rechazo.

### Preguntas de análisis (en `entregable.md`)

1. **P1.** ¿Por qué `nmap -p-` encontró un servicio que el escaneo default se
   perdió? ¿Qué lección operativa sacás para tus próximos recon?
2. **P2.** El servicio del puerto 8080 no estaba pensado para producción.
   ¿Qué evidencia concreta te lo dice? ¿Por qué es un problema aunque "no tenga
   una vulnerabilidad conocida"?
3. **P3.** El `robots.txt` te llevó a una ruta oculta. Explicá la ironía de
   seguridad: ¿para qué se creó `robots.txt` y por qué termina ayudando al
   atacante?
4. **P4.** Diferenciá con tus palabras, usando algo que hiciste en este lab,
   recon **pasivo** de **activo**. ¿Cuál de tus acciones habría quedado en los
   logs de PhantomCorp?
5. **P5.** Sos el **defensor** de PhantomCorp. Elegí **dos** hallazgos y proponé,
   para cada uno, una medida concreta que reduzca la superficie de ataque.

---

## Ampliación opcional — entendé nmap por dentro

nmap es magia hasta que sabés qué hace. En `src/escaner.py` hay un **mini-escáner
de puertos** a medio hacer: implementás dos funciones y tenés tu propio "nmap
connect" en Python puro (solo biblioteca estándar). No cuenta para la nota, pero
el que lo hace mira la salida de nmap con otros ojos —"open", "closed",
"filtered"— porque los produjo con sus manos.

```bash
# desde la consola del atacante, con el lab levantado:
python3 labs/lab05-reconocimiento/src/escaner.py phantomcorp --puertos 1-1000
```

El recon del informe se sigue haciendo con nmap. Esto es para **entender**.

---

## Qué se entrega

En `entregas/lab05/grupoXX/`:

- `informe.md` — a partir de `docs/entregable.md`: mapa de superficie + las 5
  preguntas de análisis + captura de `./ctf status 05` con las 5 flags.
- `research.md` — a partir de `docs/research.md`: mini-investigación sobre **una**
  de las técnicas o CVEs que encontraste.
- Evidencia: guardá las salidas de tus comandos en `/loot` (dentro de la consola)
  — se sincroniza con `.loot/` de tu repo. Adjuntá lo relevante.

Fecha límite: antes del inicio del Lab 06.

La rúbrica completa está en [`docs/rubrica.md`](docs/rubrica.md). **Leela antes
de empezar.**

---

## Uso responsable

Todo lo de este lab se practica **exclusivamente** contra los contenedores que
provee la cátedra, dentro de tu máquina. Ejecutar reconocimiento activo
(`nmap`, banner grabbing, etc.) contra sistemas de terceros sin autorización
escrita constituye delito en Argentina (Ley 26.388). El recon *parece* inofensivo
—"solo miré"— pero el escaneo activo es acceso no autorizado. No lo hagas.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
