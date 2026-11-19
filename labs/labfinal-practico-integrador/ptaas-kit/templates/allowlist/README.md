# Allow-list de templates de Nuclei (curada)

Esta carpeta es la **única** fuente de templates que el adaptador `nuclei.safe_templates` puede usar (`-t templates/allowlist`).

## Cómo se incorpora un template
1. Proponerlo en un change OpenSpec (qué detecta, por qué es no destructivo).
2. Revisarlo línea por línea (`security-reviewer`): solo solicitudes de lectura (GET/HEAD/OPTIONS), sin fuzzing, sin fuerza bruta, sin pruebas de ejecución, sin OAST/Interactsh.
3. Registrar versión, autor de la revisión y fecha en `MANIFEST.md`.
4. Copiarlo a esta carpeta. Nada se descarga automáticamente de repositorios comunitarios.

## Reglas
- Etiquetas incluidas y excluidas: ver `harness/profiles.yaml`.
- Un test (`tests/test_adapters.py`) garantiza que el perfil no incluya etiquetas intrusivas.
- Candidatos iniciales sugeridos (a revisar, no incluidos): detección de tecnologías, cabeceras de seguridad ausentes, paneles de administración expuestos, archivos de configuración expuestos.
