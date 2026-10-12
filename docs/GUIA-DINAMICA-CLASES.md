# Guía dinámica de clases — CyberLab UTN

> No es un temario aburrido. Es el mapa de la aventura. Cada clase tiene un
> **gancho**, la **idea** sin vueltas, un **ejemplo que hace clic**, las **tools**
> y un **dato hacker** para que no te despegues. Leela como si te la contara
> alguien en la mesa del bar, no como un PDF.

**Cómo leer cada clase:**
`🎣 gancho` · `💡 la idea` · `⚡ por qué te importa` · `🎬 ejemplo` · `🔧 tools` · `🎯 lo que hacés` · `💀 dato hacker`

El curso va de **entender** (01-04) a **atacar a mano** (05-08), a **automatizar
con agentes** (09), a **defender** (10), y cierra con un **engagement completo**
y la **forensia** de todo lo que pasó (11).

---

# BLOQUE 1 · FUNDAMENTOS (código)

*Acá no hackeás nada todavía. Acá entendés QUÉ protegés y CÓMO se hace bien.
Porque el que ataca sin entender los fundamentos, dispara al aire.*

---

## Clase 01 — Introducción: la tríada CIA · `código`

🎣 **El gancho:** Te roban la base de datos de clientes de una empresa. Grave,
¿no? Ahora: ¿QUÉ propiedad de la información se rompió exactamente? Si no sabés
responder eso con precisión, no sabés seguridad. Sabés miedo.

💡 **La idea:** Toda la seguridad se para sobre tres patas —
**C**onfidencialidad (que solo lo vea quien debe), **I**ntegridad (que no lo
alteren sin que te enteres), **D**isponibilidad (que esté cuando lo necesitás).
Es el ABC. El que dice "esto es seguro" sin decir *contra qué* propiedad, está
vendiendo humo.

⚡ **Por qué te importa:** El error más común del principiante es marcar "se violó
todo" porque el incidente fue grave. NO. La gravedad no es una propiedad de la
tríada. Si decís que se violó la integridad, tenés que mostrar QUÉ dato se
alteró. Si no podés, la respuesta es "no". Así de fácil, así de riguroso.

🎬 **Ejemplo que hace clic:** WannaCry (2017) cifró miles de hospitales. ¿Rompió
confidencialidad? No — no se llevó los datos, los ENCRIPTÓ. Rompió
**disponibilidad**. Un ransomware ataca la D, no la C. ¿Ves cómo cambia todo
cuando lo nombrás bien?

🔧 **Tools:** Python + `hashlib` (biblioteca estándar). El control técnico más
básico de integridad: un manifiesto de hashes que te dice si un archivo cambió,
aunque sea **un solo byte**.

🎯 **Lo que hacés:** Analizás un incidente real con la lente CIA, e implementás un
verificador de integridad. Vas a hacer que detecte un cambio de UN byte.

💀 **Dato hacker:** El `diff` de un byte que cambia el hash SHA-256 por completo se
llama *efecto avalancha*, y es lo que hace que un hash sirva. Cambiás una coma y
el digest es irreconocible. Magia matemática pura.

---

## Clase 02 — Criptografía · `código`

🎣 **El gancho:** ¿Sabés cuál es el 99% de las fallas de cripto del mundo real?
No es que rompieron AES. Es que alguien lo **usó mal**. El algoritmo es público y
sólido; el problema sos vos.

💡 **La idea:** Cripto no es "poner una contraseña". Es garantizar
confidencialidad, integridad y autenticidad con matemática. Y hay una regla de
oro — **Kerckhoffs**: el sistema tiene que ser seguro AUNQUE el atacante conozca
todo, menos la clave. Si tu seguridad depende de que nadie sepa cómo funciona, no
tenés seguridad: tenés un secreto que se va a filtrar.

⚡ **Por qué te importa:** Vas a ver la diferencia entre cifrar (confidencialidad),
hashear (integridad) y un MAC (autenticidad). Tres cosas distintas que todo el
mundo mezcla. El que las mezcla, la caga.

