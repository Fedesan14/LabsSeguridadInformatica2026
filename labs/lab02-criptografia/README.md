# Laboratorio 02 — Criptografía

**Unidad 2** · Criptografía
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab02/grupoXX/`

---

## Por qué este laboratorio

La criptografía no es "poner una contraseña". Es el conjunto de mecanismos que
garantizan **confidencialidad**, **integridad** y **autenticidad** de la
información. Y como todo mecanismo de seguridad, la mayoría de las fallas no están
en los algoritmos —que son públicos y sólidos— sino en **cómo se usan**.

Este lab ataca esa idea desde dos lados, como el lab01:

- **Parte A** — Analizás una falla criptográfica **real**: no un algoritmo roto,
  sino un mal uso.
- **Parte B** — Implementás en Python (biblioteca estándar) un cifrado clásico,
  lo **rompés** vos mismo, y después construís una autenticación de mensajes
  hecha bien.

> **Principio de Kerckhoffs.** Un sistema debe ser seguro aunque todo sobre él
> sea público, excepto la clave. Si tu seguridad depende de que nadie conozca el
> algoritmo, no tenés seguridad: tenés un secreto que se va a filtrar.

---

## Objetivos de aprendizaje

1. Distinguir confidencialidad, integridad y autenticidad, y qué primitiva
   criptográfica aporta cada una.
2. Diferenciar cifrado **simétrico** de **asimétrico**, y **cifrado** de
   **hashing** de **MAC**.
3. Implementar un cifrado XOR de clave repetida y **romperlo** por análisis de
   frecuencia, entendiendo por qué los cifrados clásicos fallan.
4. Explicar por qué `sha256(clave || mensaje)` es una MAC insegura y por qué
   **HMAC** es la forma correcta.
5. Justificar la comparación en **tiempo constante** de secretos.

---

## Requisitos

- Python 3.10+. **Solo biblioteca estándar** (`hashlib`, `hmac`, `secrets`).
- Git y GitHub. Haber leído [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

## Preparación

```bash
mkdir -p entregas/lab02/grupoXX
cp -r labs/lab02-criptografia/src  entregas/lab02/grupoXX/src
cp -r labs/lab02-criptografia/data entregas/lab02/grupoXX/data
cp labs/lab02-criptografia/docs/entregable.md entregas/lab02/grupoXX/informe.md
cd entregas/lab02/grupoXX
python3 data/generar_datos.py         # genera el reto a romper
python3 src/cripto.py xor --texto hola --clave K   # el esqueleto tiene que correr
```

---

## Parte A — Análisis de una falla criptográfica

### Caso asignado

Un caso por grupo. Si no te asignaron, usá `número_de_grupo mod 5`:

| # | Falla | Qué se hizo mal |
|---|---|---|
| 0 | **WEP (redes WiFi)** | IV corto y reutilizado sobre RC4 |
| 1 | **Adobe 2013** | contraseñas cifradas con ECB (¡el "pingüino"!) en vez de hasheadas |
| 2 | **Sony PS3 (ECDSA)** | reutilización del nonce `k` al firmar |
| 3 | **MD5 / colisiones** | uso de una función de hash rota para certificados |
| 4 | **Zoom "E2E" (2020)** | claves manejadas por el servidor; no era end-to-end real |

### Qué producir (en `informe.md`, Parte A)

- **A.1** — Qué prometía el sistema (qué propiedad decía garantizar).
- **A.2** — Cuál fue el **mal uso** concreto (no "el algoritmo era malo": el uso).
- **A.3** — Qué propiedad se rompió (confidencialidad / integridad / autenticidad)
  y **cómo se explotó**.
- **A.4** — La forma correcta de haberlo hecho, en una o dos oraciones.

**Cada afirmación con su fuente.** No vale "se dice que".

---

## Parte B — Implementación

Completá los `TODO` de `src/cripto.py`. La función `xor_cifrar()` ya está: leela.

### B.1 — Romper un cifrado clásico

```bash
python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)
```

Implementá `romper_xor_1byte()`: probá las 256 claves de un byte y elegí la que
produzca texto natural (por frecuencia de caracteres). Cuando funcione, vas a
leer el mensaje oculto de PhantomCorp. **La lección:** un cifrado de clave corta
se rompe por fuerza bruta trivial. La longitud y aleatoriedad de la clave importan.

### B.2 — Autenticación de mensajes: ingenuo vs. HMAC

Implementá `mac_ingenuo()`, `mac_hmac()` y `verificar_mac()`.

```bash
python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo hmac
```

En el informe (Parte B) respondé:

- **B.2.1** — ¿Por qué `sha256(clave || mensaje)` permite un ataque de
  **length-extension**? Explicá qué podría falsificar un atacante **sin conocer
  la clave**.
- **B.2.2** — ¿Cómo lo resuelve HMAC estructuralmente?
- **B.2.3** — `verificar_mac()` usa `hmac.compare_digest`. ¿Qué ataque evita
  comparar en tiempo constante? Dá un ejemplo concreto.

---

## Autoevaluación (feedback instantáneo)

Mientras completás los `TODO`, chequeá tu avance sin esperar la corrección:

```bash
python3 src/verificar.py
```

**Verde** = va · **rojo** = revisá (te dice qué falló) · **gris** = todavía no lo
implementaste. No es la nota — es para que **iteres solo**, como con las flags de
los labs ofensivos.

---

## Qué se entrega

En `entregas/lab02/grupoXX/`: `informe.md` (Parte A + respuestas B) y
`src/cripto.py` completado (los cuatro TODO). El reto XOR resuelto, con el mensaje
en claro en el informe. Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Romper cifrado se practica **solo** sobre los datos de la cátedra. Ver
[`CONTRIBUTING.md`](../../CONTRIBUTING.md). Ley 26.388.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
