# Research — Lab Extra 3: Defendé PhantomCorp

**Grupo:** 03

**Declaración de uso de IA:** Claude Code (Anthropic, modelo Opus 5) para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe.
GitHub Copilot con modelo Claude Sonnet 5 para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito.

**Opción elegida:** A — Guías de hardening reales (OWASP Cheat Sheet Series).

---

## 1. ¿Cuáles de las 5 defensas del lab aparecen en las guías? ¿Con qué nombre?

Las cinco aparecen, cada una bajo un nombre distinto al que usa el lab:

- **D1 (banner de versión).** La [OWASP HTTP Headers Cheat
  Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
  la trata como el header `Server`, que revela "el software usado por el
  servidor de origen que manejó el request", y recomienda literalmente
  *"Remove this header or set non-informative values"* (quitarlo o ponerle un
  valor genérico tipo `webserver`). También cubre el caso hermano
  `X-Powered-By`, al que directamente dice *"Remove all `X-Powered-By`
  headers"*.
- **D2 y D3 (endpoint de debug y ruta de backup sin auth).** Caen bajo **A05:2021
  — Security Misconfiguration** del [OWASP Top
  10](https://top10.owasp.org/2021/A05_2021-Security_Misconfiguration), que
  describe exactamente este patrón: *"Unnecessary features are enabled or
  installed (e.g., unnecessary ports, services, pages, accounts, or
  privileges)"*, y recomienda como prevención *"Remove or do not install
  unused features and frameworks"*. El propio ejemplo de ataque de la guía
  describe el mismo escenario que D3: una app de ejemplo o un endpoint
  administrativo que quedó en producción con acceso sin restricciones.
- **D4 (SQLi).** La [OWASP SQL Injection Prevention Cheat
  Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
  lo llama **Option 1: Prepared Statements (Parameterized Queries)**, la
  defensa primaria recomendada, y advierte explícitamente *"Do not use manual
  escaping as a substitute for parameter binding"* — la guía nombra
  directamente la "trampa típica" que señala la consigna del lab.
- **D5 (path traversal).** La [página de OWASP sobre Path
  Traversal](https://community.owasp.org/attacks/Path_Traversal) recomienda
  *"Validate the user's input by only accepting known good – do not sanitize
  the data"* y normalizar el path antes de usarlo en una llamada de
  filesystem, en vez de intentar filtrar substrings como `".."`.

## 2. ¿Qué control recomienda la guía que el lab no cubre? ¿Cómo lo implementarías?

La HTTP Headers Cheat Sheet cubre, además del `Server`, un conjunto de **security headers** que el lab no toca en ninguna de las 5 defensas: `X-Content-Type-Options: nosniff` (evita que el navegador "adivine" un content-type distinto al declarado, mitigando ciertos XSS), `X-Frame-Options: DENY` (mitiga *clickjacking*) y, para sitios HTTPS, `Strict-Transport-Security`.
Ninguno de los cinco problemas D1–D5 toca esta capa.

Se implementaría en `server.py`, sin frameworks, agregando los headers en el único punto donde ya se arma toda respuesta (`_send()`):

```python
def _send(self, code, body, ctype):
    self.send_response(code)
    self.send_header("Content-Type", ctype)
    self.send_header("X-Content-Type-Options", "nosniff")
    self.send_header("X-Frame-Options", "DENY")
    self.end_headers()
    self.wfile.write(body)
```

Al estar centralizado en un solo helper (como ya hicimos con el fix de D1 en `send_response`), un solo cambio alcanza para todas las rutas.

## 3. ¿Qué es "defense in depth" y cómo se aplica a D3?

*Defense in depth* es el principio de no depender de un único control para frenar un ataque, sino de superponer varias capas independientes, de forma que si una falla (o fue mal implementada), las demás igual contienen el problema. Ninguna capa individual tiene que ser perfecta; lo que importa es que fallen de a una, no todas juntas.

Aplicado a D3 (`/backup`), el fix que hicimos (eliminar la ruta) es la capa estructural y suficiente por sí sola. Pero si por algún motivo de negocio `/backup` tuviera que seguir existiendo, la defensa en profundidad correcta sería apilar varias capas, ninguna de las cuales reemplaza a las otras: **(1)** autenticación/autorización real en el servidor (la capa que de verdad bloquea el acceso); **(2)** no listarla en `robots.txt` (reduce ruido de bots que la respetan, sin pretender que eso "proteja" nada — ver P2 del informe); **(3)** logging/alerting de accesos a esa ruta, para detectar intentos aunque la autenticación falle; **(4)**, si el dato es sensible de verdad, cifrado en reposo del backup mismo, para que ni siquiera un acceso exitoso entregue datos en claro. Sacarla del robots.txt *sola* no es defensa en profundidad: es una sola capa cosmética haciéndose pasar por varias.

---

## Pregunta de cierre (obligatoria)

**El verificador de este lab es un "atacante automático". ¿Qué relación tiene con escáneres como Nessus, OpenVAS o nuclei? ¿Qué puede y qué NO puede demostrar un escaneo automático sobre la seguridad de una app?**

La relación es de principio, no de escala: `verificar-defensa.py` hace exactamente lo que hace un escáner de vulnerabilidades real —manda un request con un patrón de ataque conocido y mira la respuesta (código HTTP, contenido, headers) para decidir si el objetivo es vulnerable a *esa* técnica puntual—, solo que con 5 chequeos escritos a mano en vez de miles de plugins mantenidos por un equipo (Nessus, OpenVAS) o miles de templates YAML versionados por la comunidad (`nuclei`). La arquitectura es la misma: una lista de firmas de ataque conocidas, cada una con su propia forma de verificar "¿funcionó o no?".

**Qué SÍ puede demostrar:** que una vulnerabilidad *conocida y con firma escrita* no reproduce el síntoma exacto que el escáner probó, en el momento exacto del escaneo. Es exactamente lo que hace nuestro verificador: confirma que los 5 payloads puntuales de los labs 05–07 ya no funcionan.

**Qué NO puede demostrar:** que la app está "seguro" en sentido amplio. Un escaneo automático no encuentra fallas de lógica de negocio (ej. que un usuario pueda ver facturas ajenas cambiando un ID, como vimos en el Lab 10 con IDOR), no encuentra variantes del mismo bug que su firma no contempla (el mismo argumento de P4: un escáner que solo prueba `' OR 1=1 --` no prueba `admin'--` ni una docena de otras formas de la misma inyección si no están
en su base de firmas), y da una falsa sensación de seguridad si se lo trata como la palabra final en vez de una capa más. Es el mismo argumento del Lab 10 sobre detección por firmas: potente contra lo que ya conoce, ciego a lo que no, y necesita complementarse con revisión manual/auditoría de código (que es, de hecho, cómo detectamos que el "bloqueo" de D5 contra el original en Windows era un falso positivo del entorno y no una defensa real — ningún escáner automático nos iba a avisar de eso).