# Desafíos de extensión

Para equipos que terminan un día antes de tiempo. Todos pasan por OpenSpec (change + tests) y respetan las reglas del proyecto.

## Bloque A — Red team del guard (defensivo, obligatorio el Día 5)
Objetivo: **encontrar cómo se podría evadir el control y blindarlo**. Cada hallazgo se convierte en un test y una corrección.

| # | Idea a probar | Qué debería pasar |
|---|---|---|
| A1 | Hostname con mayúsculas, punto final o espacios | Se normaliza y se decide igual |
| A2 | Sufijo engañoso (`evil-lab.example.test`) | Bloqueado (ya cubierto; extenderlo) |
| A3 | IPv6 y direcciones IPv4 mapeadas a IPv6 | Se evalúan contra los CIDR autorizados |
| A4 | Un hostname autorizado que **resuelve** a una IP fuera de alcance | Se resuelve y se vuelve a validar antes de actuar |
| A5 | Redirecciones HTTP hacia otro host | El adaptador no las sigue fuera de alcance |
| A6 | Token reutilizado en otra fase o engagement | Bloqueado y registrado |
| A7 | Ventana de tiempo con zonas horarias distintas | Comparación en UTC |
| A8 | CIDR demasiado amplio en el RoE (`/8`, `0.0.0.0/0`) | El parser lo rechaza |
| A9 | Argumentos inyectados vía target o vía `parameters` | Rechazados antes de construir comandos |
| A10 | Escritura concurrente en la bitácora | La cadena sigue verificándose |

## Bloque B — Calidad de los agentes
- **B1. Evals comparativas:** mismo caso con dos modelos o dos prompts; tabla con aciertos, costo y latencia.
- **B2. Caso trampa:** diseñar 5 casos donde la respuesta correcta es **no actuar** (alcance ambiguo, dato ausente, PoC inexistente).
- **B3. Consistencia:** correr cada caso 5 veces y medir la variación de la salida.

## Bloque C — Ingeniería
- **C1. LangGraph:** reemplazar el orquestador simple por un grafo con persistencia y reanudación.
- **C2. Aislamiento por engagement:** que dos engagements en paralelo no compartan estado ni tokens.
- **C3. Bitácora firmada:** firmar cada registro (por ejemplo con una clave local) y verificar firma + cadena.
- **C4. Nuevo adaptador:** Trivy sobre una imagen del lab, con perfil acotado y tests de bloqueo.
- **C5. Mapeo ATT&CK:** asociar cada hallazgo a una técnica y mostrarla en el informe.

## Bloque D — Gobernanza
- **D1. Matriz de cumplimiento:** relacionar cada invariante con un control de ISO/IEC 27001 y una práctica de NIST SP 800-115.
- **D2. Plantilla de divulgación** según ISO/IEC 29147 para un hallazgo del lab.
- **D3. Modelo de amenazas del propio PTaaS:** ¿qué pasaría si alguien compromete el orquestador?

## Qué NO es un desafío de extensión
Agregar verificaciones que ejecuten código en el objetivo, extraer datos, o apuntar a algo que no sea el laboratorio propio.
