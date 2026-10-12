# Laboratorio 01 — Introducción a la Seguridad Informática

**Unidad 1** · Conceptos básicos y evolución histórica
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab01/grupoXX/`
**Fecha límite:** antes del inicio de la Clase 2

---

## Por qué este laboratorio

La seguridad informática no arranca con herramientas. Arranca con una pregunta:
**¿qué propiedad de la información estoy tratando de proteger, y contra qué?**

Si no sabés responder eso, ninguna herramienta te sirve. Vas a estar corriendo
scanners sin entender qué te dicen los resultados.

Este laboratorio tiene dos partes que atacan la misma idea desde dos lados:

- **Parte A** — Mirás un incidente real y lo descomponés con el vocabulario de
  la tríada CIA. Del titular de diario a la propiedad concreta que se violó.
- **Parte B** — Implementás en Python el control técnico más básico que
  protege una de esas propiedades: la verificación de integridad mediante
  funciones de hash.

Es a propósito. Primero el concepto, después el código. Si escribís el código
sin haber hecho la Parte A, el código no significa nada.

---

## Objetivos de aprendizaje

Al terminar este laboratorio deberías poder:

1. Definir con precisión confidencialidad, integridad y disponibilidad, y
   distinguir cuál de las tres se ve afectada en un incidente concreto.
2. Encadenar correctamente los términos **amenaza**, **vulnerabilidad**,
   **activo** e **impacto** al describir un incidente.
3. Explicar qué propiedades hacen que una función de hash criptográfica sirva
   para verificar integridad, y cuáles son sus límites.
4. Implementar en Python un verificador de integridad basado en manifiestos de
   hashes, y razonar sobre qué ataques detecta y cuáles no.
5. Fundamentar por qué la comparación de secretos debe hacerse en tiempo
   constante.

Tributa al **Objetivo 1** del Diseño Curricular y a los resultados de
aprendizaje **RA1** y **RA2**.

---

## Requisitos

- Python 3.10 o superior. **Solo biblioteca estándar.**
- Git y una cuenta de GitHub por integrante.
- Haber leído [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

Verificá:

```bash
python3 --version
```

---

## Preparación del entorno

Desde la raíz de tu fork, después de crear tu rama `lab01-grupoXX`:

```bash
mkdir -p entregas/lab01/grupoXX
cp -r labs/lab01-introduccion/src  entregas/lab01/grupoXX/src
cp -r labs/lab01-introduccion/data entregas/lab01/grupoXX/data
cp labs/lab01-introduccion/docs/entregable.md entregas/lab01/grupoXX/informe.md
cp labs/lab01-introduccion/docs/research.md   entregas/lab01/grupoXX/research.md
```

Generá los datos de muestra:

```bash
cd entregas/lab01/grupoXX
python3 data/generar_datos.py
```

Deberías ver creado `data/muestra/` con cuatro archivos. **Ese directorio no se
versiona** (está en `.gitignore`): se regenera con el script. Lo que se entrega
es el código, no los datos.

Verificá que el esqueleto arranca:

```bash
python3 src/integridad.py --help
python3 src/integridad.py generar --help
```

Ambos comandos tienen que funcionar **antes** de que toques una sola línea.
Si fallan, algo se copió mal.

---

## Parte A — Análisis de un incidente bajo la lente CIA

### Caso asignado

Cada grupo trabaja **un** caso. La asignación la publica el docente; si no la
recibiste, usá `número_de_grupo mod 6` sobre esta tabla.

| # | Incidente | Año |
|---|---|---|
| 0 | **Morris Worm** | 1988 |
| 1 | **Stuxnet** | 2010 |
| 2 | **Target** (brecha de datos de tarjetas) | 2013 |
| 3 | **WannaCry** | 2017 |
| 4 | **Equifax** | 2017 |
| 5 | **SolarWinds / SUNBURST** | 2020 |

### Qué hay que producir

En `informe.md`, sección Parte A:

**A.1 — Cronología.** Máximo 10 líneas. Qué pasó, cuándo, en qué orden.
**Cada afirmación con su fuente.** No vale «se dice que». Si no encontrás la
fuente, no lo pongas.

**A.2 — Activo afectado.** ¿Qué se estaba protegiendo? Sean concretos: no
«los datos», sino qué datos, de quién, en qué sistema. Si hubo más de un
activo, prioricen.

**A.3 — Matriz CIA.** Una tabla, las tres propiedades, **una por una**:

| Propiedad | ¿Se violó? | Evidencia |
|---|---|---|
| Confidencialidad | Sí / No / Parcial | *Hecho concreto del incidente que lo demuestra* |
| Integridad | Sí / No / Parcial | |
| Disponibilidad | Sí / No / Parcial | |

Ojo con esto: **«No» es una respuesta válida y frecuentemente la correcta.**
El error típico es marcar las tres en sí porque «fue grave». La gravedad no es
una propiedad de la tríada. Si marcás que se violó la integridad, tenés que
mostrar **qué dato fue alterado**. Si no podés, la respuesta es «No».

**A.4 — Encadenamiento.** Una redacción breve, en prosa, que conecte:

```
amenaza  →  explota  →  vulnerabilidad  →  sobre  →  activo  →  produce  →  impacto
```

Usá los términos con precisión. Una vulnerabilidad no es lo mismo que una
amenaza. Un exploit no es una vulnerabilidad. El impacto no es el ataque.

**A.5 — Dos controles mitigantes.** Dos controles que, de haber estado
implementados, habrían evitado o reducido el incidente. Para cada uno:

- Qué es el control, en una o dos oraciones.
- **Qué propiedad de la tríada protege.**
- Por qué habría funcionado *en este caso concreto* — no en general.

No listen «tener un antivirus» o «capacitar a los usuarios». Sean específicos
y justifiquen contra el caso.

---

## Parte B — Integridad con funciones de hash

### El problema

Tenés un directorio con archivos. Necesitás poder responder, en cualquier
momento futuro: **¿alguno de estos archivos cambió?**

La solución clásica es un **manifiesto**: un registro que asocia cada archivo
con el digest de una función de hash criptográfica. Si el digest de hoy no
coincide con el registrado, el archivo cambió.

Es el mismo mecanismo que usan los sistemas de verificación de integridad de
archivos (FIM), los gestores de paquetes cuando validan una descarga, y los
sistemas de control de versiones.

### Qué hay que implementar

El archivo `src/integridad.py` es una CLI con `argparse` y **cuatro
subcomandos**. Cada uno tiene un bloque `TODO` que actualmente lanza
`NotImplementedError`. Su trabajo es completarlos.

**No modifiquen la firma de las funciones ni la interfaz de la CLI.** El
esqueleto ya trae `sha256_archivo()` implementada como referencia: léanla
antes de empezar, muestra el patrón de lectura por bloques que hay que seguir.

#### B.1 — `generar`

```bash
python3 src/integridad.py generar --dir data/muestra --salida manifest.sha256
```

Recorre el directorio **recursivamente** y escribe un manifiesto en JSON que
mapea cada ruta relativa a su digest SHA-256.

Requisitos:

- Rutas **relativas** al directorio base, en formato **POSIX** (con `/`, no
  con `\`). Un manifiesto generado en Windows tiene que verificar en Linux.
- Claves **ordenadas** alfabéticamente. Un manifiesto es un artefacto que se
  compara y se versiona: si el orden cambia entre corridas, el `diff` es
  inútil.
- El archivo de salida no debe incluirse a sí mismo si queda dentro del
  directorio recorrido.

#### B.2 — `verificar`

```bash
python3 src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
```

Contrasta el estado actual del directorio contra el manifiesto y clasifica
cada archivo:

| Estado | Significado |
|---|---|
| `OK` | Está en el manifiesto y el digest coincide |
| `MODIFICADO` | Está en el manifiesto y el digest **no** coincide |
| `FALTANTE` | Está en el manifiesto pero ya no existe en el disco |
| `NUEVO` | Está en el disco pero no en el manifiesto |

Requisitos:

- Salida legible por un humano: un resumen con la cuenta de cada categoría y
  el detalle de todo lo que no sea `OK`.
- **Código de salida `1`** si hay al menos un hallazgo (`MODIFICADO`,
  `FALTANTE` o `NUEVO`). **Código `0`** si está todo `OK`.

Ese código de salida no es un detalle cosmético: es lo que permite que este
programa se use dentro de un script de monitoreo o un pipeline de CI. Un
programa que reporta problemas por pantalla pero sale con `0` es un programa
que nadie puede automatizar.

Prueba obligatoria — tiene que detectar **un byte**:

```bash
python3 src/integridad.py generar --dir data/muestra --salida manifest.sha256
printf 'X' >> data/muestra/transferencia.txt
python3 src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
echo "código de salida: $?"
```

Debe reportar `transferencia.txt` como `MODIFICADO` y salir con `1`.

#### B.3 — `avalancha`

```bash
python3 src/integridad.py avalancha --a "transferencia: \$1000" --b "transferencia: \$1001"
```

Calcula la **distancia de Hamming en bits** entre los digests de dos mensajes,
para evidenciar el *efecto avalancha*: un cambio mínimo en la entrada produce
un cambio masivo e impredecible en la salida.

**Cuidado con esto.** La distancia se calcula **sobre los bits**, no sobre los
caracteres hexadecimales. Dos dígitos hex distintos pueden diferir en 1 bit o
en 4. Si contás caracteres, el número te va a dar mal y el ejercicio pierde
todo el sentido.

Pista: `hashlib.sha256(...).digest()` te devuelve los bytes crudos. `int.bit_count()`
(Python 3.10+) cuenta los bits en 1 de un entero. El XOR de dos bytes tiene un
1 exactamente en las posiciones donde difieren.

La salida debe incluir ambos digests, la distancia en bits, el total de bits
(256) y el porcentaje. Para dos entradas distintas cualesquiera, el valor
esperado ronda el 50 %.

#### B.4 — `mac`

```bash
python3 src/integridad.py mac --clave "secreto" --mensaje "transferir 1000"
python3 src/integridad.py mac --clave "secreto" --mensaje "transferir 1000" --verificar <tag>
```

Calcula un **HMAC-SHA256** (RFC 2104) sobre el mensaje con la clave dada, y
—si se pasa `--verificar`— compara el tag recibido contra el calculado.

Requisitos:

- Usar el módulo `hmac` de la biblioteca estándar. **No implementen HMAC a
  mano**: el objetivo es entender qué resuelve, no reescribir el estándar.
- La comparación **debe** hacerse con `hmac.compare_digest()`, no con `==`.
  El porqué es una de las preguntas de análisis: contéstenla antes de
  escribir la línea.

---

## Preguntas de análisis

Van en `informe.md`, sección Parte B. **Se responden con fundamento técnico,
no con opinión.** Dos o tres párrafos cada una. Las respuestas de una línea no
suman.

1. **El manifiesto por sí solo no alcanza.** Un atacante que consiguió acceso
   de escritura al directorio también puede escribir el archivo
   `manifest.sha256`. ¿Qué le impide modificar un archivo y regenerar el
   manifiesto para que todo dé `OK`? ¿Qué habría que cambiar en el esquema
   para que ese ataque no funcione?

2. **Qué agrega HMAC y qué no.** ¿Qué propiedad de seguridad aporta HMAC que
   un hash simple no aporta? Y ahora la parte importante: ¿qué **no**
   resuelve HMAC? Pensá en el no repudio y en quién conoce la clave.

3. **MD5 y SHA-1.** Ambos siguen apareciendo en software en producción hoy.
   ¿Qué propiedad criptográfica se les rompió, exactamente? ¿Hay algún uso en
   el que todavía sean aceptables, o ninguno? Fundamenten con al menos una
   fuente.

4. **Comparación en tiempo constante.** ¿Por qué comparar un tag de
   autenticación con `==` puede filtrar información al atacante, y cómo lo
   evita `hmac.compare_digest()`? Describí el ataque concreto que esto
   previene.

5. **SHA-256 para contraseñas: mala idea.** SHA-256 es una función de hash
   criptográfica sólida. ¿Por qué, entonces, es una **mala elección** para
   almacenar contraseñas? ¿Qué se usa en su lugar y qué propiedad tienen esas
   funciones que SHA-256 no tiene? *(Pista: Argon2id, bcrypt, scrypt.)*

---

## Mini-research

Además del informe, cada grupo entrega un trabajo de investigación de **800 a
1000 palabras** sobre uno de cinco temas a elección.

La consigna completa, los temas y los requisitos de citación están en
[`docs/research.md`](docs/research.md). **Leelo: tiene requisitos de fuentes
que no se negocian.**

---

## Autoevaluación (feedback instantáneo)

Mientras completás los `TODO`, chequeá tu avance sin esperar la corrección:

```bash
python3 src/verificar.py
```

**Verde** = va · **rojo** = revisá (te dice qué falló) · **gris** = todavía no lo
implementaste. No es la nota — es para que **iteres solo**, como con las flags de
los labs ofensivos.

---

## Qué se entrega

Dentro de `entregas/lab01/grupoXX/`:

```
entregas/lab01/grupoXX/
├── INTEGRANTES.md      # nombre, legajo, usuario de GitHub — nada más
├── informe.md          # Partes A y B + preguntas de análisis
├── research.md         # mini-research, 800-1000 palabras
├── src/
│   └── integridad.py   # con los 4 TODO implementados
└── data/
    └── generar_datos.py
