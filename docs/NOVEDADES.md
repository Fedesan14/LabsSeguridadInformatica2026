# Novedades — actualización del 09/10/2026

> **Para los alumnos.** Arrancamos el **Bloque 2: ofensiva a mano**. Dejamos de
> escribir código y empezamos a **atacar** PhantomCorp con herramientas reales.
> Hay material nuevo para la clase 05-06 y un **diagnóstico de 5 minutos** para
> que sepas dónde estás parado antes de tirar el primer `nmap`.
>
> **Seamos honestos:** veníamos con el acelerador flojo. Las entregas están en
> los labs 01-03 y hace rato que no se mueven. No pasa nada — pero es hora de
> **ponerse las pilas**, porque lo que viene es lo bueno, y se construye sobre
> los fundamentos. Sincronizá tu fork y ponete al día.

## ¿En qué estado estás? Averigualo en 5 minutos

Antes de atacar, un **espejo**. No es nota: es para que VOS sepas si tenés la
base de los labs 01-04 y si tu entorno está listo. Se autocorrige solo.

```bash
cp docs/diagnostico-respuestas.txt mi-diagnostico.txt   # tu copia
# completá mi-diagnostico.txt con tus respuestas
python3 bin/diagnostico.py mi-diagnostico.txt           # feedback al instante
```

Te va a devolver uno de cuatro estados — **LISTO**, **CASI**, **REPASAR** o
**ENTORNO** — y una línea `RESULTADO` que **pegás en tu entrega**. Con eso el
docente ve cómo llega el curso y ajusta la clase. Detalle en
[`docs/DIAGNOSTICO-05-06.md`](DIAGNOSTICO-05-06.md).

## Qué más hay de nuevo

### 1. 🎯 Diagnóstico del cruce a ofensiva
`bin/diagnostico.py` + la plantilla `docs/diagnostico-respuestas.txt`. 8
preguntas de fundamentos (01-04) + 3 que se contestan **operando el lab 05**.
Las respuestas van hasheadas, igual que las flags: nada de espiar el código.

### 2. 🧠 Ejercicios nuevos de recon y enumeración
Seis desafíos para los labs 05-06 que **no se capturan, se razonan**. Casi sin
flags: acá se entrena el criterio (clasificar, priorizar, planear el ataque),
que es lo que la rúbrica paga de verdad. →
[`docs/EJERCICIOS-CLASE-05-06.md`](EJERCICIOS-CLASE-05-06.md)

### 3. 🖥️ Deck de la clase 05-06
La presentación del cruce a ofensiva, en PowerPoint. →
[`docs/clase-05-06-cruce-ofensiva.pptx`](clase-05-06-cruce-ofensiva.pptx)

## Cómo bajar las novedades

Sobre tu **fork**, desde la raíz:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

> ¿No tenés `upstream`? Agregalo una vez:
> `git remote add upstream https://github.com/fboiero/LabsSeguridadInformatica2026.git`

## El plan, sin vueltas

1. **Sincronizá** tu fork (arriba).
2. **Corré el diagnóstico.** Si te da REPASAR, volvé a los labs 01-04 ESE tema
   puntual. Si te da ENTORNO, resolvé Docker primero.
3. **Arrancá el Lab 05** (recon) y asomá el **Lab 06** (enum).
4. Si vas sobrado, metele los **ejercicios nuevos**.

**Dale que ahora empieza lo que viniste a aprender: romper (con criterio).**

---

# Novedades — actualización del 11/09/2026

> **Para los alumnos.** Desde la clase del **viernes 04/09** el repo creció bastante.
> Nada de lo que ya hiciste cambia: esto es **todo sumado**. Sincronizá tu fork
> (abajo te digo cómo) y aprovechá lo nuevo. **Ponete las pilas** que ahora hay
> más para exprimir.

*Referencia: en la clase (viernes 04/09, 18:30) tenías el motor, los labs 01-10,
el práctico final y la presentación en HTML y PowerPoint. Todo lo de abajo es
posterior a esa clase.*

