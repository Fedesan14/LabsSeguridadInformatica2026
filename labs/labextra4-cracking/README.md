# Laboratorio Extra 4 — Cracking de contraseñas

**Actividad extra** (posterior al Lab 08; conecta con lo que implementaste en el Lab 03)
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/labextra4/grupoXX/`
**Entorno:** sin Docker — Python puro (stdlib)

> En la post-explotación del Lab 08 looteaste credenciales. Pero en el mundo
> real lo que se lootea casi nunca son contraseñas en claro: son **hashes**.
> La pregunta que define si ese loot vale algo es: *¿los hashes resisten o
> caen?* En este lab sos vos el que responde — con un cracker que escribís vos.

---

## Por qué este laboratorio

En el Lab 03 implementaste PBKDF2 y aprendiste que las contraseñas se guardan
con **hash lento + salt por usuario**. En este lab vas a sentir **por qué**,
desde el otro lado: vas a crackear un volcado real de hashes y a comprobar con
tu propio código que:

- **MD5/SHA-256 rápidos** caen por miles de millones de intentos por segundo.
- El **salt** mata las tablas precalculadas (rainbow tables) pero NO el
  diccionario: si la contraseña es `riverplate`, cae igual.
- Las **reglas de mangling** (`phantom` → `phantom2026`) cubren lo que el
  diccionario no tiene literal.
- **PBKDF2/bcrypt/Argon2** cambian la ecuación: 200.000 iteraciones por intento
  hacen que el diccionario entero sea inviable. *Eso* es lo que implementaste
  en el Lab 03 — ahora vas a entender qué le estabas negando al atacante.

> La métrica que importa no es "¿está hasheada?" sino **"¿cuántos intentos por
> segundo tolera?"**. Esa métrica la vas a medir vos, con tu cracker.

## Objetivos de aprendizaje

1. Parsear un volcado de hashes (`usuario:algo:salt:hash`) y razonar su formato.
2. Implementar un ataque de **diccionario** y uno de **reglas** (mangling).
3. Medir y comparar la velocidad de ataque por algoritmo (md5 vs sha256 vs
   pbkdf2) y explicar la diferencia en órdenes de magnitud.
4. Evaluar el impacto del loot: de hash crackeado a **datos abiertos**.
5. Conectar con la defensa: qué propiedades del almacenamiento hicieron caer
   (o resistir) cada cuenta.

## El caso

Dentro de `caso/`:

```
caso/
├── sombra.txt          # el volcado: 4 usuarios, 3 algoritmos distintos
├── diccionario.txt     # ~50 palabras (versión mini de rockyou)
├── loot/               # un archivo .enc por usuario — se abre con SU contraseña
└── generar_caso.py     # el script que lo generó (miralo: es la receta exacta)
```

Los cuatro usuarios son una radiografía de lo que pasa en cualquier empresa:

| Usuario | Algoritmo | Historia |
|---|---|---|
| `operador` | MD5 + salt | "uso la del club de siempre" |
| `analista` | SHA-256 + salt | "la mía es más larga, es segura" |
| `admin` | SHA-256 + salt | "le agregué el año, eso la hace fuerte" |
| `root` | PBKDF2, 200k iteraciones | el único que leyó el Lab 03 |

## Parte 1 · TEORÍA — la ecuación del atacante

Crackear es una carrera de números:

```
   tiempo para caer =  (contraseñas posibles) / (intentos por segundo)
```

Tres palancas:

1. **Espacio de contraseñas** (lo pone el usuario): `riverplate` está en
   cualquier diccionario. `Tq9#vL2!xZ8-wK7&nB4`, no.
2. **Velocidad del hash** (lo pone el defensor): MD5 es rapidísimo *a propósito*
   (fue diseñado para integridad, no para contraseñas). PBKDF2 es lento *a
   propósito*.
3. **El salt** (lo pone el defensor): no frena el diccionario, frena las
   **tablas precalculadas** y obliga a atacar **usuario por usuario**. Sin salt,
   un mismo cómputo rompe todas las cuentas iguales a la vez.

