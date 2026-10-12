# Glosario — la jerga en criollo

> Seguridad tiene MUCHA jerga, y sentirse perdido no es no entender: es no tener
> las palabras. Acá están, explicadas simple, con el lab donde aparecen. Volvé
> cuando una sigla te frene.

## Fundamentos

| Término | Qué es (en criollo) | Lab |
|---|---|---|
| **Tríada CIA** | Las 3 propiedades a proteger: Confidencialidad, Integridad, Disponibilidad. | 01 |
| **Amenaza / Vulnerabilidad / Activo / Impacto** | Lo que puede pasar / la debilidad que lo permite / lo que protegés / la consecuencia. | 01 |
| **Hash** | Huella digital de un archivo: cambia un bit y la huella cambia toda. | 01 |
| **Efecto avalancha** | Un cambio mínimo en la entrada revienta toda la salida del hash. | 01 |
| **Cifrar / Hashear / MAC** | Ocultar (reversible con clave) / huella (no reversible) / huella con clave (autenticidad). | 02 |
| **Kerckhoffs** | Un sistema debe ser seguro aunque conozcan todo, menos la clave. | 02 |
| **Salt** | Un valor aleatorio por usuario que se suma a la contraseña antes de hashear. | 02, 03 |
| **Nonce** | "Number used once": un valor que no se debe repetir. Reutilizarlo rompe la cripto. | 02 |
| **HMAC** | La forma correcta de hacer un MAC (huella con clave), resistente a trampas. | 01, 02 |
| **PBKDF2 / bcrypt / scrypt / Argon2** | Funciones de hash LENTAS a propósito, para guardar contraseñas. | 03 |
| **TOTP / HOTP / 2FA** | El código de 6 dígitos que cambia (segundo factor de autenticación). | 03 |
| **Tiempo constante** | Comparar secretos sin que el TIEMPO delate cuántos caracteres acertaste. | 02, 03 |
| **ALE / SLE / ARO** | Pérdida anual esperada = pérdida por evento × frecuencia anual. | 04 |
| **ISO 27001 / NIST CSF** | Marcos para gestionar la seguridad de una organización. | 04 |

## Ofensiva

| Término | Qué es (en criollo) | Lab |
|---|---|---|
| **Recon(ocimiento)** | Mirar el objetivo antes de tocarlo: qué hay expuesto. | 05 |
| **Enumeración** | Sacarle a cada servicio todo lo que esconde (rutas, archivos, usuarios). | 06 |
| **Banner grabbing** | Leer el "saludo" de un servicio para saber qué es y qué versión. | 05 |
| **Fingerprinting** | Identificar producto y versión exactos de un servicio. | 05, 06 |
| **CVE** | El identificador único de una vulnerabilidad conocida (ej. CVE-2015-3306). | 05 |
| **CVSS** | El puntaje de gravedad de un CVE (0 a 10). | 05 |
| **Payload** | El "dato malicioso" que mandás para explotar (ej. `admin' --`). | 07 |
| **SQLi** | SQL injection: tu input se ejecuta como parte de la consulta SQL. | 07 |
| **IDOR** | Ver datos ajenos cambiando un id (`/perfil?id=1` → `id=2`). | 07 |
| **Path traversal / LFI** | Salir del directorio permitido con `../` para leer archivos. | 07 |
| **Command injection / RCE** | Ejecutar comandos en el servidor (RCE = Remote Code Execution). | 07 |
| **Shell** | Una consola de comandos en la máquina víctima. | 07, 08 |
| **Reverse shell** | Un shell que la víctima abre HACIA el atacante. | 08, 11 |
| **Escalada de privilegios** | Pasar de usuario común a root (control total). | 08 |
| **SUID** | Un permiso que hace correr un binario con los privilegios de su dueño (root). | 08 |
| **Pivoting / Movimiento lateral** | Usar un host comprometido de trampolín hacia otra red. | 08 |
| **Loot** | Lo que "te llevás": credenciales, tokens, datos. | 08 |
| **C2 (Command & Control)** | El servidor externo del atacante que controla el equipo comprometido. | 08, 11 |
| **Exfiltración** | Sacar los datos robados hacia afuera. | 08, 11 |
| **Webshell** | Un archivo (ej. `.php`) subido al server que deja ejecutar comandos por web. | 11 |
| **Persistencia** | Mecanismos para mantener el acceso (cron, usuario backdoor). | 11 |

## Agentes y defensa

| Término | Qué es (en criollo) | Lab |
|---|---|---|
| **Tool-use / Function calling** | Que un LLM pueda "usar herramientas" en un loop. | 09 |
| **Guardrail** | Los límites que le ponés al agente por código (no salir del alcance). | 09 |
| **Prompt injection** | Meterle instrucciones al LLM a través de un dato, para desviarlo. | 09 |
| **IDS / IPS / WAF** | Sistemas que detectan (y a veces bloquean) ataques. | 10 |
| **Firma (signature)** | Un patrón conocido de ataque que el IDS reconoce. | 10 |
| **Evasión** | Disfrazar un ataque para que ninguna firma lo detecte. | 10 |
| **SOC / SIEM** | El equipo/plataforma que vigila y correlaciona los eventos de seguridad. | 10, 11 |
| **Blue team / Red team** | Los que defienden / los que atacan. | 10 |

## Forensia (DFIR)

| Término | Qué es (en criollo) | Lab |
|---|---|---|
| **DFIR** | Digital Forensics & Incident Response: investigar un incidente. | 11 |
| **Cadena de custodia** | Registrar y hashear la evidencia para probar que no se alteró. | 11 |
| **Orden de volatilidad** | Capturar primero lo que se pierde antes (RAM, después disco, después logs). | 11 |
| **Locard** | "Todo contacto deja un rastro": el atacante siempre deja algo. | 11 |
| **IOC (Indicador de Compromiso)** | Una pista concreta del ataque: una IP, un archivo, un hash, un dominio. | 11 |
| **Timeline** | La línea de tiempo del ataque, minuto a minuto. | 11 |
| **Volatility** | La herramienta estándar para analizar volcados de memoria RAM. | 11 |

---

## Siglas rápidas

`CIA` Confidencialidad-Integridad-Disponibilidad · `CVE` Common Vulnerabilities and
Exposures · `CVSS` Common Vulnerability Scoring System · `RCE` Remote Code
Execution · `SQLi` SQL Injection · `IDOR` Insecure Direct Object Reference · `LFI`
Local File Inclusion · `C2` Command & Control · `IDS/IPS` Intrusion
Detection/Prevention System · `WAF` Web Application Firewall · `SOC` Security
Operations Center · `SIEM` Security Information and Event Management · `DFIR`
Digital Forensics & Incident Response · `IOC` Indicator of Compromise · `2FA`
Two-Factor Authentication · `TOTP/HOTP` Time/HMAC-based One-Time Password · `ALE`
Annualized Loss Expectancy.

> ¿Falta un término que te trabó? Abrí un Issue y lo sumamos.