---

## Qué cambió

### 1. 🖥️ Presentación de TERMINAL (nueva)
Además del deck HTML y el PPT que ya conocías, ahora hay una presentación que corre
**en la terminal**, con onda hacker de verdad: intro con **lluvia de Matrix**, un
**radar** que barre buscando el objetivo, el **firewall** con un candado que se
abre, una **calavera "SYSTEM PWNED"**, y cada slide que se **decodifica** desde el
ruido. Se maneja con las flechas.

```bash
./docs/presentacion.py        # ← → navegar · g ir a una slide · q salir
```

### 2. 📖 Guía dinámica de clases
Un mapa de las 11 clases + el práctico final, explicado para engancharte: gancho,
la idea sin vueltas, un ejemplo real (WannaCry, Adobe, TalkTalk…), las tools y un
"dato hacker" por clase. → [`docs/GUIA-DINAMICA-CLASES.md`](GUIA-DINAMICA-CLASES.md)

También está **dentro de la presentación de terminal**: la sección "Las clases,
una por una" tiene una diapositiva por clase (saltá con `g`).

### 3. 🎯 Banco de ~30 retos bonus
¿Las flags te quedaron cortas? Cada lab (01-10) ahora tiene **3 desafíos extra**,
progresivos (★/★★/★★★), que meten más herramientas: `sqlmap`, `nmap` NSE, `wfuzz`,
`git-dumper`, túneles, concurrencia, prompt injection al agente, correlación de
logs. Opcionales, pero es donde te hacés bueno de verdad.
→ [`docs/BANCO-DE-RETOS.md`](BANCO-DE-RETOS.md) (y el link está al pie de cada lab)

### 4. 🔬 Lab 11 nuevo — Forensia del pentest (DFIR)
El cierre del curso. Ahora te das vuelta: de atacar pasás a **investigar**. Te
llega el paquete de evidencia de un PhantomCorp comprometido (logs, disco,
memoria, cadena de custodia) y tenés que **reconstruir el ataque**: por dónde
entró, el webshell, la escalada, el C2, y detectar una evidencia **alterada**.
5 hallazgos + un informe forense. → [`labs/lab11-forensia/`](../labs/lab11-forensia/)

### 5. 🛠️ `timeline.py` — tu herramienta forense
Un esqueleto en el Lab 11 para que automatices la línea de tiempo del ataque en
vez de leer el log a ojo. Completás dos funciones y tenés tu propio timeline.

---

## Cómo seguir (bajá las novedades)

Trabajás sobre tu **fork**. Para traer todo lo nuevo sin perder tu trabajo,
sincronizá con el repo de la cátedra (`upstream`). Desde la raíz de tu fork:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

> ¿No tenés el remoto `upstream`? Agregalo una sola vez:
> ```bash
> git remote add upstream https://github.com/fboiero/LabsSeguridadInformatica2026.git
> ```
> El detalle está en [`CONTRIBUTING.md`](../CONTRIBUTING.md).

Después de sincronizar:

1. **Leé la guía dinámica** (novedad 2) para ubicarte en el arco completo.
2. **Seguí con el Lab 11 (Forensia)** — es el que cierra el recorrido.
3. **Volvé a los labs que ya hiciste** y encará los **retos bonus** (novedad 3):
   son los que te llevan al siguiente nivel.
4. Probá la **presentación de terminal** (novedad 1): `./docs/presentacion.py`.

---

## ¿Qué NO cambió?

- Tu trabajo en `entregas/` está intacto.
- El flujo de entrega (fork + Pull Request, grupos, rúbricas) es el mismo.
- Los labs 01-10 y el final **no se modificaron**: solo se les sumó el link al
  banco de retos al pie. Lo que entregaste sigue valiendo igual.

Cualquier duda, un Issue en el repo. **Dale que ahora hay más para romper (y para
investigar).**
