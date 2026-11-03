# Mini-research — Laboratorio 11

**Grupo:** 03

**Tema elegido:** **A.** Volatility 3: cómo se captura un volcado de RAM (LiME, avml) y qué plugins se usan para procesos, red y credenciales.

- [x] **A.** Volatility 3: cómo se captura un volcado de RAM (LiME, avml) y qué plugins se usan para procesos, red y credenciales.
- [ ] **B.** Orden de volatilidad (RFC 3227) y por qué define el orden de captura.
- [ ] **C.** Cadena de custodia: requisitos legales y por qué una evidencia mal manejada se cae en un juicio.
- [ ] **D.** IOCs y su ciclo de vida: cómo se comparten (STIX/TAXII, MISP) y cómo se usan para detectar el mismo ataque en otros sistemas.

---

## Desarrollo

### Por qué esto importa para el caso

El README del lab lo dice de frente: "un volcado de RAM real pesa gigas y no entra
en un repo [...] en producción usarías Volatility 3 sobre el dump". Los propios archivos de evidencia de `caso/memoria/` llevan un comentario con el comando real que los generó (`# volatility3 linux.pslist (extracto)`, `# volatility3 linux.sockstat (extracto)`, `# volatility3 linux.lsof (extracto)`). Esta investigación completa esa parte que el lab dio "ya resuelta": **cómo se captura** la RAM antes de poder analizarla, y **qué hace exactamente** cada uno de esos plugins por dentro, en vez de tratarlos como una caja negra.

### Primero hay que capturar: LiME y avml

Antes de poder correr Volatility hace falta un volcado de memoria, y eso lo hace una herramienta de **adquisición**, no de análisis. Dos opciones típicas en Linux:

**LiME (Linux Memory Extractor)**, de 504ENSICS Labs, es un **módulo de kernel cargable** (`insmod`): se compila contra la versión exacta del kernel objetivo y se inserta en el sistema en vivo. Su propio repositorio explica que esta decisión de diseño "minimiza su interacción entre procesos de espacio de usuario y kernel durante la adquisición", lo que la hace más confiable forense que leer `/dev/mem` desde espacio de usuario. Soporta tres formatos de salida (`raw`, `padded`, y `lime`, que agrega un header con el mapa de direcciones de cada rango de memoria) y puede escribir el volcado a disco local o transmitirlo por red (por ejemplo, con `netcat`), con hash opcional (SHA-256) para dejar registrada la integridad de la captura desde el primer momento, como la propia cadena de custodia de este lab exige.

**AVML (Acquire Volatile Memory for Linux)**, de Microsoft, resuelve la limitación más incómoda de LiME: no necesita compilarse contra el kernel del objetivo. Es un binario estático que lee la memoria desde espacio de usuario (`/dev/crash`, `/proc/kcore` o `/dev/mem`, probando cada uno si no se indica cuál usar), pensado explícitamente para "adquirir memoria sin conocer de antemano la distribución o el kernel del objetivo". Está probado contra una matriz amplia de distros (Ubuntu, RHEL, Debian, SUSE, Oracle Linux, entre
otras) y su formato de salida es **compatible con el de LiME** (además de poder convertir entre `AVML / LiME / raw`), con soporte nativo para subir el volcado directo a Azure Blob Storage o a una URL pre-firmada de S3/GCS sin tocar el disco local. La contrapartida: si el kernel tiene `kernel_lockdown` activado, AVML no puede adquirir memoria (en ese escenario, LiME, al correr como módulo de kernel, sigue teniendo más margen).

### Después, el análisis: arquitectura de Volatility 3

Volatility 3 (el sucesor de Volatility 2, reescrito en Python) ya no analiza el volcado directo: lo interpreta a través de varias capas, según su propia documentación: **capas de memoria** (la abstracción sobre los bytes crudos del dump), **templates y objetos** (que interpretan esos bytes como estructuras de datos con sentido, ej. un `task_struct`), **tablas de símbolos** y **plugins** (unidades de análisis concretas, como las que usamos en el caso). Para Linux en particular, Volatility necesita una **tabla de símbolos (ISF, *Intermediate Symbol File*)** que coincida con la versión exacta del kernel del volcado — sin eso, no puede traducir las direcciones de memoria crudas a estructuras como "lista de procesos" o "socket abierto". Es la misma idea que haber necesitado, en el caso de este lab, que alguien ya supiera qué aspecto tiene un `task_struct` o un `hist_entry` de bash para poder extraer `pslist.txt` o `bash_history.txt`.