🎬 **Ejemplo que hace clic:** Adobe, 2013. Guardaron 150 millones de contraseñas
cifradas con ECB en vez de hashearlas. ¿El resultado? El famoso "pingüino": el
patrón se veía A TRAVÉS del cifrado. Contraseñas iguales daban cifrados iguales.
Se dedujeron miles. Un modo de operación mal elegido y listo.

🔧 **Tools:** Python `hashlib`, `hmac`, `secrets`. Vas a **romper** un cifrado
clásico por análisis de frecuencia (fuerza bruta trivial) y a construir un MAC
con HMAC hecho bien.

🎯 **Lo que hacés:** Rompés un XOR de clave corta y leés el mensaje oculto. Después
entendés por qué `sha256(clave || mensaje)` es una MAC INSEGURA (ataque de
length-extension) y por qué HMAC no lo es.

💀 **Dato hacker:** Comparar dos MACs con `==` común filtra información por el
TIEMPO que tarda la comparación. Un atacante mide microsegundos y adivina el
token byte por byte. Por eso se compara en tiempo constante. La seguridad está en
los detalles que no se ven.

---

## Clase 03 — Autenticación y control de acceso · `código`

🎣 **El gancho:** "¿Sos quien decís ser?" Esa pregunta es la puerta de TODO. Si se
rompe, ningún otro control importa. Y se rompe casi siempre por una cosa:
implementación de porquería.

💡 **La idea:** Autenticación (¿quién sos?) es distinto de autorización (¿qué
podés hacer?). Y una contraseña NUNCA se guarda en claro, ni con un `sha256`
pelado. Se guarda con **salt** (para que dos claves iguales den hashes distintos)
y muchas **iteraciones** (para que crackearla cueste una eternidad).

⚡ **Por qué te importa:** El segundo factor (2FA) es lo que te salva cuando te
roban la contraseña. Vas a implementar TOTP — el de Google Authenticator — desde
cero. Cuando entiendas cómo funcionan esos 6 dígitos que cambian cada 30
segundos, no los vas a ver igual nunca más.

🎬 **Ejemplo que hace clic:** LinkedIn, 2012. 6,5 millones de contraseñas en SHA-1
**sin salt**. Con salt, cada una habría que crackearla por separado. Sin salt, una
tabla precalculada las reventó todas juntas. El salt no es un detalle: es la
diferencia entre "difícil" e "imposible".

🔧 **Tools:** `hashlib.pbkdf2_hmac`, `hmac`, `secrets`. Almacenamiento de
contraseñas correcto + TOTP (RFC 6238).

🎯 **Lo que hacés:** Guardás contraseñas con PBKDF2 y salt, verificás en tiempo
constante, y generás códigos TOTP que vas a validar contra el vector oficial del
RFC (`94287082` — si no te da eso, algo está mal).

💀 **Dato hacker:** El TOTP se basa en el reloj. Por eso si tu teléfono tiene la
hora corrida, los códigos no funcionan. El "secreto" que escaneás del QR es la
semilla; el resto es HMAC del tiempo dividido en ventanas de 30 segundos. Pura
biblioteca estándar.

---

## Clase 04 — Marcos normativos y gestión del riesgo · `código`

🎣 **El gancho:** "Poné un firewall." Eso NO es una decisión de seguridad. Una
decisión es: "este control evita $15.000 al año y cuesta $8.000, entonces
conviene". ¿La diferencia? Números.

💡 **La idea:** La seguridad se **gestiona**. No existe "seguro"; existe "riesgo
aceptable, medido y justificado". Y para eso hay marcos (ISO 27001, NIST CSF) y
matemática de riesgo: **ALE** = pérdida por evento × frecuencia anual. Con eso
priorizás lo que IMPORTA, no lo que te da miedo.

⚡ **Por qué te importa:** El que parchea por corazonada gasta plata en lo
equivocado. El que cuantifica, invierte donde duele. Y hay CUATRO respuestas al
riesgo — mitigar, transferir, aceptar, evitar — no solo "arreglarlo".

🎬 **Ejemplo que hace clic:** ¿Un meteorito destruye tu datacenter? Riesgo real,
pero probabilidad ínfima × impacto altísimo = ALE bajo. Lo **aceptás**. ¿Phishing
a tus empleados? Probabilidad alta × impacto medio = ALE alto. Lo **mitigás** con
capacitación y 2FA. Los números te dicen dónde poner la plata.

