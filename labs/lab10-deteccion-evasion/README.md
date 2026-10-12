# Laboratorio 10 — Detección y evasión: la vista del defensor

**Unidad 10** · Detección, respuesta y evasión (Blue vs Red)
**Modalidad:** grupos de 4 a 5 · **Entorno:** Docker
**Entrega:** fork + Pull Request en `entregas/lab10/grupoXX/`

> Durante cinco labs fuiste el atacante. Ahora **date vuelta**: del otro lado
> siempre hubo alguien mirando. Este lab te muestra cómo el **defensor** ve tus
> ataques — y cómo un atacante intenta que no lo vea. Hacé los labs 05–09 primero.

---

## El escenario

PhantomCorp aprendió de las auditorías anteriores y montó un **SOC** (Security
Operations Center): un IDS que inspecciona cada request contra **firmas** de
ataque y un log de eventos. Tu misión tiene dos caras:

- Como **Red team**: entender qué te delata y aprender a **evadir** la detección.
- Como **Blue team**: leer los logs, entender las firmas, y encontrar una
  **intrusión real** escondida entre el tráfico normal.

Porque un buen pentester piensa como defensor, y un buen defensor piensa como
atacante. Los dos lados son el mismo conocimiento.

---

## Por qué este laboratorio

Todo lo que hiciste (05–09) **dejó huella**. Un `nmap -p-` son miles de conexiones;
un `sqlmap` manda payloads con firma reconocible; un dirb pega en cientos de rutas.
El defensor lo ve. Este lab cierra el círculo del curso:

> **La detección por firmas es poderosa pero frágil.** Reconoce lo que *ya conoce*.
> El que entiende la firma la esquiva; y lo que ninguna firma detecta, solo lo
> encuentra alguien **leyendo los logs**. Por eso el SOC necesita las dos cosas:
> reglas *y* analistas.

En MITRE ATT&CK esto toca **Defense Evasion** (TA0005) del lado rojo y toda la
disciplina de *Detection* del lado azul.

---

## Objetivos

1. Entender cómo un IDS/WAF detecta ataques por **firmas** y qué es un **log de
   seguridad**.
2. Provocar una detección y **leer la alerta** para entender qué te delató.
3. **Evadir** una firma de detección mediante ofuscación del payload.
4. Analizar logs para **separar el ruido del ataque real** (correlación básica).
5. Argumentar, como defensor, cómo **mejorar** una detección evadible.

---

## Requisitos y preparación

```bash
make setup
./ctf lab 10
make shell
curl -s http://phantomcorp/           # el portal está monitoreado
```

> **Regla de oro.** Solo `phantomcorp`. Ley 26.388.

---

## Parte 1 · TEORÍA — el otro lado del ataque

Un **IDS/WAF** por firmas funciona como un antivirus: tiene un **ruleset** de
patrones conocidos (una User-Agent de `sqlmap`, un `../`, un `UNION SELECT`) y
alerta cuando un request matchea. Su fortaleza: detecta ataques conocidos al
instante. Su debilidad: **solo** detecta lo que su firma describe **exactamente**.

Un **log de seguridad** registra los eventos. El trabajo del analista (SOC) es
**correlacionar**: entre miles de líneas benignas, encontrar la que no lo es. La
detección automática (firmas) y la humana (análisis de logs) se complementan.

Del lado atacante, **evasión** es lograr que tu acción maliciosa **no matchee**
ninguna firma: ofuscás el payload, cambiás la User-Agent, codificás caracteres,
vas *low-and-slow*. La misma acción, disfrazada.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — La firma que exigía un espacio.** Muchos WAF viejos detectaban
`UNION SELECT` con un espacio literal. Los atacantes escribían `UNION/**/SELECT`
(comentario SQL en vez de espacio): mismo efecto, otra cadena, firma evadida.

**Ejemplo B — Cambiar la User-Agent.** `sqlmap` se anuncia en su User-Agent. Un
IDS lo bloquea al toque. Cambiando la UA a la de un navegador, el mismo ataque
pasa desapercibido. La detección miraba *quién decís ser*, no *qué hacés*.

**Ejemplo C — La aguja en el pajar.** En brechas reales, la evidencia del ataque
**estaba en los logs** desde el día uno. Nadie la miró hasta meses después. La
herramienta no falló; faltó el analista.

---

## Parte 3 · TOOLS Y TÉCNICAS

Todo con `curl` desde la consola.

```bash
# ver el log del SOC (la vista del defensor):
curl -s http://phantomcorp/soc

# provocar una detección (User-Agent de scanner):
curl -s -A sqlmap http://phantomcorp/

# ver el ruleset activo del IDS:
curl -s http://phantomcorp/soc/reglas

# evadir: mandá un ataque que NO matchee la firma exacta
#   (¿cómo escribís UNION SELECT sin el espacio que la firma exige?)
curl -s "http://phantomcorp/api?q=..."

# análisis de logs: filtrá las alertas y encontrá la que no disparaste vos
curl -s http://phantomcorp/soc | grep ALERT
```

**Cómo leer una alerta:** el IDS te dice **qué firma** disparó. Esa información,
que para el defensor es un evento, para el atacante es un mapa: si sabés qué
firma te detectó, sabés qué tenés que esquivar.

---

## Parte 4 · PRÁCTICA

| Reto | Cara | Pista |
|---|---|---|
| **R1** | Blue | Accedé a la vista del SOC (`/soc`). Ahí arranca todo. |
| **R2** | Red | Hacé un request que el IDS detecte. La User-Agent es lo más fácil de delatar. Leé la alerta. |
| **R3** | Blue | El SOC publica su ruleset. Conocer las reglas es el primer paso para evadirlas. |
| **R4** | Red | El ruleset te dijo que `sqli-union` exige un **espacio**. Mandá un `UNION SELECT` **sin** ese espacio y colate. |
| **R5** | Blue | En `/soc` hay 120 líneas de tráfico normal y **una** intrusión real que vos NO disparaste. Encontrala. |

```bash
./ctf submit 10 R1 'FLAG{...}'
./ctf status 10
```

---

## Parte 5 · ANÁLISIS — pensá como defensor (la nota)

En `informe.md`:

| Firma | Cómo la evadiste (o cómo se evade) | Cómo la mejorarías |
|---|---|---|
| scanner-ua | | |
| sqli-union | | |

### Preguntas de análisis

1. **P1.** ¿Por qué la detección por firmas es evadible por diseño? ¿Qué la
   complementa?
2. **P2.** La firma `sqli-union` exigía un espacio. Reescribí la regla para que
   NO se evada con `/**/`. ¿Se puede hacer una firma "perfecta"?
3. **P3.** Detectar por User-Agent: ¿por qué es una detección débil? ¿Qué mirarías
   en lugar de "quién dice ser"?
4. **P4.** El R5: la intrusión estaba en el log. ¿Qué habría hecho que se detecte
   automáticamente y no dependiera de que alguien la mire?
5. **P5.** Cierre del curso: recorriste ataque (05–08), agentes (09) y defensa
   (10). ¿Por qué un buen atacante tiene que entender al defensor, y viceversa?

---

## Qué se entrega

En `entregas/lab10/grupoXX/`: `informe.md` (tabla de firmas + P1–P5 + captura de
`./ctf status 10`) y `research.md`. Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Evadir detección se practica **solo** contra el lab. Fuera de acá, evadir un IDS
ajeno agrava el delito (Ley 26.388). El objetivo acá es **entender la defensa**,
no burlar la de nadie.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
