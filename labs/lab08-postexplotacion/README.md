# Laboratorio 08 — Post-explotación y automatización

**Unidad 8** · Post-explotación: escalada de privilegios, pivoting y scripting
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab08/grupoXX/`
**Entorno:** Docker (dos hosts en redes segmentadas)

> **Estás adentro.** En el Lab 07 lograste ejecución de comandos (RCE) en el
> portal de PhantomCorp. Este lab arranca desde ahí: tenés una shell sin
> privilegios en el servidor. La pregunta ya no es "¿cómo entro?" sino
> **"¿qué hago ahora que entré?"**. Hacé los labs 05–07 primero.

---

## El escenario

Caíste como el usuario `operador` en el servidor de PhantomCorp. Un atacante real
no se queda ahí: **reconoce el terreno interno, roba lo que sirve, se hace root,
salta a otros equipos, y automatiza**. Ese es exactamente tu recorrido:

1. Reconocer el host donde caíste (¿quién sos? ¿qué hay?).
2. Lootear credenciales y datos.
3. Escalar privilegios: de `operador` a `root`.
4. Pivotear: usar este host como trampolín a la **red interna** que desde afuera
   no se ve.
5. **Automatizar** lo tedioso — porque hacer 250 requests a mano no lo hace nadie.

Ese último punto es la bisagra del curso: cuando entendés cómo se **encadena** y
**automatiza** un ataque, estás listo para el Lab 09, donde un **agente** hace
esa orquestación por vos. Pero primero lo hacés a mano. Siempre.

---

## Por qué este laboratorio

La explotación te da un pie adentro. La **post-explotación** es todo lo que
convierte ese pie adentro en control real. En MITRE ATT&CK son varias tácticas
encadenadas: *Discovery*, *Credential Access*, *Privilege Escalation*,
*Lateral Movement*, *Persistence*.

Dos ideas centrales:

> **1. Un shell sin privilegios es el principio, no el final.** El valor está en
> lo que hacés después: escalar, moverte, persistir.

> **2. Lo que se hace más de una vez, se automatiza.** El atacante que scriptea
> su flujo es 100x más rápido. Y automatizar es el paso previo a delegar en un
> agente. Si no sabés encadenar tools en un script, no vas a saber dirigir un
> agente que las encadena.

---

## Objetivos de aprendizaje

1. Ejecutar **reconocimiento del host** comprometido (identidad, sistema, red).
2. **Lootear** credenciales y secretos de un sistema al que ya accediste.
3. Identificar y explotar una **escalada de privilegios** por binario **SUID**.
4. Explicar y ejecutar **pivoting**: alcanzar un host de una red segmentada a
   través del host comprometido.
5. **Automatizar** una tarea repetitiva con un script y argumentar por qué la
   automatización es el puente hacia los agentes (Lab 09).

---

## Requisitos y preparación

```bash
make setup                 # si no lo hiciste antes
./ctf lab 08               # levanta el host comprometido + el host interno (DB)
make shell-victima         # ← ¡OJO! entrás al HOST COMPROMETIDO como 'operador'
```

**Importante:** en este lab **no** trabajás desde la consola del atacante
(`make shell`), sino desde **adentro del host comprometido** (`make shell-victima`).
Simula que ya tenés tu RCE del Lab 07.

> **Regla de oro.** Todo dentro del lab. Ley 26.388.

---

## Parte 1 · TEORÍA — la vida después del shell

Apenas caés en un sistema, un atacante metódico se hace tres preguntas, **en
orden**:

```
1. ¿QUIÉN soy?      -> id, whoami            (¿qué permisos tengo?)
2. ¿DÓNDE estoy?    -> hostname, uname -a,   (¿qué sistema? ¿qué red?)
                       ip addr, env
3. ¿QUÉ puedo hacer?-> sudo -l, find SUID,   (¿cómo subo de nivel?)
                       archivos escribibles
