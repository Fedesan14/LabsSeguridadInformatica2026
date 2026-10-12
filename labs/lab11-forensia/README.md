# Laboratorio 11 — Forensia del pentest (DFIR)

**Unidad 11** · Forensia digital y respuesta a incidentes
**Modalidad:** grupos de 4 a 5 · **Entorno:** archivos de evidencia (sin Docker)
**Entrega:** fork + Pull Request en `entregas/lab11/grupoXX/`

> Cierra el círculo del curso. En las clases 05-08 aprendiste a **atacar**; en la
> 10, a **no dejar rastro**. Ahora te das vuelta del todo: sos el **forense** que
> llega después del incidente a reconstruir QUÉ pasó. El cazador se vuelve
> investigador.

---

## El escenario

PhantomCorp fue comprometido. El servidor `phantomcorp-web` (10.0.0.5) cayó — la
misma cadena que vos ejecutaste en los labs anteriores: recon, SQLi, RCE, escalada,
exfiltración. El equipo de respuesta capturó la evidencia y te la pasa a vos.

Tu misión: **reconstruir el ataque** a partir de lo que quedó. ¿Por dónde entró?
¿Qué dejó? ¿Cómo escaló? ¿Qué se llevó? ¿Sigue adentro? Y todo con una regla
sagrada: **la cadena de custodia**. Si tocás la evidencia mal, no sirve.

El paquete de evidencia está en [`caso/`](caso/):

```
caso/
├── evidencia.sha256      # cadena de custodia (hashes de captura)
├── logs/                 # access.log · auth.log
├── disco/                # captura del filesystem (listado, webshell, passwd)
└── memoria/              # artefactos volátiles EXTRAÍDOS (pslist, netstat, ...)
```

> **Nota honesta sobre la memoria:** un volcado de RAM real pesa gigas y no entra
> en un repo. En producción usarías **Volatility 3** sobre el dump. Acá te damos
> los artefactos volátiles **ya extraídos** (lista de procesos, conexiones, open
> files, bash_history) para que te concentres en el ANÁLISIS, que es lo que
> importa. La técnica de extracción se explica; el análisis lo hacés vos.

---

## Por qué este laboratorio

La forense (DFIR — *Digital Forensics & Incident Response*) es reconstruir un
hecho a partir de la evidencia que dejó. Se apoya en dos principios:

- **Principio de Locard:** "todo contacto deja un rastro". El atacante SIEMPRE
  deja algo — un timestamp, un archivo temporal, una conexión en la memoria. Tu
  trabajo es encontrarlo antes de que se pierda.
- **Orden de volatilidad:** lo que se pierde primero, se captura primero. La RAM
  se pierde apenas apagás la máquina; el disco no. Por eso la memoria se captura
  ANTES de tocar nada.

Y por encima de todo: la **cadena de custodia**. Cada pieza de evidencia se
hashea al capturarla. Si el hash cambia, la evidencia fue alterada — y una
evidencia alterada no vale ni en la investigación ni en un juicio.

---

## Objetivos de aprendizaje

1. Aplicar la **cadena de custodia**: verificar integridad de la evidencia por
   hash y detectar manipulación.
2. **Analizar logs** para reconstruir la línea de tiempo de un ataque.
3. Interpretar **artefactos de disco** (archivos dropeados, persistencia,
   usuarios agregados).
4. Interpretar **artefactos de memoria** (procesos, conexiones de red,
   historial) para hallar el proceso malicioso y el C2.
5. Extraer **IOCs** (indicadores de compromiso) y documentarlos en un **informe
   forense**.

---

## Preparación

No hay Docker: la evidencia son archivos. Analizala con las tools que ya tenés
(shell, grep/rg, python). Desde la raíz del repo:

```bash
./ctf lab 11                 # muestra la guía (este lab no levanta contenedores)
cd labs/lab11-forensia/caso  # acá vive la evidencia
```

> **Regla de oro del forense:** trabajá sobre COPIAS, nunca sobre la evidencia
> original, y verificá su integridad antes de tocarla.

---

## Parte 1 · TEORÍA — la escena del crimen digital

Un incidente deja rastros en tres lugares, ordenados por **volatilidad** (de lo
que se pierde más rápido a lo que dura más):

```
  MEMORIA (RAM)      →   DISCO            →   LOGS
  se pierde al apagar    persiste             persisten (si no los borran)
  procesos, conexiones,  archivos, binarios,  quién hizo qué y cuándo
  claves en RAM          persistencia
```

El forense **correlaciona** los tres para armar UNA historia: el mismo atacante
que en el log hizo la SQLi, en el disco dejó el webshell, y en la memoria tiene la
conexión al C2 abierta. Tres fuentes, una verdad.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — La RAM no miente.** El atacante borró su `.bash_history` del disco
(`history -c`). Pero la sesión seguía viva: en la MEMORIA, el historial y el
proceso todavía estaban. Por eso lo primero que se captura es la RAM.

**Ejemplo B — La custodia atrapa al tramposo.** Alguien editó un log después de la
captura para borrar sus huellas. ¿Cómo se detecta? El hash del archivo ya no
coincide con el registrado en la captura. La matemática no perdona.

**Ejemplo C — El timestamp que ata todo.** Un archivo `shell.php` creado a las
02:19, un log de acceso a `/uploads/shell.php` a las 02:19, y una conexión de red
a las 02:19. Tres evidencias, un solo minuto: eso es correlación.

