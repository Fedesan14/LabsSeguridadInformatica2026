## Qué cambia
<!-- Una o dos frases. Referenciá el change y el task: por ejemplo "002 · 2.4" -->

## Change y specs afectadas
- Change: `openspec/changes/<id>/`
- Specs/deltas tocados:

## Checklist
- [ ] El delta de spec fue revisado por otro integrante **antes** de implementar
- [ ] Hay un test por cada Scenario nuevo, incluido al menos un caso negativo de seguridad
- [ ] Vi fallar el test por la razón correcta antes de implementar
- [ ] `python -m pytest -q` en verde
- [ ] `python evals/run_evals.py --mode golden` en verde (y evals en vivo si cambié un prompt o un modelo)
- [ ] `python tools/progress.py` actualizado; `tasks.md` marcado
- [ ] Hice una mutación manual del control tocado y los tests la detectaron
- [ ] Pasé el diff por el agente `security-reviewer` y resolví o justifiqué cada punto
- [ ] Ninguna acción se ejecuta fuera de `Harness.invoke`; nada apunta fuera del laboratorio propio
- [ ] No hay secretos, claves ni datos reales en el diff

## Qué hizo mal la IA en este cambio (si algo)
<!-- Es parte del informe técnico: anotá errores detectados y cómo los encontraste -->