🔧 **Tools:** Python (stdlib) para una calculadora de riesgo cuantitativo; ISO
27001 / NIST CSF como marcos de referencia.

🎯 **Lo que hacés:** Aplicás un marco a un escenario real de PhantomCorp, y
calculás ALE y ROI de controles para priorizar con números, no con intuición.

💀 **Dato hacker:** El "riesgo cero" no existe y buscarlo te funde. Las empresas
serias no eliminan el riesgo: lo llevan a un nivel aceptable y lo **transfieren**
(seguro de ciberataque) o lo **aceptan** con los ojos abiertos. Gestionar > temer.

---
# BLOQUE 2 · OFENSIVA A MANO (Docker + flags)

*Acá te ensuciás las manos. Herramientas reales contra PhantomCorp. Todo manual,
tool por tool, entendiendo cada salida. Porque si no sabés lo que hace nmap a
mano, ¿cómo vas a dirigir un agente que lo automatiza? No podés.*

---

## Clase 05 — Reconocimiento · `ofensivo` 🔴

🎣 **El gancho:** Antes de entrar a robar una casa, el ladrón la mira una semana:
qué puertas hay, cuáles cierran mal, cuándo no hay nadie. Eso es recon. Y es el
80% del trabajo. El que escanea a lo bruto y no entiende lo que ve, después
dispara exploits al azar.

💡 **La idea:** Un puerto abierto NO es un hallazgo. Un puerto **identificado y
clasificado** — "el 21 corre ProFTPD 1.3.5, que tiene el CVE-2015-3306 de RCE" —
ESO es un hallazgo. Reconocer es un bucle: descubrir → identificar → clasificar →
priorizar.

⚡ **Por qué te importa:** Lo grave casi nunca está a la vista. Está en el puerto
alto que nadie recuerda, en la versión exacta, en el detalle que el defensor pasó
por alto. Por eso NUNCA se escanean solo los 1000 puertos default.

🎬 **Ejemplo que hace clic:** Una empresa expone el 22 y el 443, todo prolijo.
Pero un `nmap -p-` encuentra el 8081 con un Jenkins viejo sin auth que un dev
levantó "un ratito" en 2019. Ese Jenkins ejecuta comandos en el server. El
hallazgo estaba en el barrido COMPLETO, no en los puertos obvios.

🔧 **Tools:** `nmap` (el mapeador), `ncat` (banner grabbing), `curl` (headers y
robots.txt), `whois`/`dig` (recon pasivo). Todas adentro de la consola atacante:
tu máquina queda limpia.

🎯 **Lo que hacés:** Mapeás la superficie de PhantomCorp, hacés fingerprinting de
versiones, clasificás contra CVE/CVSS. 5 flags escondidas en los servicios.

💀 **Dato hacker:** El puerto 31337 es "eleet" (leet = elite en jerga hacker).
Cuando ves un servicio ahí, alguien quiso hacerse el vivo. Y casi siempre es un
backdoor o una consola de mantenimiento olvidada. Los puertos altos cuentan
historias.

---

## Clase 06 — Enumeración de servicios · `ofensivo` 🔴

🎣 **El gancho:** El recon te dijo "hay un servidor web". ¿Y ahora qué? Un
servidor web no es una cosa: son DECENAS de rutas, archivos, endpoints y métodos,
la mayoría no listados en ningún lado. Enumerar es sacarle todo lo que esconde.

💡 **La idea:** Todo servicio esconde más de lo que muestra. El index dice
"bienvenido"; vos preguntás por lo que NO está en el index: los directorios que
nadie linkeó, los backups que quedaron, el `.git` que se olvidaron, los métodos
que nadie deshabilitó.

⚡ **Por qué te importa:** Es la diferencia entre "hay un web server" y "hay un web
server con `/backup` accesible, el código filtrado por un `.git`, una API que
lista usuarios y `PUT` habilitado". Lo segundo es un plan de ataque.

🎬 **Ejemplo que hace clic:** Un `/.git/` accesible por HTTP te deja reconstruir el
CÓDIGO FUENTE COMPLETO de la app, con su historia y a veces credenciales
commiteadas por error. Un directorio de más = la aplicación entera en tus manos.

