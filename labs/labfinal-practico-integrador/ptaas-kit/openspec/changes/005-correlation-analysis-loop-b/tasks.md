# Tasks — Change 005

## Spec y diseño
- [ ] 1.1 `design.md`: snapshots, confianza, contradicciones, política de templates
- [ ] 1.2 Deltas de `correlation` y `vuln-analysis`
- [ ] 1.3 Revisión cruzada

## Implementación — correlación
- [ ] 2.1 Cliente de snapshot NVD (lectura offline) con tests
- [ ] 2.2 Cliente de snapshot EPSS con tests
- [ ] 2.3 `cwe.map` y normalización a ATT&CK cuando aplique
- [ ] 2.4 Correlador que produce `CandidateFinding` con evidencia

## Implementación — análisis
- [ ] 3.1 Adaptador `zap.baseline_scan` (fixtures + corrida contra el lab)
- [ ] 3.2 Curar y revisar ≥ 5 templates en `templates/allowlist/` y completar `MANIFEST.md`
- [ ] 3.3 Corrida de `nuclei.safe_templates` contra el lab
- [ ] 3.4 Orquestación del loop B con `decide_detection`

## Verificación
- [ ] 4.1 Test: candidato sin evidencia se rechaza
- [ ] 4.2 Test: dato ausente → `null`/`unknown`
- [ ] 4.3 Test: un template fuera de la allow-list no se ejecuta
- [ ] 4.4 Test: dos iteraciones sin evidencia nueva → `inconclusive`
- [ ] 4.5 Evals de correlación y análisis ampliadas (≥ 10 casos en conjunto)
- [ ] 4.6 Archivar deltas en `openspec/specs/`
