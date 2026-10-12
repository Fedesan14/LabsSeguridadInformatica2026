# Laboratorio Extra — SSRF: Server-Side Request Forgery

**Actividad extra** (posterior al Lab 07, ideal antes o junto al 08)
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/labextra/grupoXX/`
**Entorno:** Docker (dos hosts en redes segmentadas, se levanta solo)

> PhantomCorp volvió a llamar. Migraron su intranet a una red interna
> "inaccesible desde afuera" y están tranquilos: *"si no se puede llegar, no se
> puede atacar"*. Tu trabajo es demostrarles que se equivocan — sin explotar
> nada en la intranet, sin conseguir una shell: solo pidiéndole **al propio
> servidor** que haga los pedidos por vos.

---

## Por qué este laboratorio

SSRF es la vulnerabilidad que mejor explica la seguridad moderna: la mayoría de
las arquitecturas confían en la **red interna** ("si viene de adentro, es de
confianza"). SSRF convierte al propio servidor en tu proxy: el atacante no toca
la red interna — **la toca el servidor por él**.

No es un tema exótico:

- Es **A10** en el OWASP Top 10 (2021).
- El 70% de los reportes críticos de bug bounty contra apps cloud involucran
  SSRF para leer el **metadata service** (`169.254.169.254`) y robar
  credenciales de la nube (Capital One, 2019: 100 millones de registros).
- Todo "preview de link", "importar desde URL", webhook o generador de PDF
  server-side es un SSRF en potencia.

La idea central:

> **El perímetro ya no es el límite. Si el servidor puede pedir, el atacante
> puede pedir a través del servidor.**

## Objetivos de aprendizaje

1. Explicar qué es SSRF y por qué rompe el modelo de confianza por red.
2. Identificar funcionalidades susceptibles (fetch, preview, import, webhooks).
3. Explotar un SSRF para leer recursos **internos**: `localhost` y otros hosts
   de la red del servidor.
4. Medir el impacto: acceso a datos que el atacante no debería alcanzar jamás.
5. Proponer mitigaciones concretas (allowlist, DNS pinning, segregación).

## Preparación

```bash
./ctf lab extra       # levanta web pública + intranet (redes segmentadas)
make shell            # consola del atacante
curl -s phantomcorp/  # el portal público
```

El mapa de red (igual filosofía que el Lab 08):

```
   atacante ──labnet──>  phantomcorp (web :80)  ──internalnet──>  phantomcorp-intra
        │                        │                                        ▲
        └─────────── ✗ NO hay ruta directa ──────────────────────────────┘
```

La intranet **no es alcanzable** desde tu consola. Comprobalo:

```bash
curl -s --max-time 3 phantomcorp-intra/   # timeout: no existe ruta
```

## Parte 1 · TEORÍA — el servidor como cómplice involuntario

Un SSRF ocurre cuando una aplicación **recibe una URL y la fetchea**, y el
atacante controla esa URL. El pedido sale **desde el servidor**, con la
identidad y la posición de red del servidor:

```
   vos ──> web: "fetcheame http://intranet/backups" 
              │
              └── el server (que SÍ está en la red interna) la fetchea
                  y te devuelve el contenido
```

Tres destinos clásicos a través de un SSRF:

| Destino | Qué hay | Por qué importa |
|---|---|---|
| `http://127.0.0.1:PUERTO` | Servicios que escuchan **solo en localhost** del server (paneles admin, métricas, debug) | "Solo localhost" deja de ser defensa: el SSRF *es* localhost |
| `http://host-interno` | Intranets, APIs internas, bases de administración | La segmentación de red se anula si un host de la DMZ fetchea arbitrario |
| `http://169.254.169.254` | Metadata de la nube (AWS/GCP/Azure) | Credenciales temporales de la instancia → compromiso total de la cuenta cloud |

La pauta para **detectar** un SSRF candidato: cualquier funcionalidad que
reciba una URL o un host — "previsualizar", "importar desde link", "avatar por
URL", webhooks, "probar conexión".

## Parte 2 · EJEMPLOS — cómo se ve en la vida real

**Ejemplo A — El preview de links.** Un chat muestra preview de las URLs que
pegás. El bot que fetchea corre dentro de la red corporativa. Alguien pega
`http://wiki.interna/planilla-sueldos` y el preview muestra el contenido a
todos los participantes del chat. **El bot tenía acceso; el atacante no.**

