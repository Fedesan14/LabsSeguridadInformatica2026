# Laboratorio 09 — Agentes de pentest

**Unidad 9** · Inteligencia artificial aplicada a la seguridad ofensiva
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/lab09/grupoXX/`
**Entorno:** Docker + una API de LLM (Claude u OpenAI) — o el motor `mock` sin key

> **El gran final.** Recorriste recon (05), enumeración (06), explotación (07) y
> post-explotación (08) **a mano**. Ahora construís un **agente de IA** que
> orquesta todo eso. Y acá se ve por qué el orden importaba: **no podés dirigir
> un agente que hace lo que vos no sabés hacer.** Hacé los labs 05–08 primero.

---

## El escenario

PhantomCorp levantó un nuevo servicio y te pide una auditoría. En vez de correr
las tools una por una, vas a soltar un **agente**: un programa que usa un LLM para
**decidir** qué herramienta correr, mirar el resultado, y decidir el siguiente
paso — solo, en un loop, hasta reportar los hallazgos.

Pero un agente ofensivo sin control es peligroso. La otra mitad del lab es
ponerle **guardrails**: que solo toque lo autorizado, con las tools que vos le
diste, dentro de un límite de pasos. **Vos dirigís; el agente ejecuta.**

---

## Por qué este laboratorio

Un "agente" suena mágico. No lo es. Es este loop:

```
   ┌────────────────────────────────────────────────┐
   │  1. el LLM decide una accion (¿qué tool corro?) │
   │  2. ejecutamos la tool  (con GUARDRAILS)         │
   │  3. le devolvemos el resultado al LLM            │
   │  4. volver a 1, hasta que diga "terminé"         │
   └────────────────────────────────────────────────┘
