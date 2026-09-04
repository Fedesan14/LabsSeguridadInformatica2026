# Laboratorio 01 — Informe

> **Instrucciones de uso de esta plantilla**
>
> 1. Copiala a `entregas/lab01/grupoXX/informe.md`.
> 2. Completá **todas** las secciones. Borrá estas instrucciones y todos los
>    textos en *cursiva*, que son consignas, no contenido.
> 3. No borres los encabezados ni cambies el orden: la corrección los sigue.
> 4. Si una sección no aplica, escribí por qué no aplica. **No la borres.**

---

## Identificación

| | |
|---|---|
| **Grupo** | |
| **Caso asignado (Parte A)** | |
| **Tema del mini-research** | |
| **Fecha de entrega** | |

### Integrantes

*Esta tabla también va en `INTEGRANTES.md`. Solo nombre, legajo y usuario de
GitHub. Nada de DNI, teléfono ni dirección: el repositorio es público.*

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| | | @ |
| | | @ |
| | | @ |
| | | @ |
| | | @ |

---

# PARTE A — Análisis del incidente bajo la lente CIA

## A.1 — Cronología

*Máximo 10 líneas. Qué pasó, cuándo, en qué orden. **Cada afirmación con su
fuente.** Si no encontrás una fuente que lo respalde, no lo escribas.*

| Fecha | Hecho | Fuente |
|---|---|---|
| | | |
| | | |
| | | |

---

## A.2 — Activo afectado

*¿Qué se estaba protegiendo? Concreto: no «los datos», sino qué datos, de
quién, en qué sistema. Si hubo más de un activo, priorizá y justificá el
orden.*

**Activo principal:**

**Por qué es el principal:**

**Otros activos afectados:**

---

## A.3 — Matriz CIA

*Una fila por propiedad. La columna «Evidencia» tiene que citar un hecho
concreto del incidente, no una generalidad.*

> **Advertencia.** «No» es una respuesta válida y muchas veces la correcta.
> El error típico es marcar las tres propiedades en «Sí» porque el incidente
> fue grave. La gravedad no es una propiedad de la tríada. Si marcás que se
> violó la integridad, tenés que mostrar **qué dato específico fue alterado**.
> Si no podés mostrarlo, la respuesta es «No».

| Propiedad | ¿Se violó? | Evidencia concreta |
|---|---|---|
| **Confidencialidad** | Sí / No / Parcial | |
| **Integridad** | Sí / No / Parcial | |
| **Disponibilidad** | Sí / No / Parcial | |

**Justificación ampliada de la propiedad más discutible:**

*De las tres, ¿cuál fue la más difícil de determinar y por qué? Desarrollá.*

---

## A.4 — Encadenamiento amenaza → vulnerabilidad → impacto

*Redacción en prosa, no viñetas. Usá los términos con precisión: una amenaza
no es una vulnerabilidad, un exploit no es una vulnerabilidad, y el impacto
no es el ataque.*

```
amenaza  →  explota  →  vulnerabilidad  →  sobre  →  activo  →  produce  →  impacto
```

| Elemento | En este caso |
|---|---|
| **Amenaza** *(quién / qué, con qué motivación)* | |
| **Vulnerabilidad** *(la debilidad concreta que se explotó)* | |
| **Activo** *(sobre qué recayó)* | |
| **Impacto** *(consecuencia sobre el negocio o las personas)* | |

**Redacción:**

*Un párrafo que encadene los cuatro elementos anteriores.*

---

## A.5 — Dos controles mitigantes

*Controles que, de haber estado implementados, habrían evitado o reducido el
incidente. Específicos y justificados contra **este** caso. «Tener antivirus»
o «capacitar a los usuarios» no califica.*

### Control 1

| | |
|---|---|
| **Qué es** | |
| **Propiedad de la tríada que protege** | |
| **Por qué habría funcionado en este caso concreto** | |

### Control 2

| | |
|---|---|
| **Qué es** | |
| **Propiedad de la tríada que protege** | |
| **Por qué habría funcionado en este caso concreto** | |

---

## A.6 — Fuentes consultadas (Parte A)

*Formato APA. Indicá para cada una si es primaria (informe oficial, documento
del fabricante, resolución judicial, paper) o secundaria (nota periodística,
entrada de blog).*

1.
2.
3.

---

# PARTE B — Integridad con funciones de hash

## B.1 — Evidencia de ejecución

*Pegá la salida real de cada comando. No la transcribas a mano: copiala tal
cual sale de la terminal.*

### Generación del manifiesto

```
$ python3 src/integridad.py generar --dir data/muestra --salida manifest.sha256

(pegar salida)
```

### Verificación sobre un directorio íntegro

```
$ python3 src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
$ echo "código de salida: $?"

(pegar salida)
```

### Detección de la modificación de un byte

