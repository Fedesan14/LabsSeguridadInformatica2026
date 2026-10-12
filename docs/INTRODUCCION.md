# Empezá por acá — Introducción a los prácticos

> **Leé esto antes que nada.** En 5 minutos entendés cómo se trabaja en TODOS los
> prácticos y qué se agregó desde la clase pasada. Después, a romper (y a
> investigar). **Ponete las pilas.**

---

## Qué es esto

Un recorrido práctico por la seguridad informática: **11 clases + un práctico
final**. No se aprende de memoria — se aprende **haciendo**. Cada clase tiene su
laboratorio con un objetivo concreto, herramientas reales y una entrega.

El arco va de **entender** (labs 01-04, en código) a **atacar a mano** (05-08), a
**automatizar con agentes** (09), a **defender** (10), a un **engagement completo**
(final) y a la **forensia** de todo lo que pasó (11).

> El mapa completo, clase por clase, está en la
> [Guía dinámica de clases](GUIA-DINAMICA-CLASES.md).

---

## Lo que tenés que hacer en CADA práctico

Todos los labs siguen el mismo ritmo. Aprendételo una vez y sabés trabajar todos.

### 1. Leé el README del lab — completo, antes de tocar nada
Cada lab (`labs/labNN-*/README.md`) está armado con la misma anatomía:
**Teoría → Ejemplos → Tools → Práctica**. Si saltás a la práctica sin leer la
teoría, vas a copiar comandos sin entender la salida. Y eso no es seguridad: es
adivinar.

### 2. Hacé el lab según su tipo

**Labs de código (01-04)** — se resuelven en **Python** (biblioteca estándar):
- Copiás el esqueleto a tu carpeta de grupo.
- Completás los `TODO` del `src/`.
- Respondés el análisis del incidente / las preguntas.

**Labs ofensivos (05-10)** — corren en **Docker** (no instalás nada):
```bash
make setup          # la primera vez (arma la consola del atacante)
./ctf lab 05        # levanta el lab y abre la guía
make shell          # entrás a la consola con todas las tools
# ... operás las herramientas contra el objetivo ...
./ctf submit 05 R1 'FLAG{...}'   # entregás cada flag que encontrás
./ctf status 05     # ves tu progreso
```

**Lab de forensia (11)** — analizás un paquete de evidencia (archivos), sin Docker.

### 3. Capturá las flags... pero acordate:
> **Las flags te enganchan; el INFORME es lo que evalúa la rúbrica.** Las flags
> demuestran que *pudiste*; el informe demuestra que *entendiste*.

### 4. Escribí el informe
Cada lab tiene su plantilla de entregable en `docs/entregable.md` (o
`informe-forense.md` en el 11). Completala con tu análisis y evidencia.
¿No sabés qué nivel se espera? Mirá el [Informe modelo](INFORME-MODELO.md): un
ejemplo completo, sobre un objetivo ficticio, con la estructura y calidad que
evalúa la rúbrica. Ese es el molde.

### 5. Entregá por fork + Pull Request
En grupos de 4-5, dentro de `entregas/labNN/grupoXX/`. El flujo completo está en
[`CONTRIBUTING.md`](../CONTRIBUTING.md). **Los commits de todos los integrantes
cuentan.**

### 6. (Opcional) Encará los retos bonus
Cuando las flags te queden chicas, cada lab tiene 3 desafíos extra en el
[Banco de retos bonus](BANCO-DE-RETOS.md) — con más herramientas y dificultad
progresiva (★/★★/★★★). No suman a la aprobación, pero es donde te hacés bueno.

**Regla de oro, siempre:** todo se practica SOLO contra los contenedores de la
cátedra. Contra terceros es delito (Ley 26.388).

---

## Qué se agregó desde la clase pasada (04/09)

*En la clase tenías el motor, los labs 01-10, el final y la presentación HTML/PPT.
Esto es lo nuevo:*

1. **🖥️ Presentación de terminal** (`./docs/presentacion.py`) — deck con onda
   hacker: matrix, radar, calavera, y cada slide se decodifica. Ahora explica
   **clase por clase**.
2. **📖 Guía dinámica de clases** — cada clase con gancho, ejemplo real y dato hacker.
3. **🎯 Banco de ~30 retos bonus** — más tools por lab, enlazado al pie de cada uno.
4. **🔬 Lab 11 — Forensia (DFIR)** — el lab nuevo: de atacar pasás a investigar.
5. **🛠️ `timeline.py`** — herramienta para reconstruir la línea de tiempo del ataque.

> El detalle está en [Novedades](NOVEDADES.md).

---

## Cómo bajás todo esto (sincronizar tu fork)

Trabajás sobre tu fork. Para traer lo nuevo sin perder tu trabajo:

```bash
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

¿No tenés el remoto `upstream`? Agregalo una vez:
```bash
git remote add upstream https://github.com/fboiero/LabsSeguridadInformatica2026.git
```

---

## En resumen

```
LEÉ el README  →  HACÉ el lab (código / ./ctf / forensia)  →  CAPTURÁ flags
      →  ESCRIBÍ el informe  →  ENTREGÁ por fork + PR  →  (bonus si te animás)
```

Eso, para los 11 labs. Es así de simple, y así de riguroso. **Dale que arrancamos.**
