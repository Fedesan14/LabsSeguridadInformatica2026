# Laboratorio Extra 2 — El repo que delata (forense git)

**Actividad extra** (posterior al Lab 06; buen puente hacia el Lab 11)
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/labextra2/grupoXX/`
**Entorno:** sin Docker — solo `git` y tu terminal

> PhantomCorp te pasa el repositorio de su `deploy-tool` y te jura que está
> limpio: *"ya sacamos las credenciales del código, revisá el último commit si
> querés"*. Tu trabajo es demostrarles que **git no olvida**: encontrar todo lo
> que creyeron borrar, reconstruir cómo pasó, y escribir el informe que nadie
> quiere recibir.

---

## Por qué este laboratorio

Borrar un secreto del código **no lo borra de la historia**. Es el error de
seguridad más común del mundo real: hay bots que barren GitHub 24/7 buscando
claves en commits, y una API key filtrada se empieza a usar en **minutos**.

La lección tiene tres niveles, y los vas a vivir con las manos:

1. **El commit viejo.** `git log` muestra mensajes; `git log -p` muestra
   *cambios*. Lo que se commiteó alguna vez quedó.
2. **El commit "perdido".** Un `git reset --hard` no borra el objeto: queda
   colgado en el *reflog* y en el object store. Git guarda todo por ~90 días.
3. **La rama abandonada.** Lo que no está en `main` sigue estando en el repo.
   Las ramas viejas son un archivero de secretos.

Y el corolario de defensa: **reescribir la historia (force-push) tampoco es
remediación** si alguien ya clonó o forkeó. La única remediación real es
**rotar el secreto**.

## Objetivos de aprendizaje

1. Explicar por qué "borrar en un commit nuevo" no elimina un secreto.
2. Investigar una historia de git: `log -p`, `reflog`, `fsck`, ramas.
3. Reconstruir una línea de tiempo de la filtración (quién, cuándo, qué).
4. Evaluar la exposición real: ¿quién pudo haberlo visto ya?
5. Prescribir la remediación correcta: rotación primero, reescritura después.

## Preparación

```bash
./ctf lab extra2        # genera el caso (un repo git con historia sospechosa)
cd labs/labextra2-git-forense/caso/repo-delata
git log --oneline --all
```

El generador es **determinista**: todos los grupos investigan exactamente la
misma historia. No uses herramientas externas: `git` y tus ojos alcanzan.

## Parte 1 · TEORÍA — el modelo mental: git guarda TODO

Git es una base de datos de objetos **append-only**. Cada commit apunta a un
árbol de archivos; cada rama y cada `HEAD` son solo *referencias* a commits.

```
   rama main ──> C3 ──> C2 ──> C1     (referencias: solo etiquetas movibles)
                    │
                    └── el CONTENIDO de C2 sigue existiendo aunque
                        ninguna rama lo apunte  →  reflog / fsck lo encuentran
