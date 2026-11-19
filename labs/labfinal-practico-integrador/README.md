# Práctico Final — Engagement integrador

**Cierre del práctico** · integra las Unidades 5 a 10
**Modalidad:** grupos de 4 a 5 · **Entorno:** Docker
**Entrega:** fork + Pull Request en `entregas/final/grupoXX/`

> Esto no es un lab guiado. Es un **engagement**: te dan un objetivo y un alcance,
> y tenés que auditarlo **de punta a punta** con todo lo que aprendiste — y
> entregar un **informe de pentest profesional**. Poco hand-holding: para eso
> hiciste los diez labs.

---

## 🤖 Variante capstone avanzada — Desafío PTaaS (con agentes de IA)

Además del engagement clásico de arriba, hay una **variante de autor** mucho más
ambiciosa: en vez de *hacer* el pentest a mano, **construís la plataforma** que lo
hace — un *Pentest as a Service* gobernado por un swarm de agentes, con
autorización determinista, bitácora y validación en sandbox. Es un proyecto
spec-driven de ~15 días, pensado para equipos.

- **Carpeta:** [`ptaas-kit/`](ptaas-kit/) · empezá por su [`README.md`](ptaas-kit/README.md)
- **Qué hay que hacer:** [`docs/enunciado-alumnos.md`](ptaas-kit/docs/enunciado-alumnos.md)
- **Cómo construirlo:** [`docs/marco-teorico.md`](ptaas-kit/docs/marco-teorico.md) · [`docs/plan-15-dias.md`](ptaas-kit/docs/plan-15-dias.md)
- **Cómo se evalúa:** [`docs/rubrica-evaluacion.md`](ptaas-kit/docs/rubrica-evaluacion.md)
- **Funciona con Claude Code o con opencode:** ver [`AGENTS.md`](ptaas-kit/AGENTS.md)
- **Presentación del desafío:** [`presentacion/ptaas-desafio.pptx`](ptaas-kit/presentacion/ptaas-desafio.pptx)

> Esta variante es un proyecto de ingeniería de seguridad, no un CTF. El foco no
> es romper: es **diseñar el control** que hace el pentest seguro y auditable.

---

## El encargo

PhantomCorp te contrata para una auditoría de caja negra de su nuevo sistema
**"Clientes"**. No te dan credenciales ni documentación: solo el objetivo en la
red del lab (`phantomcorp`) y esta autorización.

Tu trabajo: **comprometer el sistema y demostrar el impacto**, siguiendo la cadena
completa, y **documentarlo** como lo haría una consultora de verdad.

### Reglas del engagement (Rules of Engagement)

- **Alcance:** únicamente el host `phantomcorp` del lab. Nada más.
- **Ventana:** la que fije la cátedra.
- **Permitido:** recon, enumeración, explotación, post-explotación sobre el target.
- **Prohibido:** cualquier acción destructiva (borrar datos, DoS). Sos un
  auditor, no un vándalo.
- **Fuera del lab:** nada. Ley 26.388.

---

## La cadena (4 hitos)

El sistema se cae en cuatro pasos encadenados; cada uno habilita el siguiente.
**No te doy los comandos** — usá lo de los labs 05–10.

| Hito | Fase | Qué demostrar |
|---|---|---|
| **R1** | Recon + Enumeración | Encontrá el portal interno que no está linkeado. |
| **R2** | Explotación | Entrá al portal sin credenciales válidas (foothold). |
| **R3** | Post-explotación | Del acceso, conseguí un secreto que habilite más. |
| **R4** | Impacto | Llegá a los "crown jewels": los datos de clientes. |

```bash
./ctf lab final          # levanta el objetivo
make shell               # tu consola
# ... auditá ...
./ctf submit final R1 'FLAG{...}'
./ctf status final
```

Las flags confirman que llegaste. **El informe es lo que se evalúa.**

---

## El entregable: informe de pentest profesional

Copiá [`docs/informe-pentest.md`](docs/informe-pentest.md) a
`entregas/final/grupoXX/informe.md` y completalo. Un informe de pentest real
tiene dos lectores y las dos secciones:

- **Resumen ejecutivo** — para quien decide (no técnico): qué encontraste, qué
  tan grave es, qué hacer. Sin jerga.
- **Detalle técnico** — para quien remedia: cada hallazgo con su **severidad
  (CVSS)**, **evidencia reproducible**, **impacto** y **remediación** concreta.

Más una **narrativa del ataque** (cómo encadenaste los cuatro hitos) y una
**conclusión** con la postura de seguridad general.

> Un pentest sin informe no sirve de nada. La habilidad técnica se demuestra
> rompiendo; el **valor profesional** se demuestra comunicando lo que rompiste de
> forma que alguien lo pueda arreglar.

---

## Qué se entrega

En `entregas/final/grupoXX/`:
- `informe.md` — el informe de pentest completo (a partir del template).
- Evidencia — capturas/salidas que respaldan cada hallazgo (guardá en `/loot`).
- Captura de `./ctf status final` con los 4 hitos.

Rúbrica en [`docs/rubrica.md`](docs/rubrica.md). **Leela antes de empezar.**

## Uso responsable

Autorización acotada al target del lab. Todo lo demás es delito (Ley 26.388). Este
es el mensaje final del curso: la diferencia entre un pentester y un delincuente
es **la autorización, el alcance y la ética**. Nunca lo olvides.