### Los plugins detrás de la evidencia del caso

Confirmamos en el repositorio oficial de Volatility 3 (`framework/plugins/linux/`) que los tres plugins citados en los comentarios de `caso/memoria/` existen tal cual:

- **`linux.pslist`** — lista los procesos activos recorriendo la lista enlazada
  de tareas del kernel. Es el origen de `pslist.txt`, donde vimos el proceso
  `system-check` corriendo con `euid=0` y el `nc` hacia el C2.
- **`linux.sockstat`** — expone las conexiones de red por proceso (origen de
  `netstat.txt`), que fue donde encontramos la conexión `ESTABLISHED` hacia
  `45.13.37.7:4444`.
- **`linux.lsof`** — lista los archivos abiertos por cada proceso (origen de
  `lsof.txt`), que fue donde vimos el `.tar.gz` de la exfiltración todavía
  abierto por el proceso `bash` del atacante.

El más interesante para este caso es un cuarto plugin que **no** aparece citado en los comentarios, pero que explica exactamente el hallazgo de la sección 2 del informe (P1/P4): **`linux.bash`**. Revisamos su código fuente: su propio docstring dice que "recupera el historial de comandos de bash desde la memoria del proceso". No lee `.bash_history` del disco en ningún momento: recorre la lista de procesos buscando `bash`/`sh`/`dash`, aísla el **heap** de cada uno (porque ahí es donde bash guarda sus entradas de historial en una estructura `hist_entry`), y escanea ese heap buscando el carácter `#` que bash antepone como marca de tiempo a cada comando guardado, para después reconstruir cada entrada completa con su timestamp. Esto confirma, a nivel de implementación, por qué `history -c` (que solo limpia el archivo en disco y el historial en memoria del intérprete de líneas del propio proceso) no borra retroactivamente lo que un volcado de memoria tomado mientras el proceso seguía vivo ya capturó: el comando de limpieza y la técnica de recuperación operan sobre estructuras distintas.

---

## Fuentes (mín. 3)

1. Volatility Foundation. *Volatility 3 Documentation.*
   [https://volatility3.readthedocs.io/en/latest/](https://volatility3.readthedocs.io/en/latest/)
   — arquitectura (capas, símbolos, plugins) y lista de plugins Linux.
2. 504ENSICS Labs (repositorio transferido actualmente a jtsylve). *LiME —
   Linux Memory Extractor* (repositorio oficial).
   [https://github.com/jtsylve/LiME](https://github.com/jtsylve/LiME) —
   adquisición por módulo de kernel, formatos `raw`/`padded`/`lime`, captura
   local/por red.
3. Microsoft. *AVML — Acquire Volatile Memory for Linux* (repositorio oficial).
   [https://github.com/microsoft/avml](https://github.com/microsoft/avml) —
   adquisición en espacio de usuario sin módulo de kernel, compatibilidad con
   el formato de LiME, soporte multi-distro y subida a la nube.
4. Volatility Foundation. *`volatility3/framework/plugins/linux/bash.py`*
   (código fuente del plugin, repositorio oficial).
   [https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py](https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/bash.py)
   — cómo se recupera el historial de bash desde el heap del proceso, no desde
   el archivo en disco.

---

## Reflexión

Lo que más cambió con esta investigación es cómo entendemos la sección 2 del informe (P1/P4): antes de esto, "la RAM no miente" era una frase que repetíamos porque la vimos en el README, sin poder explicar el mecanismo. Ahora podemos decir exactamente por qué: `linux.bash` no lee el archivo que el atacante borró con `history -c`, lee una estructura de datos (`hist_entry`) que bash mantiene en el heap de su propio proceso mientras corre, con una marca de tiempo reconocible (`#`). El atacante hubiera necesitado matar su propia sesión (y
perder la shell interactiva) para que esa evidencia dejara de existir también en memoria. También nos sorprendió que exista una herramienta como AVML pensada específicamente para no depender de compilar un módulo de kernel por cada distro distinta, justo el problema que hace a LiME más incómodo de usar en un parque heterogéneo de servidores — son dos herramientas que compiten en el mismo paso (adquisición) con compromisos opuestos entre confiabilidad forense y portabilidad operativa.