# Tasks — Change 002

## Spec y diseño
- [ ] 1.1 Escribir `design.md` (esquema SQLite, política de integridad, concurrencia)
- [ ] 1.2 Delta de `audit-log` con ≥ 4 Requirements nuevos y Scenarios negativos
- [ ] 1.3 Revisión del delta por otro integrante

## Implementación
- [ ] 2.1 Tests que fallan para persistencia y recuperación tras reinicio
- [ ] 2.2 `harness/audit.py`: almacenamiento append-only con hash encadenado
- [ ] 2.3 Impedir UPDATE/DELETE (trigger o capa de acceso) y probarlo
- [ ] 2.4 Verificador: `python -m harness.audit verify <archivo>`
- [ ] 2.5 Integrar con `Harness` sin cambiar su contrato público

## Verificación
- [ ] 3.1 Test: alterar una fila → el verificador falla
- [ ] 3.2 Test: borrar una fila intermedia → el verificador falla
- [ ] 3.3 Test: dos engagements no comparten registros
- [ ] 3.4 Test: escrituras concurrentes conservan la cadena
- [ ] 3.5 Mutation check del verificador y registro del resultado
- [ ] 3.6 Archivar el delta en `openspec/specs/audit-log/spec.md`
