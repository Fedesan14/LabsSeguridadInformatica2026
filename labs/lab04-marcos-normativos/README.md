# Laboratorio 04 — Marcos normativos y gestión de la seguridad

**Unidad 4** · Marcos normativos y gestión de la seguridad
**Modalidad:** grupos de 4 a 5 · **Entrega:** fork + PR en `entregas/lab04/grupoXX/`

---

## Por qué este laboratorio

Hasta acá viste **técnica**. Pero en una organización, la seguridad se **gestiona**:
se decide *qué proteger*, *cuánto invertir* y *contra qué marco medirse*. Sin
gestión, la técnica es esfuerzo sin rumbo — parcheás lo que te da miedo, no lo que
más importa.

- **Parte A** — Aplicás un **marco** real (ISO/IEC 27001 o NIST CSF) a un escenario.
- **Parte B** — Cuantificás y **priorizás riesgos** con números (ALE), y decidís
  qué control conviene con un ROI. Porque "poné un firewall" no es una decisión:
  una decisión es "este control evita $15k/año y cuesta $8k, conviene".

> **La seguridad es una función de gestión de riesgo, no una lista de tools.** No
> existe "seguro": existe "riesgo aceptable, medido y justificado".

---

## Objetivos

1. Ubicar los grandes marcos (**ISO/IEC 27001**, **NIST CSF**) y para qué sirve
   cada uno.
2. Mapear un escenario a las funciones/controles de un marco.
3. Cuantificar riesgo con **SLE**, **ARO** y **ALE**.
4. Justificar la inversión en un control con un **ROI de seguridad**.
5. Distinguir las cuatro respuestas al riesgo: **mitigar, transferir, aceptar,
   evitar**.

---

## Requisitos y preparación

Python 3.10+, solo stdlib.

```bash
mkdir -p entregas/lab04/grupoXX && cp -r labs/lab04-marcos-normativos/src entregas/lab04/grupoXX/src
python3 src/riesgo.py ale --sle 50000 --aro 0.4     # el esqueleto debe correr
```

---

## Parte A — Aplicar un marco

Elegí **uno** (ISO/IEC 27001 o NIST CSF) y aplicalo a **este** escenario:

> *PhantomCorp guarda datos de clientes (nombres, DNI, tarjetas). Tiene un
> servidor web público, empleados con acceso remoto, y backups en un disco en la
> oficina. No tiene MFA, ni política de contraseñas, ni plan de respuesta a
> incidentes.*

En `informe.md` (Parte A):
- **A.1** — Qué marco elegiste y por qué.
- **A.2** — Mapeá **cinco** debilidades del escenario a controles/funciones del
  marco (ej. NIST CSF: *Identify, Protect, Detect, Respond, Recover*; o dominios
  de controles de ISO 27001 Anexo A).
- **A.3** — Para cada una, la respuesta al riesgo elegida (mitigar/transferir/
  aceptar/evitar) **con justificación**.

---

## Parte B — Cuantificar y priorizar

Completá los `TODO` de `src/riesgo.py`.

```bash
python3 src/riesgo.py ale --sle 50000 --aro 0.4      # -> 20000.00
python3 src/riesgo.py roi --antes 20000 --despues 5000 --costo 8000   # -> 0.875
python3 src/riesgo.py priorizar --archivo riesgos.json
```

Creá un `riesgos.json` con **al menos cuatro** riesgos del escenario de la Parte A
(`{"nombre":..,"sle":..,"aro":..}`), corré `priorizar`, y en el informe (Parte B):

- **B.1** — El ranking por ALE. ¿Coincide con tu intuición? ¿Dónde no?
- **B.2** — Para el riesgo #1, proponé un control, estimá su costo y el ALE
  resultante, y calculá el ROI. ¿Conviene?
- **B.3** — Un riesgo donde la respuesta correcta sea **aceptar** o **transferir**
  (no mitigar), y por qué.

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

`informe.md` (Parte A + B), `src/riesgo.py` completado y tu `riesgos.json`.
Rúbrica en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

Los datos del escenario son ficticios. Ley 26.388 · ver `CONTRIBUTING.md`.

---

## Retos bonus (opcional)

¿Estas flags te quedaron cortas? En el
[banco de retos bonus](../../docs/BANCO-DE-RETOS.md) hay **3 desafíos más para
este lab**, con más herramientas y dificultad progresiva (★ / ★★ / ★★★). No
cuentan para la aprobación, pero es donde te hacés bueno de verdad.