🔧 **Tools:** `dirb`/`gobuster` (fuerza bruta de directorios), `whatweb`
(fingerprinting), `wfuzz` (fuzzing), `nmap` con scripts NSE. `curl` para afinar.

🎯 **Lo que hacés:** Enumerás la intranet de PhantomCorp: directorios ocultos,
`.git` expuesto, métodos HTTP peligrosos, una API de usuarios, y el CMS por
fingerprint. 5 flags.

💀 **Dato hacker:** El `robots.txt`, el archivo que le pedís a Google que NO
indexe, es un MAPA de las rutas sensibles para el atacante. El que lo escribió
quería esconderlas... y te las listó todas juntas. La ironía de seguridad más
vieja del libro.

---

## Clase 07 — Explotación · `ofensivo` 🔴🔴

🎣 **El gancho:** ¿Cómo pasás de "veo el login" a "estoy adentro como admin"? No
con suerte. Con entender una sola cosa: el software mezcla, en el mismo string,
DATOS (lo que escribís) y CÓDIGO (la consulta, el comando). Cuando esa frontera
se rompe, tu dato se EJECUTA como código.

💡 **La idea:** Toda entrada del usuario es una mentira potencial. SQL injection,
command injection, path traversal, IDOR — son variantes de lo mismo: confiar en
el input. En OWASP Top 10 es A03 (Injection) y A01 (Broken Access Control), las
dos categorías más explotadas del planeta.

⚡ **Por qué te importa:** Vas a hacerlo A MANO primero. sqlmap es maravilloso,
pero si no sabés qué inyecta y por qué, el día que la app tenga una defensa rara,
el que entiende pasa y el que solo aprieta botones, no.

🎬 **Ejemplo que hace clic:** El login arma `SELECT * FROM users WHERE user='X'`.
Escribís de usuario `admin' --`. La query queda `...WHERE user='admin' --'...`. El
`--` comenta el resto: la verificación de contraseña DESAPARECIÓ. Entraste como
admin sin saber su clave. Tu dato se volvió código.

🔧 **Tools:** `curl` (tu bisturí), `sqlmap` (automatización — después de entender).
Backend sqlite REAL, así que la inyección es auténtica.

🎯 **Lo que hacés:** Bypass de login por SQLi, extracción con UNION, inyección de
comandos (RCE), path traversal e IDOR. 5 flags, cada una una vulnerabilidad real.

💀 **Dato hacker:** La brecha de TalkTalk (2015) fue UNA SQL injection en una
página web: 157.000 clientes expuestos, multa récord. Una consulta concatenada.
La vulnerabilidad más vieja del top 10 sigue siendo la que más plata cuesta.

---

## Clase 08 — Post-explotación y automatización · `ofensivo` 🔴🔴

🎣 **El gancho:** Lograste tu RCE. Estás adentro. ¿Y ahora? Un atacante real NO se
queda ahí con un shell sin privilegios. Reconoce el terreno interno, roba lo que
sirve, se hace root, salta a otros equipos, y automatiza. Un shell es el
principio, no el final.

💡 **La idea:** La explotación te da un pie adentro. La post-explotación convierte
ese pie en control real: escalada de privilegios, movimiento lateral (pivoting),
loot de credenciales. Y lo que se hace más de una vez, se AUTOMATIZA — el puente
directo hacia los agentes.

⚡ **Por qué te importa:** El pivoting es la joya. Las redes internas están
segmentadas: el server web ve la base de datos interna, pero vos desde Internet
no. Comprometés el web, y lo usás de TRAMPOLÍN para alcanzar la red que antes no
existía para vos.

🎬 **Ejemplo que hace clic:** `find / -perm -4000` lista binarios SUID (corren con
permisos de su dueño, root). Si aparece una copia de `bash` con SUID, corrés
`bash -p` y sos root en un segundo. GTFOBins te da el truco exacto. Una de las
escaladas más comunes del mundo real.

🔧 **Tools:** `find` (SUID), `curl` (pivot), scripting en bash/python
(automatización). Dos hosts en redes SEGMENTADAS — pivoting de verdad.