```

Consecuencias:

| Lo que creés | Lo que pasa en realidad |
|---|---|
| "Saqué la key en un commit nuevo" | El commit viejo la sigue teniendo: `git log -p` |
| "Hice `reset --hard`, se perdió" | El objeto quedó: `git reflog`, `git fsck --lost-found` |
| "Eso está en una rama vieja, no en main" | `--all` lo ve todo; y quien clonó, también |
| "Hice force-push, ya no existe" | Ya estaba clonado/forkeado/indexado por bots |

## Parte 2 · EJEMPLOS — cómo se ve en la vida real

**Ejemplo A — Los bots de GitHub.** Servicios legítimos (GitGuardian, TruffleHog)
y atacantes escanean cada push público. El tiempo mediano entre *push* y *uso
de una clave de AWS filtrada* es de minutos. Borrar el commit 10 minutos
después no cambia nada: ya la tenían.

**Ejemplo B — El force-push que no fue.** Una empresa "limpia" su historia con
`git filter-repo` + force-push. Pero 40 devs tenían clones locales, 6 forks
existían, y el commit quedó accesible por hash directo en la API de GitHub
durante meses. La key hubo que rotarla igual — la reescritura solo evitó
*futuras* exposiciones.

**Ejemplo C — La rama de staging.** Nadie revisa `feature/test-2019`. Ahí está
el `.env` con las credenciales viejas… que siguen vigentes porque *"total eso
no está en main"*.

## Parte 3 · PRÁCTICA — investigá el repo y cazá las 3 flags

El repo está en `caso/repo-delata/`. Tres secretos quedaron atrapados en su
historia. Cada uno premia una técnica distinta de la Parte 1.

| Reto | Técnica | Pista |
|---|---|---|
| **R1** | Historia con cambios | `git log` solo muestra mensajes ("fix: sacar credenciales del codigo (ups)"). ¿Qué cambió exactamente en cada commit? Hay un flag para ver el *diff* de la historia completa. |
| **R2** | Objetos colgados | Hubo un `reset --hard` que "borró" trabajo. El *reflog* recuerda todo lo que hizo HEAD; `git fsck` encuentra objetos sin referencia. |
| **R3** | Ramas | `git log --all` y `git branch -a`. Alguien arrancó una integración de pagos y la dejó a mitad de camino. Con un archivo que "no había que commitear". |

Entregá cada una:

```bash
./ctf submit extra2 R1 'FLAG{...}'
./ctf status extra2
```

### Preguntas de análisis (en `entregable.md`)

1. **P1.** Reconstruí la **línea de tiempo** completa de la filtración del
   token de la API: qué commit lo introdujo (autor, fecha, mensaje), qué commit
   "lo sacó", y cuánto tiempo estuvo expuesto. ¿Alcanza con el commit de
   limpieza? Justificá.
2. **P2.** El dev hizo `reset --hard` para "borrar" sus notas. Explicá con el
   modelo de objetos de git por qué no funcionó, y nombrá **dos** comandos que
   lo demuestran.
3. **P3.** ¿Qué riesgo representa la rama abandonada si este repo fuera
   *público*? ¿Y si fuera privado pero con 30 colaboradores?
4. **P4.** PhantomCorp ya publicó este repo en GitHub y hubo forks. Proponé el
   plan de remediación **en orden**, y explicá por qué reescribir la historia
   es la parte *menos* urgente.
5. **P5.** Como defensor: nombrá **dos** mecanismos que habrían *prevenido*
   que estos secretos entraran a la historia (pista: uno corre en tu máquina
   antes del commit, otro corre en el servidor al hacer push).

## Qué se entrega

En `entregas/labextra2/grupoXX/`:

- `informe.md` — a partir de `docs/entregable.md`: línea de tiempo, los 3
  hallazgos con los comandos exactos que usaste y su salida, las 5 preguntas,
  y captura de `./ctf status extra2` completo.
- `research.md` — a partir de `docs/research.md`: herramientas reales de
  detección/limpieza de secretos, o un incidente real por claves en git.

**Evidencia obligatoria (además del informe):** ver la sección
[Reporte y evidencia](#reporte-y-evidencia).

La rúbrica está en [`docs/rubrica.md`](docs/rubrica.md).

---

## Reporte y evidencia

Además del informe, el grupo adjunta en su directorio de entrega:

1. **`evidencia/comandos.txt`** — la salida de `history` de la terminal (o un
   listado fiel) con **todos** los comandos git que usaron, en orden.
2. **`evidencia/salidas/`** — la salida cruda (redirigida con `>`) de los 3
   comandos que encontraron cada flag: `git log -p ... > salidas/r1.txt`, etc.
3. **Captura de `./ctf status extra2`** con los 3 ✓.
4. **Declaración de IA** (obligatoria, en el informe).
5. El historial de commits del PR mostrando trabajo de **todos** los
   integrantes (como en todos los labs).

> **Por qué tanta evidencia:** una flag se puede copiar; una cadena de
> investigación no. La evidencia es lo que permite al docente distinguir
> "encontraron" de "entendieron".

## Uso responsable

La investigación se hace sobre el caso generado localmente. La técnica
(buscar secretos en historias de git) aplicada a repos de terceros sin
autorización puede violar la Ley 26.388 y los términos de servicio de las
plataformas. Reportar hallazgos por los canales de divulgación responsable
(coordinated disclosure) es la vía correcta cuando es legítimo.
