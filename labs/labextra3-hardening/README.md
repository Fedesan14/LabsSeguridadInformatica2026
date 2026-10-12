# Laboratorio Extra 3 — Defendé PhantomCorp (hardening)

**Actividad extra** (posterior al Lab 07; cierra el arco con el Lab 10)
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/labextra3/grupoXX/`
**Entorno:** sin Docker — Python puro (stdlib)

> Todo el cuatrimestre **rompiste** PhantomCorp: recon, enumeración, SQLi,
> traversal, SSRF. Ahora te dan el código fuente de la app y una orden:
> **arreglala**. Vas a descubrir una verdad incómoda: atacar es encontrar UNA
> puerta abierta; defender es cerrarlas TODAS.

---

## Por qué este laboratorio

El defensor juega un partido distinto. El atacante necesita un solo error; el
defensor tiene que eliminar **toda la superficie**. Y hay una diferencia más
sutil: el atacante demuestra con una captura ("mirá, entré"), el defensor
demuestra con un **argumento** ("esto ya no se puede, y acá está la prueba").

Este lab invierte la mecánica del curso:

- En los labs ofensivos, la flag estaba **escondida en el servicio** y la
  sacabas atacando.
- Acá, la flag la **entrega el atacante del docente** (`verificar-defensa.py`)
  cuando tu parche logra que su ataque **ya no funcione**. La flag es la
  constancia de que cerraste la puerta.

> **Atacar enseña dónde están las puertas. Defender enseña cuánto cuesta
> cerrarlas bien** — sin romper la app, sin mentirte, con evidencia.

## Objetivos de aprendizaje

1. Traducir hallazgos ofensivos (labs 05–07) en **parches concretos** de código.
2. Endurecer una app web: info leaks, endpoints de debug, rutas sensibles,
   SQLi, path traversal.
3. Distinguir mitigación **real** de mitigación cosmética (esconder ≠ arreglar).
4. Verificar defensas con la mentalidad del atacante: re-correr el ataque.
5. Documentar cada fix como un hallazgo cerrado: antes/después, con evidencia.

## Cómo se juega

```bash
./ctf lab extra3        # te muestra los 3 pasos
```

1. **Mirá el ataque funcionar** contra el objetivo roto:

   ```bash
   python3 labs/labextra3-hardening/verificar-defensa.py
   # 0/5 defensas correctas — todo vulnerable
   ```

2. **Copiá el objetivo a tu entrega y parchalo ahí.** El original NO se toca
   (es la referencia rota):

   ```bash
   mkdir -p entregas/labextra3/grupoXX
   cp -r labs/labextra3-hardening/objetivo entregas/labextra3/grupoXX/objetivo
   ```

3. **Re-corré el ataque contra tu copia** hasta llegar a 5/5:

   ```bash
   python3 labs/labextra3-hardening/verificar-defensa.py \
     --dir entregas/labextra3/grupoXX/objetivo
   ```

Cada defensa correcta te da su flag:

```bash
./ctf submit extra3 D1 'FLAG{...}'
./ctf status extra3
```

## Las cinco defensas

La app (`objetivo/server.py`) tiene los cinco problemas marcados con comentarios
`D1`–`D5`. Son los mismos hallazgos que vos explotaste en los labs 05–07:

| Defensa | Problema | Qué se espera | Trampa típica |
|---|---|---|---|
| **D1** | El header `Server` canta `PhantomServer/2.4.1-debug` | El banner ya no identifica producto ni versión | Creer que esto es "seguridad por oscuridad" (¿lo es? → P3) |
| **D2** | `/api/status` expone `debug:true`, rutas y PID en producción | Ese endpoint no existe o no expone nada sensible | Dejarlo "pero con menos datos" |
| **D3** | `robots.txt` delata `/backup` y la ruta responde 200 sin auth | `/backup` no responde sin autorización; robots no la lista | Solo sacarla del robots (¿alcanza? → P2) |
| **D4** | `/login` concatena strings en el SQL | Consulta **parametrizada** (`?`, no f-strings) | Filtrar comillas con replace (¿bypasseable? → P4) |
| **D5** | `/descargar?archivo=` concatena y lee cualquier path | El acceso queda **confinado** al directorio de descargas | Bloquear el string `..` (¿y `%2e%2e`? ¿y `....//`?) |

Reglas del juego:

- **La app tiene que seguir funcionando.** `/` responde, el login legítimo
  (`admin` / `sup3r-s3cr3t0`) sigue entrando, `/descargar?archivo=manual.txt`
  sigue descargando. Un parche que rompe la funcionalidad no es un parche: es
  un apagón. (El verificador no lo chequea; la rúbrica sí.)
- Podés reescribir lo que quieras **dentro de tu copia**. No agregar
  dependencias externas: stdlib solamente.
- Las flags del verificador demuestran que *bloqueaste*; el informe demuestra
  que *entendiste*.

## Preguntas de análisis (en `entregable.md`)

1. **P1.** Elegí una de tus cinco defensas y mostrá el **antes/después**:
   ataque que funcionaba (salida), parche (diff), ataque bloqueado (salida).
2. **P2.** En D3: ¿qué diferencia hay entre *sacar la ruta del robots.txt* y
   *proteger la ruta*? ¿Cuál de las dos es la defensa real y por qué?
3. **P3.** D1 es solo ocultar información. ¿Es una defensa "real"? Argumentá con
   el concepto de **seguridad por oscuridad**: cuándo ayuda y cuándo engaña.
4. **P4.** En D4: un compañero propone `user.replace("'", "")` como fix.
   Explicá por qué no alcanza y por qué la consulta parametrizada **sí** es la
   solución estructural.
5. **P5.** De los cinco problemas, ¿cuál era el más grave y por qué? Rankealos
   por impacto y justificá el #1 como lo harías en un informe a gerencia.

## Qué se entrega

En `entregas/labextra3/grupoXX/`:

- `objetivo/server.py` — tu copia **parchada** (el diff contra el original es
  parte de la evaluación).
- `informe.md` — a partir de `docs/entregable.md`: tabla antes/después de cada
  defensa, las 5 preguntas, captura del verificador en 5/5 y de
  `./ctf status extra3`.
- **Evidencia** según `docs/PROTOCOLO-EVIDENCIA.md`: `evidencia/comandos.txt`,
  `evidencia/salidas/` (incluí la salida del verificador 0/5 inicial y la 5/5
  final), declaración de IA.

La rúbrica está en [`docs/rubrica.md`](docs/rubrica.md). **Leela antes de
empezar.**

## Uso responsable

Los parches los escribís vos; las verificaciones corren contra tu propia copia,
en tu máquina. Las técnicas del verificador (SQLi, traversal, info leaks) son
las de los labs 05–07: solo se practican contra objetivos propios o de la
cátedra (Ley 26.388).
