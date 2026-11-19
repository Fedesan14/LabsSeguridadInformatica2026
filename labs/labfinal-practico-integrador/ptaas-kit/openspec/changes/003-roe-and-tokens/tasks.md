# Tasks — Change 003

## Spec y diseño
- [ ] 1.1 `design.md`: formato del RoE, validaciones, representación de aprobación
- [ ] 1.2 Delta de `authorization` con ≥ 5 Requirements nuevos (≥ 3 negativos)
- [ ] 1.3 Revisión cruzada del delta

## Implementación
- [ ] 2.1 Tests que fallan para RoE inválidos (sin alcance, ventana invertida, CIDR amplio, exclusión que anula todo)
- [ ] 2.2 `harness/roe.py`: modelo y parser (YAML) con errores explicativos
- [ ] 2.3 `harness/tokens.py`: emisor por fase con TTL de `policy.yaml`
- [ ] 2.4 Restringir la creación de `ScopeToken` al emisor y probarlo
- [ ] 2.5 Registrar emisiones y rechazos en la bitácora

## Verificación
- [ ] 3.1 Test: RoE válido → token solo de la fase pedida
- [ ] 3.2 Test: pedir una fase no autorizada → rechazo registrado
- [ ] 3.3 Test: exclusiones del RoE prevalecen sobre el alcance
- [ ] 3.4 Test: token vencido no se renueva solo
- [ ] 3.5 Tests adversariales A6, A7 y A8 de `docs/desafios-extension.md`
- [ ] 3.6 Archivar el delta en `openspec/specs/authorization/spec.md`