```

`INTEGRANTES.md` lleva **exclusivamente** nombre y apellido, legajo y usuario
de GitHub. Nada de DNI, teléfono, dirección ni correo personal: el repositorio
es público.

> **Recordá:** `data/muestra/` y `manifest.sha256` **no se versionan**. Son
> salida, no fuente. Ya están en `.gitignore`.

---

## Evaluación

La rúbrica completa, con el detalle de los 100 puntos, está en
[`docs/rubrica.md`](docs/rubrica.md). Resumen:

| Componente | Puntos |
|---|---|
| Parte A — análisis del incidente | 35 |
| Parte B — implementación y preguntas | 40 |
| Mini-research | 20 |
| Proceso (uso de Git, colaboración) | 5 |
| **Total** | **100** |

Aprobación: **60**. Nivel de promoción práctica: **80**.

**Leé la rúbrica antes de empezar**, no después de entregar. Tiene una
penalización específica y tiene causales de rechazo automático.

---

## Bibliografía de la unidad

**Obligatoria**

- Cybrary. *Introduction to IT & Cybersecurity*.
  https://www.cybrary.it/course/introduction-to-it-and-cybersecurity/

**Referencia técnica para la Parte B**

- NIST. *FIPS PUB 180-4: Secure Hash Standard (SHS)*.
- Krawczyk, H., Bellare, M. y Canetti, R. *RFC 2104: HMAC — Keyed-Hashing for
  Message Authentication*. IETF.
- Documentación de Python: módulos `hashlib` y `hmac`.

**Marco conceptual**

- ISO/IEC 27000:2018 — *Information security management systems — Overview and
  vocabulary*. (Definiciones de confidencialidad, integridad y disponibilidad.)

**Marco legal argentino**

- Ley 26.388 — Delitos informáticos.
- Ley 25.326 — Protección de los Datos Personales.
- Ley 27.411 — Adhesión al Convenio de Budapest sobre Ciberdelito.

---

## Consultas

Abrí un **Issue** en este repositorio con la etiqueta `lab01`. Es público: si
tenés la duda vos, la tienen otros tres grupos.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
