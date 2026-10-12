# Licencias

Este repositorio usa **doble licencia** — una para el código, otra para el
material educativo. Es la práctica estándar en repos que mezclan las dos cosas.

**Copyright © 2026 Fernando Boiero — UTN Facultad Regional Villa María.**

---

## 1. Código → GNU AGPL-3.0-or-later

Todo lo **ejecutable** está bajo la [GNU Affero General Public License v3.0 o
posterior](LICENSE):

- El motor: `ctf`, `Makefile`, `bin/`, `entorno/`.
- Los scripts y esqueletos de código: `**/*.py`, `**/*.sh`, `docs/*.py`.
- Los `Dockerfile` y `server.py` de los targets.

Cada archivo de código lleva el encabezado:

```
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Fernando Boiero — CyberLab UTN FRVM
```

La AGPL exige que, si distribuís una versión modificada (incluso sirviéndola por
red), publiques el código fuente correspondiente bajo la misma licencia.

## 2. Documentación y material educativo → CC-BY-SA-4.0

Todo el **material del curso** está bajo la
[Creative Commons Atribución-CompartirIgual 4.0 Internacional](LICENSE-DOCS):

- Los enunciados y guías: `labs/**/README.md`, `labs/**/docs/*.md`.
- La documentación: `docs/*.md` (guías, novedades, banco de retos, teoría, etc.).
- Los datos y artefactos de evidencia: `labs/**/caso/**`, `labs/**/data/**`.
- Este `README.md` y los archivos de texto explicativos.

Podés **usarlo, adaptarlo y compartirlo** —incluso para otra cátedra— siempre que:

- **Atribuyas** al autor original (abajo el modelo de cita), y
- **Compartas igual**: las obras derivadas mantienen esta misma licencia CC-BY-SA-4.0.

### Cómo citar

> *CyberLab UTN — Laboratorios de Seguridad Informática*, Fernando Boiero
> (UTN FRVM, 2026). Bajo CC-BY-SA-4.0.
> Fuente: https://github.com/fboiero/LabsSeguridadInformatica2026

---

## Resumen

| Qué | Licencia | Archivo |
|---|---|---|
| Código (motor, scripts, targets) | AGPL-3.0-or-later | [`LICENSE`](LICENSE) |
| Documentación y material educativo | CC-BY-SA-4.0 | [`LICENSE-DOCS`](LICENSE-DOCS) |

Si tenés dudas sobre qué licencia aplica a un archivo puntual, abrí un Issue.
