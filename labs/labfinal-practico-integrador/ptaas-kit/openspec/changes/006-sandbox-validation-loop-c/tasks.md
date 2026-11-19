# Tasks — Change 006

## Spec y diseño
- [ ] 1.1 `design.md`: ciclo de vida del sandbox, límites, evidencia, timeout del Reviewer
- [ ] 1.2 Deltas de `validation` y `poc-catalog`
- [ ] 1.3 Revisión cruzada

## Implementación
- [ ] 2.1 Tests que fallan para el `Sender` aislado (sin red externa, sin estado)
- [ ] 2.2 Sandbox efímero: contenedor en red interna que implementa `Sender`
- [ ] 2.3 Límites de tiempo, tamaño y cantidad de solicitudes
- [ ] 2.4 Orquestación del loop C con `decide_validation`
- [ ] 2.5 CLI de aprobación: listar hallazgos pendientes, aprobar o rechazar con motivo
- [ ] 2.6 Registrar aprobación, verificación elegida y resultado en bitácora

## Verificación
- [ ] 3.1 Test: sin aprobación no se invoca el `Sender`
- [ ] 3.2 Test: verificación inexistente en catálogo → "no validado"
- [ ] 3.3 Test: el sandbox no alcanza hosts fuera del lab
- [ ] 3.4 Test: el sandbox se destruye aunque falle la verificación
- [ ] 3.5 Evals de validación ampliadas con casos donde la respuesta correcta es no actuar
- [ ] 3.6 Archivar deltas en `openspec/specs/`