**Ejemplo B — Capital One (2019).** Una WAF mal configurada permitió un SSRF
contra el metadata service de AWS (`169.254.169.254`). De ahí salieron
credenciales temporales, y con esas credenciales, 100 millones de registros de
un bucket S3. La app no estaba "rota": hizo exactamente lo que le pidieron.

**Ejemplo C — El generador de PDF.** Una app que genera PDFs de páginas
"pasame la URL". `file:///etc/passwd` en algunos motores, o
`http://localhost:8080/actuator/env` en un Spring, y el PDF viene con el
contenido adentro.

En los tres casos el patrón es el mismo: **la confianza por ubicación de red
es una defensa ilusoria cuando un servicio fetchea URLs arbitrarias.**

## Parte 3 · PRÁCTICA — cazá las 3 flags

El portal de PhantomCorp tiene una herramienta de **previsualización de URLs**
para empleados (buscala en la home). El servidor fetchea la URL que le pases y
te muestra el contenido. Sin validación. Sin allowlist. Gracias, IT.

| Reto | Técnica | Pista |
|---|---|---|
| **R1** | SSRF a `localhost` | El server corre más cosas que el portal. Los paneles de admin suelen escuchar **solo en 127.0.0.1** "por seguridad". ¿Qué puertos internos podés sondear pidiéndole al server que los fetchee? (los errores de conexión también informan) |
| **R2** | SSRF a la red interna | Sabés que existe una intranet (el enunciado te lo dice; en la vida real la descubrís por OSINT o por errores bocones). Los nombres internos de PhantomCorp siguen el patrón que ya conocés de otros labs. |
| **R3** | Exfiltración de datos | La intranet tiene cosas que "había que borrar" y nadie borró. Leéla entera. |

Entregá cada una:

```bash
./ctf submit extra R1 'FLAG{...}'
./ctf status extra
```

### Preguntas de análisis (en `entregable.md`)

1. **P1.** Explicá con el diagrama de red de este lab por qué la frase *"la
   intranet no es alcanzable desde afuera"* dejó de ser cierta. ¿Qué componente
   la hizo alcanzable?
2. **P2.** En R1 usaste los **mensajes de error** para distinguir puerto
   cerrado de puerto abierto dentro de localhost. ¿Qué diferencia observaste?
   ¿Qué tiene eso de un **oráculo de escaneo de puertos**?
3. **P3.** ¿Qué información sensible cruzó el perímetro en R3? Redactá el
   hallazgo como lo harías en un informe profesional: activo afectado, vector,
   impacto, evidencia.
4. **P4.** Sos el defensor. Proponé **tres** mitigaciones concretas para este
   `/preview`, ordenadas de mejor a peor, y explicá qué limitación tiene cada
   una (pista: ¿alcanza con filtrar strings tipo "localhost"? ¿y
   `http://2130706433/`? ¿y un dominio que resuelve a 127.0.0.1?).
5. **P5.** Conectá con la nube: ¿qué es el metadata service `169.254.169.254`
   y por qué un SSRF en una app cloud es mucho más grave que en este lab?

## Qué se entrega

En `entregas/labextra/grupoXX/`:

- `informe.md` — a partir de `docs/entregable.md`: cadena de explotación de los
  3 retos (comandos + salidas), las 5 preguntas y captura de
  `./ctf status extra` completo.
- `research.md` — a partir de `docs/research.md`: investigá **un** caso real de
  SSRF (Capital One u otro) o el metadata service de una nube.

La rúbrica está en [`docs/rubrica.md`](docs/rubrica.md). **Leela antes de
empezar.**

## Uso responsable

Mismo marco de siempre: solo contra los contenedores de la cátedra, en tu
máquina. SSRF contra sistemas de terceros sin autorización escrita es delito en
Argentina (Ley 26.388). Y en cloud ni siquiera hace falta "romper" nada:
pedirle a un servidor que lea su propio metadata ya es acceso no autorizado.

---

## Retos bonus (opcional)

¿Te quedaste con hambre? En el [banco de retos
bonus](../../docs/BANCO-DE-RETOS.md) hay desafíos progresivos (★ / ★★ / ★★★)
para seguir: escaneo de puertos interno vía SSRF, bypass de filtros ingenuos
(¿`http://127.1/`? ¿decimal? ¿DNS rebinding?) y lectura de `file://`.
