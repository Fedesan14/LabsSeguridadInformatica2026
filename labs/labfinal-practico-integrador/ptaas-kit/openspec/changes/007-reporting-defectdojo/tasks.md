# Tasks — Change 007

## Spec y diseño
- [ ] 1.1 `design.md`: estructura del informe, versionado, qué sale hacia DefectDojo
- [ ] 1.2 Delta de `reporting` con ≥ 4 Requirements nuevos
- [ ] 1.3 Revisión cruzada

## Implementación
- [ ] 2.1 Tests que fallan para armado del informe desde hallazgos y bitácora
- [ ] 2.2 Construcción del informe con referencias a evidencia en bitácora
- [ ] 2.3 Validación de vectores CVSS v4.0 y presentación junto a EPSS
- [ ] 2.4 Resumen ejecutivo y estructura PTES §7
- [ ] 2.5 Exportación a DefectDojo o a su formato de importación
- [ ] 2.6 Gate de entrega conectado a la CLI de aprobación

## Verificación
- [ ] 3.1 Test: hallazgo sin CWE/CVSS/remediación → falla indicando el campo
- [ ] 3.2 Test: estado "validado" vs "no validado" visible en el informe
- [ ] 3.3 Test: entrega sin aprobación → rechazada
- [ ] 3.4 Test: el informe no contiene datos sensibles del lab (lista de patrones)
- [ ] 3.5 Recorrido end-to-end con un solo comando contra el lab
- [ ] 3.6 Archivar el delta en `openspec/specs/reporting/spec.md`