Las **reglas** merecen mención aparte: los humanos no eligen contraseñas
aleatorias, eligen *patrones*. `palabra + año`, `palabra + 123`, `Palabra` con
mayúscula. John the Ripper (`--rules`) y hashcat (`-r`) industrializaron esos
patrones. Tu `aplicar_reglas()` es una versión mini de eso.

## Parte 2 · PRÁCTICA

Completá los TODO de `src/cracker.py` (`hash_de`, `cargar_sombra`,
`aplicar_reglas`, `crackear`). `descifrar_loot()` viene hecha: leela, es la
mitad del lab.

```bash
cd labs/labextra4-cracking
python3 src/cracker.py crackear caso/sombra.txt caso/diccionario.txt
python3 src/cracker.py crackear caso/sombra.txt caso/diccionario.txt --reglas
python3 src/cracker.py descifrar caso/loot/operador.enc --password <la que encontraste>
```

| Reto | Qué entrena | Pista |
|---|---|---|
| **R1** | Diccionario puro contra MD5 | El operador usa "la del club". Mirá el diccionario con ojos argentinos. |
| **R2** | Diccionario puro contra SHA-256 | Misma técnica, otro algoritmo. Medí cuánto tarda vs. R1: la diferencia ES el tema del lab. |
| **R3** | Reglas de mangling | La contraseña del admin **no está literal** en el diccionario. Pero su lemma sí. Pensá como humano que cumple la política "tiene que tener números". |

Y hay un cuarto usuario. `root` no es un reto: **es la lección**. No vas a
encontrar su contraseña en este lab — y ese es exactamente el resultado que
tenés que poder explicar.

Entregá las flags (están dentro del loot de cada usuario):

```bash
./ctf submit extra4 R1 'FLAG{...}'
./ctf status extra4
```

## Preguntas de análisis (en `entregable.md`)

1. **P1.** Medí con tu cracker los **intentos/segundo** contra MD5, contra
   SHA-256 y contra PBKDF2 (con 20 intentos alcanza para estimar). Expresá la
   diferencia en órdenes de magnitud y explicá qué significa para un atacante
   con una GPU (10⁹ intentos/s en MD5).
2. **P2.** El salt no impidió que `operador` y `analista` cayeran. Entonces,
   ¿para qué sirve? Explicá qué ataque SÍ bloquea el salt (pista: tablas
   precalculadas + atacar todas las cuentas a la vez).
3. **P3.** La contraseña del admin cumplía la política típica (largo ≥ 8,
   mayúsculas/minúsculas, números). Cayó igual. ¿Qué le falta a esa política?
   ¿Qué recomendaría NIST SP 800-63B en vez de "complejidad"?
4. **P4.** Explicá por qué `root` no cayó en términos de **trabajo por
   intento**. Si el atacante tiene 1.000 GPUs, ¿cuánto tarda el diccionario
   entero contra PBKDF2-200k? Hacé la cuenta.
5. **P5.** Sos el defensor de PhantomCorp y este volcado es real. Listá en
   orden las acciones de respuesta (pista: la primera no es técnica, es de
   gestión de incidentes) y la política de almacenamiento correcta para el
   futuro.

## Qué se entrega

En `entregas/labextra4/grupoXX/`:

- `cracker.py` — tu implementación completa.
- `informe.md` — a partir de `docs/entregable.md`: tabla de resultados (quién
  cayó, con qué técnica, en cuánto tiempo), las 5 preguntas, captura de
  `./ctf status extra4`.
- **Evidencia** según `docs/PROTOCOLO-EVIDENCIA.md`: `evidencia/comandos.txt`,
  `evidencia/salidas/` (salida del crackeo y del descifrado de cada loot),
  declaración de IA.

La rúbrica está en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

El volcado es ficticio y vive en tu máquina. Crackear hashes ajenos — o incluso
*poseer* credenciales ajenas obtenidas sin autorización — tiene consecuencias
legales reales (Ley 26.388 y, según el caso, normativa de datos personales).
La técnica se practica acá o en plataformas autorizadas (HackTheBox, etc.).
