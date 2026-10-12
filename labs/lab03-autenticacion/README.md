# Laboratorio 03 — Autenticación y control de acceso

**Unidad 3** · Autenticación, identidad y control de acceso
**Modalidad:** grupos de 4 a 5 · **Entrega:** fork + PR en `entregas/lab03/grupoXX/`

> El título de esta unidad se ajusta al programa analítico de la cátedra; el
> laboratorio cubre el núcleo técnico de la autenticación.

---

## Por qué este laboratorio

La autenticación responde a **"¿sos quien decís ser?"**. Es la puerta de todo lo
demás: si se rompe, ningún otro control importa. Y se rompe **casi siempre por
implementación**, no por falta de teoría: contraseñas guardadas en claro, hashes
sin salt, comparaciones que filtran tiempo, segundo factor mal hecho.

- **Parte A** — Analizás una brecha de autenticación real.
- **Parte B** — Implementás almacenamiento de contraseñas **correcto** (PBKDF2 con
  salt) y un segundo factor **TOTP** (el de Google Authenticator), todo en Python
  estándar.

---

## Objetivos

1. Distinguir **autenticación** de **autorización** y los factores (algo que
   sabés / tenés / sos).
2. Explicar por qué una contraseña **nunca** se guarda en claro ni con un simple
   `sha256`, y qué agregan **salt** e **iteraciones**.
3. Implementar almacenamiento con **PBKDF2** y verificación en **tiempo constante**.
4. Implementar **TOTP** (RFC 6238) y explicar por qué el 2FA mitiga el robo de
   contraseñas.
5. Razonar sobre control de acceso: por qué se verifica **en el servidor**.

---

## Requisitos y preparación

Python 3.10+, solo stdlib (`hashlib`, `hmac`, `secrets`).

```bash
mkdir -p entregas/lab03/grupoXX && cp -r labs/lab03-autenticacion/src entregas/lab03/grupoXX/src
python3 src/auth.py hash --password hola     # el esqueleto debe correr
```

---

## Parte A — Análisis de una brecha de autenticación

Un caso por grupo (`número mod 4`):

| # | Caso | La falla |
|---|---|---|
| 0 | **LinkedIn 2012** | 6.5M contraseñas en SHA-1 **sin salt** → crackeadas masivamente |
| 1 | **RockYou 2009** | contraseñas en **texto plano**; hoy es la wordlist de fuerza bruta |
| 2 | **Credential stuffing** | reuso de contraseñas entre sitios; por qué el 2FA lo corta |
| 3 | **Ataques de timing** | fugas por comparación no constante de tokens/MAC |

En `informe.md` (Parte A): qué se guardó/comparó mal, cómo se explotó, y la forma
correcta. **Con fuentes.**

---

## Parte B — Implementación

Completá los `TODO` de `src/auth.py`. `hotp()` ya está: es la base de `totp()`.

### B.1 — Contraseñas

```bash
python3 src/auth.py hash   --password 'Phantom-2026!'
python3 src/auth.py verify --password 'Phantom-2026!' --registro 'pbkdf2_sha256$...'
```

Responder: **¿por qué salt por usuario?** (pensá en dos usuarios con la misma
contraseña) y **¿por qué muchas iteraciones?** (pensá en el atacante con GPUs).

### B.2 — Segundo factor (TOTP)

```bash
python3 src/auth.py totp --secret 12345678901234567890 --t 59   # debe dar 287082
```

Verificación contra el **vector oficial de RFC 6238**: con el secreto ASCII
`12345678901234567890` y `t=59`, el código de 6 dígitos es **287082** (los 8
dígitos del RFC son `94287082`). Si tu TOTP no da eso, algo está mal.

Responder: si un atacante te robó la contraseña (Parte A), **¿por qué el TOTP lo
frena?** ¿Y qué **no** protege el TOTP?

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

`informe.md` (Parte A + respuestas B) y `src/auth.py` completado.
Rúbrica en [`docs/rubrica.md`](docs/rubrica.md). Ley 26.388 · uso responsable.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