```

El LLM aporta el **razonamiento** (qué conviene hacer ahora). Tu código aporta
las **manos** (las tools) y los **límites** (los guardrails). Eso es todo. Y por
eso los labs anteriores eran obligatorios: el LLM propone un `nmap -sV`, pero si
vos no sabés leer un `nmap -sV`, no vas a poder validar si el agente está
haciendo bien o cualquier cosa. **La IA es una herramienta. El humano dirige.**

> Regla del lab: **un agente no te exime de saber. Te exige saber MÁS**, porque
> ahora tenés que evaluar decisiones, no solo ejecutarlas.

---

## Objetivos de aprendizaje

1. Explicar el loop de **tool-use** de un agente y sus componentes (LLM, tools,
   resultados, condición de fin).
2. Implementar el loop de un agente (completar el esqueleto) y correrlo.
3. Diseñar y justificar **guardrails**: alcance, allowlist de tools, límite de
   pasos.
4. Configurar el agente de forma **agnóstica** al proveedor (Claude / OpenAI /
   mock) vía variables de entorno.
5. **Auditar críticamente** un agente: dónde acierta, dónde se equivoca, y por
   qué el juicio humano sigue siendo imprescindible.

---

## Requisitos y preparación

- Docker (como siempre).
- **Opcional pero recomendado:** una API key de **Claude** (`ANTHROPIC_API_KEY`)
  o de **OpenAI** (`OPENAI_API_KEY`). Sin key, corré con el motor **`mock`**, que
  simula las decisiones del agente de forma offline: vas a ver el loop funcionar
  igual, solo que el "razonamiento" es fijo en vez de venir de un LLM.

```bash
./ctf lab 09          # levanta el target capstone
# exportá tu proveedor y key ANTES de entrar a la consola (o usá mock):
export LLM_PROVIDER=claude   ANTHROPIC_API_KEY=sk-ant-...    # o
export LLM_PROVIDER=openai   OPENAI_API_KEY=sk-...           # o
export LLM_PROVIDER=mock                                     # sin key
make shell            # entrás a la consola (te lleva LLM_PROVIDER y la key)
cd /repo/labs/lab09-agentes/src
python3 agente_pentest.py
```

> **Guardrail del mundo real:** tu API key es un secreto. **Nunca** la subas al
> repo ni la pegues en un archivo versionado. Va en una variable de entorno.
> Ver `.gitignore`.

> **Regla de oro.** El agente solo tiene permitido `phantomcorp`. Ese límite está
> en el código (guardrail) y no es negociable. Ley 26.388.

---

## Parte 1 · TEORÍA — anatomía de un agente

Tres piezas, en tres archivos (`src/`):

- **`llm.py`** — el **cerebro** intercambiable. Habla con Claude, con OpenAI o con
  el motor mock, detrás de una **misma interfaz**. El agente no sabe (ni le
  importa) cuál está atrás. Eso es diseño agnóstico: acoplás a una interfaz, no a
  un proveedor.
- **`herramientas.py`** — las **manos** y los **límites**. Las tools (`nmap_scan`,
  `http_get`, `http_post`) y, sobre todo, el **guardrail** de alcance: toda tool
  valida el objetivo antes de actuar.
- **`agente_pentest.py`** — el **loop** que las une.

El **guardrail** es la parte que más te va a hacer pensar. Un agente que puede
correr nmap es útil. Un agente que puede correr nmap **contra cualquier IP** es un
arma. La diferencia son diez líneas de validación de alcance. Escribilas bien.

---

## Parte 2 · EJEMPLOS

**Ejemplo A — El agente que se fue de scope.** En pruebas reales de agentes
ofensivos, un error clásico es que el LLM "decide" escanear un host que vio
mencionado en un resultado (un dominio de terceros, una IP externa). Sin
guardrail, el agente lo hace. Con guardrail, lo intenta y **se lo bloquea**. Vas a
ver exactamente esto en el R4.

**Ejemplo B — Alucinación con confianza.** Un LLM puede "reportar" una
vulnerabilidad que no existe, con lujo de detalle. Si no sabés validar (labs
05–08), te la comés. El agente acelera; no reemplaza tu criterio.

**Ejemplo C — El agente que encadena.** Lo potente: el LLM ve en un resultado
"pedí el token en /api/token", pide el token, y lo usa en el siguiente paso. Ese
**encadenamiento** autónomo es lo que un script fijo no hace. Lo vas a ver en el R5.

---

## Parte 3 · TOOLS Y CONFIGURACIÓN

### 3.1 Elegir el motor (agnóstico)

```bash
export LLM_PROVIDER=mock      # offline, sin key (para probar el loop)
export LLM_PROVIDER=claude ; export ANTHROPIC_API_KEY=sk-ant-...
export LLM_PROVIDER=openai ; export OPENAI_API_KEY=sk-...
# opcional: export LLM_MODEL=... para elegir modelo
```

### 3.2 Correr el agente de referencia

```bash
cd /repo/labs/lab09-agentes/src
python3 agente_pentest.py
```

Miralo trabajar: cada paso imprime qué tool corrió y qué obtuvo. Las flags
aparecen en los resultados de las tools.

### 3.3 Leer el guardrail

Abrí `herramientas.py` y leé `_verificar_alcance()`. Entendé **antes de correr
nada** qué hace cuando el objetivo está fuera de `ALCANCE`. Ese es el corazón de
la seguridad del agente.

---

## Parte 4 · PRÁCTICA

Corré el agente (mock o con tu key) y capturá las flags que reporta. Después,
completá **tu** agente.

| Reto | Qué demuestra | Cómo |
|---|---|---|
| **R1** | El agente hace recon | Corré `agente_pentest.py`. La primera flag sale del recon inicial. |
| **R2** | El agente enumera y sigue pistas | El agente lee `robots.txt` y va a la ruta oculta. |
| **R3** | El agente detecta una API expuesta | Aparece al tocar `/api/debug`. |
| **R4** | El guardrail funciona | El agente intenta salir de alcance (`8.8.8.8`) y el guardrail lo **bloquea**, devolviendo esta flag. Leé por qué. |
| **R5** | Encadenamiento (tu esqueleto) | Completá `agente_esqueleto.py` (los TODO del loop). Cuando funcione, encadena `/api/token` → `POST /api/vault` y trae el flag capstone. |

```bash
./ctf submit 09 R1 'FLAG{...}'
./ctf status 09
```

> R1–R4 salen con `agente_pentest.py` (referencia). **R5 exige completar tu
> propio `agente_esqueleto.py`** — ese es el punto del lab.

---

## Parte 5 · ANÁLISIS CRÍTICO — el entregable (la nota)

### A. Tu agente

Entregá `agente_esqueleto.py` completado y funcionando (que traiga el flag R5).

### B. Auditoría del agente

Corriste un agente ofensivo. Ahora **criticalo** en `informe.md`:

1. **Transcript.** Pegá la corrida del agente (mock o con key). Marcá cada
   decisión: ¿fue la que vos habrías tomado?
2. **Aciertos y errores.** ¿Dónde el agente fue eficiente? ¿Dónde perdió pasos,
   repitió, o hubiera necesitado algo que no tenía?
3. **El guardrail.** Explicá qué pasó en el R4 y por qué el guardrail es
   imprescindible. ¿Qué otros guardrails le agregarías?

### Preguntas de análisis

1. **P1.** Describí el loop de tool-use con tus palabras y con lo que viste en la
   corrida.
2. **P2.** ¿Qué aporta el LLM que un script fijo (como el `recolector.py` del Lab
   08) no puede? ¿Y qué hace mejor el script?
3. **P3.** El diseño es agnóstico al proveedor. ¿Qué ventaja concreta da eso?
   ¿Contra qué se acopla el agente en vez de al proveedor?
4. **P4.** Un agente ofensivo autónomo: nombrá **dos riesgos** reales y el
   guardrail que mitiga cada uno.
5. **P5.** Cerrá el curso: ¿por qué hacer los labs 05–08 a mano fue requisito
   para este? ¿Qué no podrías hacer con el agente si no supieras pentesting?

---

## Qué se entrega

En `entregas/lab09/grupoXX/`: `informe.md` (auditoría + P1–P5 + transcript),
`src/agente_esqueleto.py` (completado) y `research.md`. **Nunca** subas tu API
key. Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Un agente ofensivo automatiza intrusión: fuera del lab, el daño (y el delito) se
automatiza con él. El alcance del agente está limitado por código **a propósito**.
No lo levantes. Solo la cátedra. Ley 26.388.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