```

**Escalar privilegios** es pasar de un usuario común a `root` (control total).
Una vía clásica: un binario con el **bit SUID** activo, que se ejecuta con los
permisos de su **dueño** (root) en vez de los tuyos. Si ese binario te deja correr
comandos, corrés comandos **como root**.

**Pivoting** (movimiento lateral): las redes internas están **segmentadas**. El
servidor web ve la base de datos interna, pero vos desde Internet no. Una vez
adentro del servidor web, lo usás de **trampolín** para alcanzar esa red que
antes no existía para vos.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — SUID a root en segundos.** Un `find / -perm -4000` lista binarios
SUID. Si aparece algo raro (una copia de `bash`, `find`, `python`, `vim` con
SUID), GTFOBins te dice el truco exacto para saltar a root. Es una de las
escaladas más comunes en CTFs y en la vida real.

**Ejemplo B — El pivot que abrió la red.** En muchas brechas grandes, el equipo
comprometido inicialmente era **irrelevante** (un servidor web público). El daño
vino de usarlo para **saltar** a la red interna —bases de datos, controladores de
dominio— que desde afuera eran invisibles.

**Ejemplo C — Automatizar o morir.** Enumerar 10.000 IDs, probar 500 usuarios,
descargar 200 archivos: a mano es imposible. Un `for` de tres líneas lo hace en
segundos. El pentester que scriptea encuentra lo que el que hace click no.

---

## Parte 3 · TOOLS Y TÉCNICAS

Todo desde `make shell-victima` (sos `operador`).

### 3.1 Reconocimiento del host

```bash
id ; whoami ; hostname ; uname -a
env                                  # variables de entorno (¡suelen filtrar secretos!)
ip addr ; cat /etc/hosts             # ¿a qué redes/hosts llego?
ls -la /opt /var/www /home           # ¿qué archivos interesantes hay?
```

### 3.2 Loot de credenciales

```bash
cat /var/www/.env                    # configs de apps = credenciales
cat ~/.bash_history                  # qué comandos corrió el usuario antes (¡oro!)
grep -rai "pass\|secret\|token" /var/www 2>/dev/null
```

### 3.3 Escalada de privilegios

```bash
sudo -l 2>/dev/null                  # ¿puedo correr algo como root?
find / -perm -4000 -type f 2>/dev/null   # binarios SUID
# si encontrás una copia SUID de bash, GTFOBins dice: ejecutalo con -p
#   /ruta/al/binario -p        (mantiene los privilegios del dueño)
```

### 3.4 Pivoting

```bash
# desde la victima, ¿qué hay en la red interna que desde el atacante no se ve?
curl -s http://phantomcorp-db/       # este host solo se alcanza DESDE acá
```

### 3.5 Automatización

```bash
# lo tedioso, en un loop:
for i in $(seq 1 250); do curl -s "http://phantomcorp-db/empleado?id=$i"; done
# afinalo: filtrá, parseá con python, guardá resultados. Eso es una herramienta.
```

---

## Parte 4 · PRÁCTICA

Desde `make shell-victima`:

| Reto | Fase | Pista |
|---|---|---|
| **R1** | Reconocimiento del host | Recién caíste. Enumerá el filesystem: mirá en `/opt`. Hay una nota de deploy que no debería estar. |
| **R2** | Loot de credenciales | Las apps guardan sus secretos en archivos de config. Buscá el `.env` de la aplicación. |
| **R3** | Escalada de privilegios | Buscá binarios SUID. Uno no es estándar. GTFOBins te dice cómo usarlo para leer un archivo que solo root puede leer (`/root/flag.txt`). |
| **R4** | Pivoting | Hay un host interno (`phantomcorp-db`) que la consola del atacante NO alcanza. Desde acá sí. Tocalo. |
| **R5** | Automatización | Ese host tiene 250 legajos (`/empleado?id=N`). Uno esconde el flag. A mano es inviable: **scriptealo**. |

```bash
./ctf submit 08 R1 'FLAG{...}'
./ctf status 08
```

> Para entregar las flags corré `./ctf submit` desde la **raíz del repo** (fuera
> del host víctima). Copiá y pegá la flag que encontraste adentro.

---

## Parte 5 · ANÁLISIS Y AUTOMATIZACIÓN — el entregable (la nota)

### A. Informe de post-explotación

| Fase | Qué hiciste | Comando/técnica | Evidencia | Defensa |
|---|---|---|---|---|
| Recon host | | | | |
| Loot | | | | |
| Privesc | | | | |
| Pivoting | | | | |

### B. El script de automatización (obligatorio)

En `src/` hay un esqueleto (`recolector.py`) que automatiza el R5. Completalo:
que enumere los 250 legajos, encuentre el que tiene el flag, y lo imprima. **Es
el entregable central de este lab**: demostrar que sabés convertir una tarea
manual en una herramienta.

Bonus (suma en research): esbozá cómo encadenarías recon → enum → explotación de
los labs anteriores en **un solo pipeline**. Eso es, conceptualmente, lo que hará
tu agente en el Lab 09.

### Preguntas de análisis

1. **P1.** ¿Por qué un binario SUID es peligroso? ¿Qué hace el flag `-p`?
2. **P2.** Explicá el pivoting con lo que hiciste: ¿por qué el atacante no
   alcanzaba `phantomcorp-db` y vos sí desde la víctima?
3. **P3.** El `.bash_history` y el `.env` te dieron loot. ¿Qué práctica de
   desarrollo/operaciones evita que esos secretos queden ahí?
4. **P4.** Tu script del R5 automatizó 250 requests. ¿Qué **decisiones** tuviste
   que tomar vos que el script no toma solo? (esto es clave para el Lab 09).
5. **P5.** Defensor: proponé una mitigación concreta para el privesc por SUID y
   otra para el pivoting.

---

## Qué se entrega

En `entregas/lab08/grupoXX/`: `informe.md`, `src/recolector.py` (completado) y
`research.md`. Fecha límite: antes del Lab 09. Rúbrica en
[`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Post-explotación es control de un sistema ajeno: máxima gravedad legal fuera del
lab. Solo la cátedra. Ley 26.388.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
