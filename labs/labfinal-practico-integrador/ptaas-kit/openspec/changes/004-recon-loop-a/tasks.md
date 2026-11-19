# Tasks — Change 004

## Spec y diseño
- [ ] 1.1 `design.md`: schemas de salida, versionado del grafo, manejo de errores
- [ ] 1.2 Deltas de `asset-discovery` y `tool-adapters`
- [ ] 1.3 Revisión cruzada

## Implementación
- [ ] 2.1 Grabar fixtures de salida de subfinder y httpx (contra el lab o sintéticas)
- [ ] 2.2 `harness/adapters/subfinder_adapter.py` con tests de argv y de salida
- [ ] 2.3 `harness/adapters/httpx_adapter.py` con tests de argv y de salida
- [ ] 2.4 Modelo `AssetGraph` y persistencia
- [ ] 2.5 Orquestación del loop A usando `decide_recon`
- [ ] 2.6 Descubrimientos fuera de alcance: registrar y no sondear

## Verificación
- [ ] 3.1 Test: loop A termina por grafo estabilizado
- [ ] 3.2 Test: loop A termina por tope
- [ ] 3.3 Test: un activo fuera de alcance nunca llega a un adaptador
- [ ] 3.4 Test: el adaptador respeta el rate limit
- [ ] 3.5 Corrida real contra el lab y bitácora verificada con `audit verify`
- [ ] 3.6 Archivar deltas en `openspec/specs/`
