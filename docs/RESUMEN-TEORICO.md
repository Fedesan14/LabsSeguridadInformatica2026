# Resumen teórico — con referencias para profundizar

> Una **introducción teórica breve** a cada tema del curso, y para cada uno,
> **documentación pública, libre y gratuita** que lo explica mejor o va más a
> fondo. La idea no es que memorices esto: es que tengas el mapa y sepas a dónde
> ir cuando quieras profundizar. Todos los enlaces son de acceso abierto.

> Cada tema se corresponde con su laboratorio (`labs/labNN-*`). El "cómo se hace"
> está en la guía del lab; acá está el "qué es y dónde leer más".

---

# BLOQUE 1 · Fundamentos

## 01 · La tríada CIA e integridad

La seguridad de la información protege tres propiedades: **Confidencialidad** (solo
accede quien debe), **Integridad** (los datos no se alteran sin detección) y
**Disponibilidad** (el servicio está cuando se necesita). Alrededor giran cuatro
conceptos que hay que distinguir con precisión: **amenaza** (lo que puede pasar),
**vulnerabilidad** (la debilidad que lo permite), **activo** (lo que protegés) e
**impacto** (la consecuencia). Las **funciones de hash criptográficas** (SHA-256)
dan integridad verificable: cualquier cambio, aunque sea de un bit, produce un
digest completamente distinto (efecto avalancha).

**Para profundizar (libre):**
- NIST — Glosario y publicaciones de ciberseguridad (CSRC): <https://csrc.nist.gov/glossary>
- OWASP — Fundamentos y proyectos: <https://owasp.org>
- Ross Anderson, *Security Engineering* (libro completo, gratis): <https://www.cl.cam.ac.uk/~rja14/book.html>

## 02 · Criptografía

La criptografía provee confidencialidad (cifrado), integridad (hash) y
autenticidad (MAC/firmas). El **principio de Kerckhoffs** dice que un sistema debe
ser seguro aunque el atacante conozca todo menos la clave. La mayoría de las
fallas reales no están en los algoritmos (AES, SHA-2 son sólidos) sino en su
**uso**: modos de operación inseguros (ECB), reutilización de nonces, MACs mal
construidos (vulnerables a *length-extension*), comparaciones no constantes en el
tiempo. Cifrar ≠ hashear ≠ autenticar: son primitivas distintas.

**Para profundizar (libre):**
- *Crypto 101* (libro introductorio gratuito): <https://www.crypto101.io/>
- Boneh & Shoup, *A Graduate Course in Applied Cryptography* (gratis): <https://toc.cryptobook.us/>
- OWASP — Cryptographic Storage Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html>

## 03 · Autenticación y control de acceso

**Autenticación** responde "¿sos quien decís ser?"; **autorización**, "¿qué podés
hacer?". Las contraseñas nunca se guardan en claro ni con un hash rápido: se usan
funciones lentas con **salt** por usuario e **iteraciones** (PBKDF2, bcrypt,
scrypt, Argon2). El **segundo factor** (TOTP/HOTP) agrega "algo que tenés" al
"algo que sabés", mitigando el robo de credenciales. Las comparaciones de
secretos deben ser en **tiempo constante**.

**Para profundizar (libre):**
- OWASP — Authentication Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>
- RFC 6238 (TOTP) y RFC 4226 (HOTP): <https://www.rfc-editor.org/rfc/rfc6238> · <https://www.rfc-editor.org/rfc/rfc4226>
- OWASP — Password Storage Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html>

## 04 · Marcos normativos y gestión del riesgo

La seguridad es una función de **gestión de riesgo**, no una lista de herramientas.
El riesgo se cuantifica: **ALE** (pérdida anual esperada) = **SLE** (pérdida por
evento) × **ARO** (frecuencia anual). Frente a un riesgo hay cuatro respuestas:
**mitigar, transferir, aceptar, evitar**. Los marcos dan estructura: **ISO/IEC
27001** (sistema de gestión), **NIST CSF** (Identify, Protect, Detect, Respond,
Recover), **CIS Controls** (controles priorizados).

**Para profundizar (libre):**
- NIST Cybersecurity Framework: <https://www.nist.gov/cyberframework>
- CIS Critical Security Controls: <https://www.cisecurity.org/controls>
- ENISA — Risk Management: <https://www.enisa.europa.eu/topics/risk-management>

---
# BLOQUE 2 · Ofensiva

## 05 · Reconocimiento

Primera fase de todo ataque (y de toda defensa): descubrir la superficie
expuesta. Se distingue **recon pasivo** (sin tocar el objetivo: OSINT, DNS,
certificados) de **activo** (interactuar: escaneo de puertos, banner grabbing). El
valor no está en "hay un puerto abierto" sino en **identificar** producto y
versión y **clasificar** su criticidad contra CVE/CVSS. En la Cyber Kill Chain es
*Reconnaissance*; en MITRE ATT&CK, la táctica `TA0043`.

**Para profundizar (libre):**
- MITRE ATT&CK — Reconnaissance (TA0043): <https://attack.mitre.org/tactics/TA0043/>
- Nmap — Reference Guide y el libro (gratis online): <https://nmap.org/book/>
- HackTricks — Pentesting metodología: <https://book.hacktricks.xyz/>

## 06 · Enumeración de servicios

Profundizar dentro de cada servicio ya descubierto: rutas y archivos no listados,
repositorios `.git` expuestos, métodos HTTP peligrosos, endpoints de API,
versiones exactas del stack (fingerprinting). En ATT&CK es la táctica *Discovery*
(`TA0007`). La diferencia con el recon: recon es amplio (qué hay), enumeración es
profundo (qué esconde cada cosa).