🎯 **Lo que hacés:** Caés como usuario `operador`, reconocés el host, robás
credenciales, escalás a root por SUID, pivoteás a la DB interna, y escribís un
script que automatiza lo tedioso. 5 fases.

💀 **Dato hacker:** En muchas brechas gigantes, el equipo comprometido INICIALMENTE
era irrelevante — un server web público. El daño vino de usarlo para saltar a la
red interna: bases de datos, controladores de dominio, lo que desde afuera era
invisible. El pivot es el que abre el reino.

---
# BLOQUE 3 · AGENTES Y DEFENSA

*Recién ACÁ entra la IA. Y no antes, ¿sabés por qué? Porque no podés dirigir un
agente que hace lo que vos no sabés hacer. Primero las manos en el teclado.*

---

## Clase 09 — Agentes de pentest · `ofensivo` 🤖

🎣 **El gancho:** Un "agente de IA" suena a magia. No lo es. Es un LOOP de cuatro
pasos que podés dibujar en una servilleta. El día que lo entendés, dejás de tenerle
misterio y empezás a dirigirlo.

💡 **La idea:** El loop de tool-use: (1) el LLM decide qué herramienta correr, (2)
la ejecutás con GUARDRAILS, (3) le devolvés el resultado, (4) repite hasta
terminar. El LLM aporta el razonamiento; tu código, las manos (tools) y los
límites. Eso es todo.

⚡ **Por qué te importa:** Un agente ofensivo sin guardrails es un ARMA. Un agente
que puede correr nmap es útil; uno que puede correr nmap contra CUALQUIER IP es
peligroso. La diferencia son diez líneas de validación de alcance. Escribilas bien.

🎬 **Ejemplo que hace clic:** El LLM ve en un resultado "pedí el token en
/api/token", lo pide, y lo usa en el siguiente paso. Ese ENCADENAMIENTO autónomo
es lo que un script fijo no hace. Pero también puede "alucinar" una vulnerabilidad
que no existe, con lujo de detalle. Si no sabés validar (clases 05-08), te la comés.

🔧 **Tools:** Cliente LLM agnóstico — `Claude` · `OpenAI` · `mock` offline (corre
sin API key). Tools con guardrail de alcance. Tu propio agente a completar.

🎯 **Lo que hacés:** Construís y dirigís un agente que orquesta recon y enumeración
sobre PhantomCorp, con guardrails. Lo auditás: ¿dónde acierta? ¿dónde se equivoca?

💀 **Dato hacker:** El error clásico de un agente ofensivo real: "decide" escanear
un host que vio mencionado en un resultado — un dominio de terceros. Sin guardrail,
lo hace. Con guardrail, lo intenta y se lo BLOQUEA. El humano define los límites;
el agente opera adentro. Siempre.

---

## Clase 10 — Detección y evasión (Blue vs Red) · `ofensivo` 🔵

🎣 **El gancho:** Durante cinco clases fuiste el atacante. Ahora date vuelta: del
OTRO lado siempre hubo alguien mirando. Todo lo que hiciste dejó huella. Un
`nmap -p-` son miles de conexiones. El defensor las vio.

💡 **La idea:** Un IDS/WAF detecta ataques por FIRMAS: patrones conocidos (la
User-Agent de sqlmap, un `../`, un `UNION SELECT`). Es poderoso pero frágil:
reconoce solo lo que ya conoce. El que entiende la firma, la esquiva.

⚡ **Por qué te importa:** Un buen pentester piensa como defensor, y un buen
defensor piensa como atacante. Son el MISMO conocimiento visto de los dos lados.
El que solo sabe atacar, es medio profesional.

🎬 **Ejemplo que hace clic:** El WAF detecta `UNION SELECT` con un espacio. El
atacante escribe `UNION/**/SELECT` — un comentario SQL en vez del espacio. Mismo
efecto, otra cadena, firma EVADIDA. Y lo que ninguna firma detecta, solo lo
encuentra alguien LEYENDO los logs.

🔧 **Tools:** Un target tipo IDS/SOC. `curl` para disparar y evadir firmas,
análisis de logs para cazar la intrusión escondida en el ruido.

🎯 **Lo que hacés:** Provocás una detección, entendés el ruleset, EVADÍS una firma,
y encontrás una intrusión real escondida entre 120 líneas de tráfico normal. 5
retos, cara Red y cara Blue.

