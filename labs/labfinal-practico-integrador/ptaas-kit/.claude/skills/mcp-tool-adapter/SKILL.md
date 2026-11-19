---
name: mcp-tool-adapter
description: Usar al incorporar una herramienta open source (nmap, httpx, ZAP, Nuclei, Trivy, DefectDojo, etc.) a PTaaS como adaptador MCP/ToolAdapter tipado.
---

# Adaptadores de herramientas

## Criterios de selección
Licencia permisiva, salida JSON/XML parseable, proyecto activo, CLI o API estable.

## Catálogo por fase (candidatas)
| Fase | Herramientas |
|---|---|
| Recon pasivo | subfinder, amass, theHarvester |
| Recon activo | httpx, naabu, nmap |
| Correlación | feeds NVD/CVE, EPSS, templates Nuclei (solo datos) |
| Análisis | OWASP ZAP (baseline), Nuclei (templates seguros), Trivy, OpenVAS/Greenbone |
| Hallazgos | DefectDojo |

## Plantilla de adaptador
```python
class HttpxProbe:
    name = "httpx.probe"
    allowed_phases = (Phase.RECON,)
    destructive = False

    def run(self, action, target, token) -> dict:
        # 1) construir argv fijo (sin shell=True, sin interpolar input sin validar)
        # 2) ejecutar con timeout y rate limit de policy.yaml
        # 3) parsear salida a schema Pydantic; devolver dict
        ...
```

## Reglas
- `subprocess.run([...], shell=False, timeout=...)`; nunca concatenar strings.
- El target llega ya validado por el Guard, pero el adaptador revalida formato.
- Un adaptador por capability; nombre `herramienta.accion` y registrado en `policy.yaml`.
- Test con salida grabada (fixtures) + un Scenario de bloqueo fuera de alcance.