**Para profundizar (libre):**
- PortSwigger — Web Security Academy (gratis, con labs): <https://portswigger.net/web-security>
- OWASP — Web Security Testing Guide: <https://owasp.org/www-project-web-security-testing-guide/>
- MITRE ATT&CK — Discovery (TA0007): <https://attack.mitre.org/tactics/TA0007/>

## 07 · Explotación

Convertir una vulnerabilidad en acceso. La familia más común es la **inyección**:
el software mezcla datos (input) y código (una consulta SQL, un comando de shell,
una ruta de archivo) y, al romperse esa frontera, el dato se ejecuta como código —
SQLi, command injection, path traversal. Sumado al **control de acceso roto**
(IDOR). En OWASP Top 10: A03 (Injection) y A01 (Broken Access Control), las dos
categorías más explotadas.

**Para profundizar (libre):**
- OWASP Top 10: <https://owasp.org/www-project-top-ten/>
- PortSwigger — SQL injection, command injection, path traversal, access control: <https://portswigger.net/web-security/all-topics>
- GTFOBins (abuso de binarios Unix): <https://gtfobins.github.io/>

## 08 · Post-explotación y automatización

Lo que ocurre **después** del primer acceso: reconocimiento interno, **escalada de
privilegios** (de usuario común a root, p. ej. por binarios SUID), **loot** de
credenciales, **movimiento lateral / pivoting** (usar un host comprometido para
alcanzar redes segmentadas), y persistencia. En ATT&CK: *Privilege Escalation*
(`TA0004`), *Lateral Movement* (`TA0008`), *Persistence* (`TA0003`). Lo repetitivo
se automatiza — el puente hacia los agentes.

**Para profundizar (libre):**
- MITRE ATT&CK — Privilege Escalation (TA0004) y Lateral Movement (TA0008): <https://attack.mitre.org/tactics/TA0004/> · <https://attack.mitre.org/tactics/TA0008/>
- HackTricks — Linux Privilege Escalation: <https://book.hacktricks.xyz/linux-hardening/privilege-escalation>
- PEASS-ng (linpeas/winpeas): <https://github.com/peass-ng/PEASS-ng>

---
# BLOQUE 3 · Agentes, defensa y forensia

## 09 · Agentes de pentest (IA)

Un agente de IA para tareas ofensivas es, técnicamente, un **loop de tool-use**: un
LLM decide qué herramienta usar, el sistema la ejecuta (con **guardrails**), le
devuelve el resultado, y el ciclo se repite hasta cumplir el objetivo. El LLM
aporta el razonamiento; el código, las herramientas y los límites. Los riesgos
propios (salir del alcance, alucinar hallazgos, *prompt injection* desde el
objetivo) exigen controles específicos. El humano define los límites; el agente
opera adentro.

**Para profundizar (libre):**
- OWASP Top 10 for LLM Applications: <https://genai.owasp.org/llm-top-10/>
- MITRE ATLAS (amenazas a sistemas de IA): <https://atlas.mitre.org/>
- OWASP — LLM Prompt Injection Prevention Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html>

## 10 · Detección y evasión (Blue vs Red)

La defensa detecta ataques por **firmas** (patrones conocidos: una User-Agent, un
`../`, un `UNION SELECT`) y por **anomalía**, y correlaciona **logs** en un SIEM.
La detección por firmas es poderosa pero frágil: reconoce solo lo que ya conoce, y
por eso es **evadible** (ofuscación, encoding, *low-and-slow*). Del lado rojo es la
táctica *Defense Evasion* (`TA0005`); del lado azul, la disciplina de detección
(reglas Sigma) y las contramedidas de MITRE D3FEND.

**Para profundizar (libre):**
- MITRE ATT&CK — Defense Evasion (TA0005): <https://attack.mitre.org/tactics/TA0005/>
- MITRE D3FEND (contramedidas defensivas): <https://d3fend.mitre.org/>
- Sigma — reglas de detección genéricas: <https://github.com/SigmaHQ/sigma>

## 11 · Forensia del pentest (DFIR)

*Digital Forensics & Incident Response*: reconstruir un incidente a partir de la
evidencia. Dos principios rigen: el de **Locard** ("todo contacto deja un rastro")
y el **orden de volatilidad** (se captura primero lo que se pierde antes: memoria
RAM, luego disco, luego logs). Por encima de todo, la **cadena de custodia**: cada
pieza de evidencia se hashea al capturarla; si el hash cambia, fue alterada, y una
evidencia alterada no vale. El objetivo: línea de tiempo, alcance del daño e
**IOCs** (indicadores de compromiso).

**Para profundizar (libre):**
- RFC 3227 — Guidelines for Evidence Collection and Archiving: <https://www.rfc-editor.org/rfc/rfc3227>
- NIST SP 800-86 — Guide to Integrating Forensic Techniques: <https://csrc.nist.gov/pubs/sp/800/86/final>
- Volatility 3 — documentación: <https://volatility3.readthedocs.io/>
- SANS — DFIR posters y recursos: <https://www.sans.org/posters/?focus-area=digital-forensics>

---

## Marco legal (Argentina)

Todas las técnicas del curso se practican **exclusivamente** contra los entornos
provistos por la cátedra. Aplicadas a sistemas de terceros sin autorización escrita
constituyen **delito**: la **Ley 26.388** incorporó al Código Penal argentino las
figuras de acceso indebido, daño informático y otras.

- Ley 26.388 (texto oficial, InfoLEG): <https://www.argentina.gob.ar/normativa/nacional/ley-26388-141790>

> La diferencia entre un pentester y un delincuente es una sola: **la
> autorización, el alcance y la ética.**
