# Ejercicios nuevos — clase 05-06 (recon + enumeración)

> Complementan las 5 flags base de cada lab y el
> [`BANCO-DE-RETOS.md`](BANCO-DE-RETOS.md) (que es más de *tool*). Estos son otra
> cosa: **no se capturan, se razonan.** Casi no hay flag — hay criterio. Y el
> criterio es exactamente lo que la rúbrica paga y donde más se patina.
>
> Regla: todo contra los contenedores de la cátedra, en tu máquina. Nada afuera.

---

## Por qué estos ejercicios

Capturar una flag demuestra que **pudiste**. Clasificar lo que encontraste
demuestra que **entendiste**. El principiante tira `nmap`, ve 4 puertos abiertos
y grita "¡encontré algo!". No encontró nada: encontró puertos. El hallazgo
aparece cuando los **nombrás, los clasificás y los priorizás**. Eso es lo que
practicás acá.

Cada ejercicio entrega **texto en tu `entregable.md`** (salvo que diga otra cosa).
Corto, preciso, defendible. Si no lo podés defender en 3 líneas, no lo entendiste.

---

# Lab 05 · Reconocimiento

### E05.1 — Recon pasivo primero, sin tocar nada ★
**La idea:** antes de escanear a lo bruto, un buen recon exprime lo que el objetivo
**regala solo**. Levantá el lab 05 y, SIN hacer `nmap`, juntá todo lo que puedas
del puerto 80: el cuerpo del HTML, los headers (`curl -I`), el `robots.txt`.

**Qué entregás:**
1. Tres cosas que inferís del objetivo **sin escanear puertos** (ej. qué CMS,
   qué versión, qué rutas sensibles asoman).
2. En el HTML del index hay un **comentario de infraestructura**. Transcribilo y
   explicá por qué un comentario olvidado es, técnicamente, un **hallazgo** — y
   qué le filtra al atacante que el equipo no quería.

> Dato: el recon pasivo no genera ruido en los logs del objetivo. Por eso se hace
> primero. El que arranca con `nmap -p-` a lo bestia ya se anunció.

### E05.2 — El puerto que cuenta una historia ★★
**La idea:** un barrido completo (`nmap -p-`) encuentra un servicio en el **31337**.
Ese número no es casualidad.

**Qué entregás:**
1. Qué significa `31337` en la jerga y por qué, cuando aparece, el analista
   **desconfía**.
2. Por qué un servicio de mantenimiento en un **puerto alto no estándar** es un
   riesgo **distinto** a uno en el 80 — en términos de *exposición* y de *por qué
   el defensor lo pasó por alto*.
3. **Clasificá:** ¿qué propiedad de la tríada CIA amenaza ese servicio, y por qué?
   (Sí, esto es del lab 01. Por algo los fundamentos van primero.)

### E05.3 — Mapa de superficie con PRIORIDAD, no lista ★★
**La idea:** cualquiera lista 4 servicios. El profesional dice **cuál atacar
primero y por qué**. Tomá los 4 servicios de PhantomCorp (21, 80, 8080, 31337).

**Qué entregás:** una tabla `servicio → exposición → impacto potencial → prioridad
(1-4)` y, debajo, **3 líneas** defendiendo tu orden. La prioridad sale de cruzar
*qué tan expuesto está* con *cuánto daño haría si cae* — no de cuál te resulta más
fácil. (Distinto del reto ★★★ del banco, que arma la tabla CVSS: acá lo que se
evalúa es el **razonamiento de priorización**, no el score.)

---

# Lab 06 · Enumeración

### E06.1 — Del `.git` a la intención ★★
**La idea:** el `/.git/` expuesto filtra más que un archivo: filtra la **historia**
del proyecto. Ya viste el `.git/config` y su URL interna. Sin dumpear el repo
completo (eso es el reto ★★★ del banco), **razoná**:

**Qué entregás:**
1. Qué **otros tres archivos** del `.git` pedirías (ej. `HEAD`, `logs/HEAD`,
   `index`) y qué revela **cada uno**.
2. Qué riesgo **concreto** implica para PhantomCorp que su `.git` esté accesible —
   nombralo contra la tríada CIA (¿confidencialidad del código? ¿secretos
   commiteados?).
3. Una frase de **remediación** que el equipo de PhantomCorp debería aplicar hoy.

### E06.2 — PUT habilitado = webshell (en la teoría) ★★
**La idea:** la intranet tiene el método **PUT** habilitado. Descubrilo con
`curl -X OPTIONS` (o el NSE `http-methods`). **No lo explotes** — razoná la cadena.

**Qué entregás:**
1. La **cadena de ataque** que habilita un PUT abierto: de "método habilitado" a
   "ejecuto código en el server". Paso a paso, en palabras.
2. Por qué "PUT está habilitado" **no es** el hallazgo — el hallazgo es lo que
   **permite**. Clasificá la severidad **con argumento** (no un número CVSS: por
   qué es grave o no en ESTE contexto).
3. La configuración que lo cierra.

> Importante: el ejercicio es de **razonamiento**. No subas nada al target. Saber
> por qué algo es peligroso vale más que apretar el gatillo sin entender.

### E06.3 — La API que habla de más ★★★
**La idea:** `/api/users` devuelve usuarios y **roles** (`admin/superuser`,
`jperez/editor`, `mgomez/viewer`). Enumerá eso (R4) y después **pensá como el que
va a atacar en el lab 07**.

**Qué entregás:** un **plan de ataque priorizado** (en papel, no se ejecuta nada
todavía):
1. Con esos usuarios y roles, ¿a **quién** apuntarías primero y por qué?
2. ¿Qué técnica del lab 07 usarías (p. ej. fuerza de credenciales dirigida al
   `admin`, no al azar) y cómo la **enumeración de hoy** la hace más barata?
3. Qué **control** habría evitado que la API te regale la lista de usuarios.

Esto es el puente real recon/enum → explotación: la enumeración no es un fin, es
**munición** para el paso siguiente. El que enumera sin plan, junta datos; el que
enumera con plan, prepara el golpe.

---

## Cómo se corrigen

Van en el `entregable.md` del grupo, en una sección **"Ejercicios de clase
05-06"**. Se evalúa **criterio**, no cantidad de texto: una respuesta de 3 líneas
bien fundada vale más que media carilla de relleno. Peso sugerido: hasta +10 sobre
la nota del lab, o como recuperación de concepto para grupos en estado REPASAR.

**Causales de rechazo (las de siempre):** operar fuera del alcance, IA no
declarada, copiar de otro grupo sin atribución. El razonamiento es **tuyo** o no
es nada.
