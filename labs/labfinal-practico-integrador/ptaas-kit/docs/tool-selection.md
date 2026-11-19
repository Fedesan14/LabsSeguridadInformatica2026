# Selección de herramientas — PTaaS (MVP)

## Resumen
Para el MVP se eligen **7 herramientas/fuentes**, todas con salida parseable y capacidad de operar de forma no destructiva: **subfinder, httpx, nmap, NVD/EPSS (feeds), OWASP ZAP, Nuclei y DefectDojo**. Cada una entra al sistema solo como **adaptador tipado** invocado por `Harness.invoke`. El resto queda para después del MVP o se descarta con motivo.

> Las licencias de la tabla son las que conozco; **verificalas en el repositorio de cada proyecto antes de adoptarlas o redistribuirlas**.

## Criterios de selección
1. **Licencia** compatible con uso comercial como servicio (permisiva o uso como proceso externo).
2. **Salida parseable** (JSON/JSONL/XML) para validar contra schema.
3. **Modo no destructivo** configurable y rate limit controlable.
4. **Madurez y actividad** del proyecto.
5. **Cobertura de estándar:** qué fase de PTES / qué guía (WSTG, NIST 800-115, OSSTMM) soporta.
6. **Adaptador estable:** CLI con argv fijo o API.

## Matriz por fase

| Fase PTES | Capability | Herramienta | Licencia (a verificar) | Salida | Estándar/guía | MVP |
|---|---|---|---|---|---|---|
| Intelligence Gathering (pasivo) | `subfinder.enum` | subfinder | MIT | JSONL | PTES §2, OSSTMM | Sí |
| Intelligence Gathering (activo) | `httpx.probe` | httpx | MIT | JSONL | PTES §2 | Sí |
| Intelligence Gathering (activo) | `nmap.service_scan` | nmap | NPSL (licencia propia de Nmap) | XML | PTES §2, NIST 800-115 | Sí* |
| Threat Modeling / correlación | `cve.lookup` | feed NVD | datos públicos | JSON | CVE, CWE | Sí |
| Threat Modeling / correlación | `epss.lookup` | feed EPSS | datos públicos | JSON | EPSS | Sí |
| Threat Modeling / correlación | `cwe.map` | catálogo CWE | datos públicos | JSON | CWE | Sí |
| Vulnerability Analysis (web) | `zap.baseline_scan` | OWASP ZAP | Apache-2.0 | JSON | OWASP WSTG | Sí |
| Vulnerability Analysis (web/red) | `nuclei.safe_templates` | Nuclei | MIT | JSONL | NIST 800-115 | Sí |
| Reporting / gestión | `defectdojo.export` | DefectDojo | BSD-3-Clause | JSON (API) | ISO 29147/30111 | Sí |
| Validation | `poc_catalog.run_parametrized` | catálogo interno | propia | JSON | PTES §5 | Sí |
| Recon pasivo ampliado | `amass.passive` | Amass | Apache-2.0 | JSON | OSSTMM | Después |
| Supply chain / IaC / imágenes | `trivy.scan` | Trivy | Apache-2.0 | JSON | NIST SSDF (contexto) | Después |
| Infra | `greenbone.scan` | OpenVAS/Greenbone | GPL (varios componentes) | XML | NIST 800-115 | Después |
| Web (segundo motor) | `wapiti.scan` | Wapiti | GPL-2.0 | JSON | OWASP WSTG | Después |
| Recon (puertos masivo) | — | masscan | AGPL-3.0 | — | — | Descartada |
| Web (legacy) | — | Nikto | GPL-2.0 | — | — | Descartada |

\* **Nmap:** su licencia (NPSL) restringe la redistribución/embebido en productos comerciales. Mantenerlo como **proceso externo** que el usuario/operador instala, y revisar la licencia con asesoría legal antes de empaquetarlo.

## Decisiones y motivos
- **Nuclei acotado a una allow-list de templates revisados.** Los templates comunitarios incluyen pruebas intrusivas; sin allow-list contradiría "análisis no destructivo".
- **ZAP en modo baseline (pasivo)** para el MVP; los escaneos activos de ZAP quedan fuera hasta definir el RoE de intensidad.
- **masscan descartada** por el ritmo de emisión que puede degradar servicios y por la licencia AGPL; nmap + naabu (post-MVP) cubren el caso con control de rate.
- **Nikto descartada**: mucho ruido y poco aporte sobre ZAP + Nuclei.
- **Validación sin herramienta de terceros**: usa un **catálogo interno versionado y aprobado** de PoCs, ejecutado en sandbox; el modelo solo parametriza.
- **Orquestación:** LangGraph (estado persistente por fase) + MCP para exponer las capabilities.

## Contrato de adaptador (recordatorio)
`name`, `allowed_phases`, `destructive`, `run(action, target, token) -> dict`; `subprocess` con argv fijo, `shell=False`, timeout y rate limit; salida validada con Pydantic. Ver skill `mcp-tool-adapter`.

## Flujo del MVP con las herramientas
1. `subfinder.enum` → `httpx.probe` → `nmap.service_scan` (loop A, tope 5).
2. `cve.lookup` + `epss.lookup` + `cwe.map` sobre el `AssetGraph` (loop B, parte de correlación).
3. `zap.baseline_scan` + `nuclei.safe_templates` (loop B, análisis).
4. `poc_catalog.run_parametrized` sobre 1 hallazgo, con gate HITL (loop C).
5. `defectdojo.export` + `report.render` → informe con CWE + CVSS v4 + remediación.

## Decisiones cerradas en esta versión
- **Nuclei:** solo `templates/allowlist/` (curada) + exclusión de tags intrusivos + sin OAST (`-ni`). Ver `harness/profiles.yaml`.
- **nmap:** `-sV --top-ports 100 -T3 --max-rate 100`, sin scripts NSE, sin `-A/-O/-sU`; argumentos prohibidos validados por test.
- **Catálogo de validación:** 6 verificaciones **inertes** (cabeceras, cookies, listado de directorio, reflexión con canario, divulgación de errores). Se evalúan sobre la respuesta observada; no ejecutan código en el objetivo.

## Pendientes
- Curar y revisar los primeros templates de `templates/allowlist/`.
- Verificar los flags contra las versiones instaladas de nmap y Nuclei.
- Revisión legal de licencias antes de empaquetar cualquier herramienta.
