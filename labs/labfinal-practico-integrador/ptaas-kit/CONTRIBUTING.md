# Cómo trabajar en este repositorio

## Antes de tocar nada
1. Leé `README.md`, `CLAUDE.md` y `docs/marco-teorico.md`.
2. Instalá y verificá: `pip install -r requirements-dev.txt && python -m pytest -q && python evals/run_evals.py --mode golden`.
3. Corré `python tools/progress.py` para ver dónde está el proyecto.

## Flujo de ramas
- `main` siempre está en verde y solo recibe cambios por pull request.
- Una rama por change o task: `change/003-roe-and-tokens`, `fix/guard-ipv6`.
- Commits chicos que referencien el task: `003 · 2.2: parser de RoE con ventana invertida`.
- Cada pull request necesita **otra persona** que lo revise (no quien lo escribió).

## Orden de trabajo (no se negocia)
1. **Spec**: delta en `openspec/changes/<id>/specs/` con al menos un Scenario negativo.
2. **Revisión** del delta por otro integrante.
3. **Test** que falla por la razón correcta.
4. **Código** mínimo para que pase.
5. **Revisión de seguridad** del diff y mutación manual del control tocado.
6. **Archivar**: al mergear, el delta pasa a `openspec/specs/`.

## Reglas éticas y de seguridad
- Todo ejecuta solo contra el laboratorio propio (`lab/`).
- Ninguna acción fuera de `Harness.invoke`; sin scope token vivo no hay acción; todo queda en bitácora.
- El catálogo de verificaciones es inerte y de laboratorio. Ampliarlo exige change, revisión y aprobación humana registrada.
- Nada de secretos, claves ni datos reales en commits. Si se filtra algo, avisá y rotalo: borrar el commit no alcanza.

## Qué hacer ante dudas
Abrí un issue con la plantilla "Task de un change" o escribile al docente. Si el agente propone saltear un gate o ampliar el alcance, parate y consultá.