---

## Parte 3 · TOOLS Y TÉCNICAS

### 3.1 Cadena de custodia (hashing)

```bash
cd caso
shasum -a 256 -c evidencia.sha256      # verifica CADA archivo contra su hash de captura
```

Un `FAILED` significa que ese archivo **fue alterado** después de la captura. Eso
es un hallazgo en sí mismo.

### 3.2 Análisis de logs / timeline

```bash
rg '185.220.101.42' logs/access.log            # todo lo que hizo la IP sospechosa
rg -n 'POST|api/reporte|shell.php' logs/access.log   # los momentos clave
```

Ordená los eventos por hora y armá la **línea de tiempo** del ataque: recon →
enumeración → explotación → RCE → exfiltración.

### 3.3 Artefactos de disco

```bash
bat caso/disco/listado.txt                     # archivos creados durante el ataque
bat caso/disco/var/www/uploads/*.txt           # el webshell (defangeado)
bat caso/disco/etc/passwd.snippet              # ¿usuarios agregados?
```

### 3.4 Artefactos de memoria (extraídos)

```bash
bat caso/memoria/pslist.txt                    # procesos: ¿cuál no debería estar?
bat caso/memoria/netstat.txt                   # conexiones: ¿hay un C2 saliente?
bat caso/memoria/bash_history.txt              # los comandos del atacante
```

En producción esto sale de `volatility3 -f dump.raw linux.pslist` (y `.sockstat`,
`.bash`, `.lsof`). Acá ya están extraídos.

---

## Parte 4 · PRÁCTICA — reconstruí el ataque (los 5 hallazgos)

Cada reto es un hallazgo de la investigación. La flag es la evidencia concreta que
lo prueba.

| Reto | Hallazgo | Dónde buscar |
|---|---|---|
| **R1** | El **vector de entrada** | En `access.log`, encontrá la petición con la que el atacante logró ejecutar comandos (RCE). Dejó un marcador en un `echo`. Ojo: está **URL-encodeado**, decodificalo. |
| **R2** | El **webshell** | En el disco, en `uploads/`. El atacante lo dejó con un comentario. |
| **R3** | La **escalada** | En la memoria/historial, el comando con el que pasó a root por el binario SUID. |
| **R4** | El **C2 y la exfiltración** | En el `bash_history`, el comando que sube los datos robados al servidor externo. El marcador está en la URL. |
| **R5** | La **evidencia alterada** | Verificá la cadena de custodia. Un archivo fue tocado tras la captura: adentro está el marcador que recuperó el forense. |

```bash
./ctf submit 11 R1 'FLAG{...}'
./ctf status 11
```

---

## Parte 5 · EL INFORME FORENSE (esto es la nota)

En `informe.md` (a partir de [`docs/informe-forense.md`](docs/informe-forense.md)):

1. **Línea de tiempo** del ataque, minuto a minuto, con la evidencia de cada paso.
2. **IOCs** (indicadores de compromiso): IPs, archivos, usuarios, hashes,
   dominios/puertos del C2. Una tabla.
3. **Cadena de custodia:** qué verificaste y qué encontraste alterado.
4. **Alcance del daño:** ¿qué se llevó el atacante? ¿dejó persistencia? ¿sigue
   adentro?
5. **Recomendaciones de contención y erradicación:** qué haría el equipo de
   respuesta AHORA (cerrar el vector, matar el proceso, rotar credenciales,
   remover la persistencia).

### Preguntas de análisis

- **P1.** ¿Por qué la RAM se captura antes que el disco? Dá un ejemplo de este caso
  donde la memoria tenía algo que el disco ya no.
- **P2.** El R5: ¿cómo supiste que el archivo fue alterado? ¿Por qué eso invalida
  la evidencia si no se documenta?
- **P3.** Correlacioná tres artefactos (log + disco + memoria) que apunten al MISMO
  evento con el mismo timestamp.
- **P4.** El atacante corrió `history -c`. ¿Por qué igual pudiste recuperar sus
  comandos?
- **P5.** Cierre del curso: recorriste ataque, agentes, defensa y forensia.
  ¿Por qué un buen forense tiene que entender cómo ataca un pentester?

---

## Ampliación opcional — automatizá la timeline

Leer 20 líneas de log a ojo se puede. ¿200.000? Ni loco. Por eso el forense
scriptea. En `src/timeline.py` hay un esqueleto a medio hacer: completás dos
funciones y tenés tu propia herramienta de línea de tiempo que parsea el log,
filtra al atacante y etiqueta cada evento por fase.

```bash
cd labs/lab11-forensia/src
python3 timeline.py ../caso/logs/access.log --ip 185.220.101.42
```

No cuenta para las flags, pero el que lo hace reconstruye el ataque en segundos
en vez de a mano. Esa es la diferencia entre mirar y ANALIZAR.

---

## Qué se entrega

En `entregas/lab11/grupoXX/`: `informe.md` (informe forense completo), tu
`src/timeline.py` completado (opcional, suma) y la captura de `./ctf status 11`.
Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

La evidencia es ficticia y del laboratorio. En un caso real, la forense tiene
implicancias legales serias: la cadena de custodia y el manejo de la evidencia
pueden decidir un juicio. Se hace con rigor o no se hace.