💀 **Dato hacker:** En casi todas las brechas grandes, la evidencia del ataque
estaba en los logs DESDE EL DÍA UNO. Nadie la miró hasta meses después. La
herramienta no falló; faltó el analista. La detección automática y la humana se
complementan — no se reemplazan.

---

# BLOQUE 4 · INTEGRACIÓN Y FORENSIA

---

## ★ Práctico Final — Engagement integrador · `ofensivo` 🏆

🎣 **El gancho:** Se acabaron las guías paso a paso. Te dan un objetivo y un
alcance, y tenés que auditarlo DE PUNTA A PUNTA con todo lo que aprendiste. Como
un pentest de verdad.

💡 **La idea:** Un solo objetivo que exige encadenar TODO: recon → foothold por
SQLi → loot de un token → RCE hasta los datos de clientes. Cuatro hitos
encadenados, cada uno habilita el siguiente. Caja negra, reglas de engagement.

⚡ **Por qué te importa:** La técnica se demuestra rompiendo. El VALOR PROFESIONAL
se demuestra comunicando lo que rompiste de forma que alguien lo pueda arreglar.
Por eso el entregable estrella es un **informe de pentest profesional**: resumen
ejecutivo (para el que decide) + hallazgos con CVSS, evidencia y remediación (para
el que arregla).

🎯 **Lo que hacés:** El engagement completo + el informe. Sin hand-holding: para
eso hiciste los diez labs.

💀 **Dato hacker:** Un pentest sin informe no vale NADA. Podés ser un crack
rompiendo, pero si no sabés escribir el informe, no te contratan dos veces. La
diferencia entre un pentester y un delincuente es una sola: la autorización, el
alcance y la ética.

---

## Clase 11 — Forensia del pentest (DFIR) · `defensivo` 🔬

🎣 **El gancho:** El atacante entró, hizo su desastre y se fue. Ahora sos VOS el
que llega después: ¿qué tocó? ¿por dónde entró? ¿qué se llevó? ¿sigue adentro?
Esto es lo que hace un forense digital, y es tan adrenalínico como el ataque.

💡 **La idea:** Forensia (DFIR — Digital Forensics & Incident Response) es
reconstruir lo que pasó a partir de la evidencia que quedó: la memoria RAM, la
imagen del disco, los logs. Con una regla sagrada por encima de todo: la **cadena
de custodia**. Si tocás la evidencia mal, no sirve ni en la investigación ni en un
juicio.

⚡ **Por qué te importa:** Acá se cierra el círculo del curso. En la clase 10
aprendiste a NO dejar rastro (evasión); en la 11 aprendés a ENCONTRAR el rastro
que el atacante dejó igual. El cazador y la presa, las dos miradas.

🎬 **Ejemplo que hace clic:** El atacante borró sus comandos del historial. Pero
en la MEMORIA RAM todavía está el proceso corriendo, la conexión de red abierta,
el comando en el buffer. La RAM es la escena del crimen fresca — por eso lo
primero que se captura, antes de apagar nada, es la memoria.

🔧 **Tools:** `Volatility` (memoria RAM), análisis de imagen de disco, `grep`/
timeline de logs, hashing para la cadena de custodia. *(Lo estamos construyendo.)*

🎯 **Lo que vas a hacer:** Analizar un volcado de RAM y una imagen de disco de un
PhantomCorp comprometido, reconstruir la línea de tiempo del ataque, extraer los
indicadores de compromiso (IOCs), y documentar todo con cadena de custodia
verificable.

💀 **Dato hacker:** El primer principio de la forense es el de Locard: "todo
contacto deja un rastro". El atacante SIEMPRE deja algo — un timestamp, un archivo
temporal, una conexión en la memoria. El trabajo del forense es encontrarlo antes
de que se pierda. Y la memoria RAM se pierde apenas apagás la máquina. El reloj
corre.

---

> **Cómo sigue esto:** cada clase tiene su lab con guía completa en
> `labs/labNN-*/README.md`, sus ejercicios (flags) y su rúbrica. Esta guía es el
> mapa; los labs son el territorio. **Ponete las pilas.**
