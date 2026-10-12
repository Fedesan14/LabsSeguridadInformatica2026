# Guía para docentes

> Cómo está diseñado el práctico, cómo se corrige y cómo se extiende. Para uso de
> la cátedra.

## Diseño pedagógico

Cada laboratorio ofensivo respeta la misma **anatomía de cuatro partes**, pensada
para que el alumno pueda seguirlo **solo** (autoexplicativo):

1. **Teoría** — el concepto desde cero, sin herramientas todavía.
2. **Ejemplos** — casos reales que muestran el patrón en la vida real.
3. **Tools** — cada herramienta explicada: qué hace, anatomía del comando, cómo
   leer la salida, cómo clasificar lo que encuentra.
4. **Práctica** — el alumno mete mano en el lab Docker y lo hace él mismo.

La progresión es deliberada: **manual (05–08) → agentes (09)**. Un mismo hilo
narrativo (PhantomCorp) mantiene el enganche y da continuidad entre unidades.

## Cómo corregir

Cada lab entrega en `entregas/labNN/grupoXX/` y trae su **rúbrica de 100 puntos**
en `labs/labNN-*/docs/rubrica.md`, con descriptores por componente y **causales de
rechazo automático** (operar fuera de alcance, IA no declarada, commits de una
sola cuenta, flags copiadas del `solucion.md`).

Cada lab tiene además un **`solucion.md`** (marcado *SOLO DOCENTE*) con las flags
en claro, los comandos exactos y la clave de clasificación. **No compartir con
alumnos.**

Peso general: las **flags valen poco** (demuestran que operaron las tools); el
**informe/análisis vale la nota** (demuestra que entendieron).

## Verificar un lab antes de darlo

```bash
make setup                 # una vez
./ctf lab NN               # levanta el entorno
make shell                 # (o make shell-victima en el Lab 08)
# ... resolvé los retos como lo haría el alumno ...
./ctf submit NN R1 'FLAG{...}'
./ctf status NN
make down
```

Regla de oro de autoría: **si una flag no se puede obtener con las tools tal como
la guía lo indica, el lab no está listo.** Probalo vos antes que ellos.

## Rotar las flags (por cohorte, o si se filtraron)

Si sospechás que alguien vio las soluciones, o simplemente querés flags nuevas
para otra cohorte, no hace falta editar a mano cada target. Usá el rotador:

```bash
bin/rotar-flags.py                 # DRY-RUN: muestra qué cambiaría, no escribe
bin/rotar-flags.py --lab 07        # solo un lab
bin/rotar-flags.py --apply         # aplica en todos los labs
bin/rotar-flags.py --random --apply  # flags opacas FLAG{<hex>} en vez de slug
```

Qué hace, sin romper nada:

- Cambia el **valor** de cada flag y recalcula su `sha256` en el `retos.manifest`.
  Detecta la codificación de cada target (base64, claro o URL-encoded) y respeta
  la que corresponde.
- En el **Lab 11** recalcula la cadena de custodia (`evidencia.sha256`) de los
  archivos que toca, pero **respeta el hash falso de `auth.log`** — ese "fallo"
  de custodia es el reto R5.
- Deja el nuevo answer-key en `.soluciones-docente/FLAGS-<fecha>.txt`
  (gitignoreado, nunca se sube).

Después de `--apply`, **reconstruí las imágenes Docker** (`make setup` / rebuild
del lab) para que los targets sirvan las flags nuevas. Y verificá un reto de
punta a punta, como siempre.

## Crear un laboratorio nuevo

El molde está en `labs/_plantilla/`. El procedimiento completo, en
[`../labs/_plantilla/COMO-CREAR-UN-LAB.md`](../labs/_plantilla/COMO-CREAR-UN-LAB.md).
Resumen:

1. `cp -r labs/_plantilla labs/labNN-tema` (el número y el tema se derivan solos
   del nombre del directorio).
2. Armá el target vulnerable en `entorno/`.
3. Definí las flags con `bin/nueva-flag.sh` (guarda **hashes**, nunca la flag en
   claro).
4. Completá el `README.md` respetando la anatomía de 4 partes.
5. Adaptá la rúbrica y los entregables.
6. Probá de punta a punta.

## Estado de publicación

| Unidad | Lab | Tipo | Estado |
|---|---|---|---|
| 1 | Introducción (CIA, hashing) | código | Publicado |
| 2–4 | Cripto, normativa | código | Por publicar |
| 5 | Reconocimiento | ofensivo | Publicado |
| 6 | Enumeración | ofensivo | Publicado |
| 7 | Explotación | ofensivo | Publicado |
| 8 | Post-explotación | ofensivo | Publicado |
| 9 | Agentes | ofensivo | Publicado |

## Nota sobre el Lab 09 y las API keys

El Lab 09 usa una API de LLM (Claude u OpenAI) de forma **agnóstica** (se elige por
variable de entorno). Para no depender de que cada alumno tenga key, incluye un
motor **`mock`** offline que corre el agente de forma determinística. Sirve para
corregir sin costo y para que cualquier alumno vea el loop funcionar. **Ninguna
API key debe subirse al repo** — es causal de rechazo y obliga a rotar la key.