*Esta prueba es obligatoria y tiene una penalización específica en la rúbrica
si falla.*

```
$ printf 'X' >> data/muestra/transferencia.txt
$ python3 src/integridad.py verificar --dir data/muestra --manifiesto manifest.sha256
$ echo "código de salida: $?"

(pegar salida — debe reportar MODIFICADO y salir con 1)
```

### Detección de archivo faltante y de archivo nuevo

```
(pegar los comandos que usaron y la salida)
```

### Efecto avalancha

```
$ python3 src/integridad.py avalancha --a "transferencia: $1000" --b "transferencia: $1001"

(pegar salida)
```

**Distancia obtenida:** ____ bits de 256 (____ %)

*¿Coincide con lo esperado? ¿Qué esperaban antes de correrlo?*

### HMAC

```
$ python3 src/integridad.py mac --clave "secreto" --mensaje "transferir 1000"

(pegar salida)
```

```
$ python3 src/integridad.py mac --clave "secreto" --mensaje "transferir 1000" --verificar <tag válido>
$ python3 src/integridad.py mac --clave "secreto" --mensaje "transferir 1000" --verificar <tag alterado>

(pegar ambas salidas)
```

---

## B.2 — Decisiones de implementación

*Qué decisiones tuvieron que tomar que el enunciado no resolvía por ustedes.
Ejemplos: cómo trataron los enlaces simbólicos, qué hicieron con los archivos
vacíos, cómo excluyeron el manifiesto del recorrido, qué pasa si el directorio
está vacío. Una o dos oraciones por decisión.*

| Decisión | Qué hicimos | Por qué |
|---|---|---|
| | | |
| | | |

---

## B.3 — Preguntas de análisis

> **Se responden con fundamento técnico, no con opinión.** Dos o tres párrafos
> cada una. Las respuestas de una línea no suman puntos.

### 1. El manifiesto por sí solo no alcanza

*Un atacante con acceso de escritura al directorio también puede escribir
`manifest.sha256`. ¿Qué le impide modificar un archivo y regenerar el
manifiesto para que todo dé `OK`? ¿Qué habría que cambiar en el esquema para
que ese ataque no funcione?*

**Respuesta:**

---

### 2. Qué agrega HMAC y qué no

*¿Qué propiedad de seguridad aporta HMAC que un hash simple no aporta? Y la
parte importante: ¿qué **no** resuelve HMAC? Pensá en el no repudio y en
quién conoce la clave.*

**Respuesta:**

---

### 3. MD5 y SHA-1

*Ambos siguen apareciendo en software en producción. ¿Qué propiedad
criptográfica se les rompió, exactamente? ¿Hay algún uso en el que todavía
sean aceptables, o ninguno? Fundamentá con al menos una fuente.*

**Respuesta:**

**Fuente:**

---

### 4. Comparación en tiempo constante

*¿Por qué comparar un tag de autenticación con `==` puede filtrar información
al atacante, y cómo lo evita `hmac.compare_digest()`? Describí el ataque
concreto que esto previene.*

**Respuesta:**

---

### 5. SHA-256 para contraseñas: mala idea

*SHA-256 es una función de hash criptográfica sólida. ¿Por qué, entonces, es
una mala elección para almacenar contraseñas? ¿Qué se usa en su lugar y qué
propiedad tienen esas funciones que SHA-256 no tiene?*

**Respuesta:**

---

# Cierre

## Dificultades encontradas

*Qué les costó, dónde se trabaron, qué decidieron y por qué. Esta sección se
lee y suma. No es relleno: es donde se ve si entendieron el problema.*

---

## Distribución del trabajo

*Quién hizo qué. Tiene que ser consistente con el historial de commits.*

| Integrante | Aportes |
|---|---|
| | |
| | |
| | |
| | |
| | |

---

## Declaración de uso de asistentes de IA

> **Obligatoria.** No está prohibido usar asistentes de IA. Lo que se evalúa es
> que entiendan lo que entregan. La omisión de esta declaración es **causal de
> rechazo automático** de la entrega. Una declaración honesta no baja la nota.

**¿El grupo usó asistentes de IA en este trabajo?**  Sí / No

*Si la respuesta es No, firmen igual la sección y pasen al final.*

| Herramienta | Para qué se usó | Qué partes del entregable afectó | Cómo se verificó que lo devuelto era correcto |
|---|---|---|---|
| | | | |
| | | | |

**Declaración:**

*El grupo declara que comprende el contenido íntegro de lo entregado y que
puede explicar y defender oralmente cualquier parte del código y del análisis,
independientemente de la asistencia recibida.*

---

## Fuentes consultadas (general)

*Todas las fuentes del trabajo, en formato APA. Las de la Parte A pueden
repetirse acá o referenciarse a la sección A.6.*

1.
2.
3.
