# Plan de clase — Cruce a ofensiva (labs 05-06)

> Uso docente. Viernes 18:30. Esta es LA clase bisagra: se termina el bloque de
> código y empieza el pentesting a mano. Diseñada para un curso que viene
> **atrasado en entregas** y con **3 semanas sin movimiento** — por eso abre con
> diagnóstico, no con contenido nuevo a ciegas.

## Dónde está parado el curso (foto real)

De los PRs en GitHub al momento de armar esta clase:

- **Lab 01** entregado por 4 grupos (05, 07, 08, 12) — todos abiertos.
- **Lab 02** por 2 grupos (02, 07). **Lab 03** por 1 grupo (06, cerrado).
- Última actividad de entrega: **19/09**. Hoy: ~3 semanas después.

**Lectura:** el material llega a lab 11, pero el curso real está en **01-03** y
frenado. No tiene sentido empujar lab 07 si no consolidaron la base. Hoy se
**mide, se reencuadra y se arranca ofensiva con red** — no se corre.

## Objetivo de la clase

1. **Reencuadrar** tras el parate: dónde estábamos, a dónde vamos (el arco).
2. **Diagnosticar** con datos, no con sensación, dónde está cada grupo.
3. **Arrancar el bloque 2**: recon (05) + enumeración (06) sobre PhantomCorp.
4. Dejar **una entrega concreta y alcanzable** para recuperar ritmo.

## Timeline sugerido (clase de ~3 h con break)

| Bloque | Min | Qué |
|---|---|---|
| Apertura | 15 | Reencuadre con la PPT nueva (arco completo + por qué hoy es bisagra). |
| **Diagnóstico** | 20 | Cada grupo corre `bin/diagnostico.py`. Levantás el semáforo del aula. |
| Teoría recon | 25 | Pasivo vs activo, el bucle descubrir→identificar→clasificar→priorizar. |
| Demo en vivo | 25 | `nmap -p-`, banner grab, `curl -I`, robots.txt contra PhantomCorp. |
| *break* | 15 | |
| Manos a la obra 05 | 30 | Grupos cazan las 5 flags del lab 05. Vos circulás. |
| Puente a enum | 20 | Del mapa (05) al detalle (06): dirb, `.git`, métodos, API, fingerprint. |
| Ejercicios nuevos | 20 | Soltás `EJERCICIOS-CLASE-05-06.md` (los que midan por grupo). |
| Cierre + la pedida | 10 | Qué entregan y para cuándo (abajo). |

> Si en el diagnóstico **predomina ENTORNO**, cambiá el plan sin culpa: la clase
> se vuelve taller de Docker. Sin entorno no hay bloque 2. Es tiempo bien
> invertido, no tiempo perdido.

## Qué pedirles (la entrega de esta clase)

**Mínimo exigible (todos los grupos, para la próxima):**

1. **Línea `RESULTADO` del diagnóstico** pegada en el PR del grupo. Es el termómetro.
2. **Lab 05 completo** — las 5 flags + el **mapa de superficie** (la tabla
   puerto→servicio→versión→clasificación de `README.md` § Parte 5). Recordales:
   *las flags enganchan, el mapa es la nota.*
3. **Lab 06 arrancado** — al menos R1 (enumeración de directorios) y R2 (`.git`
   expuesto), con el **inventario** empezado.

**Para el que va LISTO (que no afloje):**

4. Uno de los **ejercicios nuevos** de `EJERCICIOS-CLASE-05-06.md` — los de
   clasificación y razonamiento, que es lo que separa al que captura del que
   entiende.

**Recuperación (grupos en REPASAR):**

- Antes que nada, cerrar labs 01-03. El diagnóstico les dice qué tema puntual.
  No los mandes a lab 05 con la base rota: es prepararlos para que fracasen.

## Causales de rechazo (recordáselas)

Mismas de siempre (ver rúbricas): operar fuera del alcance (solo los contenedores
de la cátedra), IA no declarada, commits de una sola cuenta, flags copiadas del
`solucion.md`. El CI de PRs (`.github/workflows/validar.yml`) ya chequea salud del
repo y reglas de entrega automáticamente.

## Material de apoyo de esta clase

- **PPT:** `docs/clase-05-06-cruce-ofensiva.pptx` (deck general + bisagra).
- **Diagnóstico:** `docs/DIAGNOSTICO-05-06.md` + `bin/diagnostico.py`.
  Clave en `.soluciones-docente/DIAGNOSTICO-05-06-key.md` (NO al repo).
- **Ejercicios nuevos:** `docs/EJERCICIOS-CLASE-05-06.md`.
- Presentación de terminal (si querés onda hacker en vivo): `./docs/presentacion.py`.
