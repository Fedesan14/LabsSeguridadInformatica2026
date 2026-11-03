# Mini-research — Laboratorio 10

**Grupo:** 03

**Tema elegido:** **A.** IDS/IPS por firmas vs por anomalía (Snort/Suricata): fortalezas y límites.

- [x] **A.** IDS/IPS por firmas vs por anomalía (Snort/Suricata): fortalezas y límites.
- [ ] **B.** Técnicas de evasión de WAF (ofuscación, encoding, case, comentarios).
- [ ] **C.** SIEM y correlación de logs: cómo se detecta lo que ninguna firma ve.
- [ ] **D.** MITRE ATT&CK: la táctica Defense Evasion y sus técnicas.

---

## Desarrollo

### Las familias de detección, según NIST

NIST SP 800-94, *Guide to Intrusion Detection and Prevention Systems (IDPS)*
(Scarfone & Mell, 2007), es la guía de referencia del gobierno de EE. UU. para
estos sistemas y agrupa sus métodos de detección en tres familias:

1. **Detección por firmas (signature-based).** Compara el tráfico contra un
   catálogo de patrones conocidos (un string, una regex, una secuencia de
   bytes) asociados a un ataque específico. Es rápida y computacionalmente
   barata, y prácticamente no genera falsos positivos sobre lo que conoce;
   pero es ciega a cualquier variante que no calce el patrón exacto, y
   necesita mantenimiento constante del *ruleset* (una firma nueva por cada
   variante nueva).
2. **Detección por anomalía (anomaly-based).** Construye un perfil
   estadístico de lo que es "normal" (volumen de tráfico, protocolos usados,
   horarios, orígenes) y alerta ante desvíos de ese perfil. Puede detectar
   ataques nunca vistos (incluso *zero-day*) porque no depende de conocerlos
   de antemano; a cambio, es más costosa de calibrar y, si el perfil de base
   no está bien ajustado, genera más falsos positivos.
3. **Análisis de protocolo con estado (stateful protocol analysis).**
   Compara el tráfico contra un modelo de cómo "debería" comportarse el
   protocolo (siguiendo su RFC), detectando desviaciones del estándar (por
   ejemplo, un comando FTP fuera de secuencia) independientemente de si
   matchea algún patrón puntual.

El Lab 10 implementó, a propósito, **solo la primera**: una lista de
`(nombre, función)` que hace `re.search()`/`in` sobre distintas partes del
request. Eso explica exactamente por qué R4 funcionó: un motor que mira *solo*
firmas puntuales se cae ante cualquier variante sintáctica que el autor de la
regla no haya previsto, aunque la intención maliciosa sea idéntica.

### Cómo lo resuelven herramientas reales: Snort y Suricata

**Snort** es el motor de referencia histórico de detección por firmas: cada
regla tiene un *header* (protocolo, IPs, puertos, dirección) y opciones (qué
patrón buscar y en qué parte del tráfico). El propio índice de reglas que
publica Snort ([snort.org/documents](https://www.snort.org/documents)) muestra
firmas con la misma lógica que nuestra `sqli-union`, pero de producción: una de
las reglas más recientes al momento de revisar el índice "busca
metacaracteres de inyección SQL en parámetros específicos de requests HTTP
dirigidos a un endpoint de API concreto" — exactamente el mismo principio
(patrón conocido → alerta), a escala de miles de reglas mantenidas por un
equipo dedicado.

**Suricata** muestra cómo un motor moderno mitiga justo el problema que
explotamos en R4. Según su propia documentación de reglas
([docs.suricata.io/en/latest/rules/intro.html](https://docs.suricata.io/en/latest/rules/intro.html)),
el motor no aplica las reglas sobre el byte crudo del paquete: reconstruye el
protocolo de aplicación (HTTP, TLS, DNS, SMB, SSH, FTP, entre otros) y expone
**buffers normalizados** (`http.uri`, `http_header`, `file_data`, etc.). La
documentación describe esa normalización como un proceso que "erase anomalous
content, combine packets etcetera": antes de matchear, Suricata decodifica
`%XX`, reensambla streams TCP fragmentados y limpia el tráfico. Eso es,
literalmente, el fix que proponemos para `sqli-union` en la pregunta P2 del
informe (decodificar el query antes de aplicar la regex), implementado a
nivel de motor en lugar de tener que repetirlo a mano en cada regla. Suricata
además conserva el buffer sin normalizar aparte (`http_raw_uri`) para quien
necesite inspeccionar también el valor crudo, y soporta detección de
**anomalías de protocolo** a nivel de decodificador (`decode-event`, por
ejemplo paquetes IP mal formados) — un mecanismo de la familia 3 (protocolo
con estado), totalmente distinto de la detección por firmas de la familia 1.

### Por qué ninguna de las dos reemplaza a la otra

Firmas: rápidas y precisas contra lo conocido, ciegas a lo nuevo. Anomalía:
puede ver lo nunca-visto, pero es más ruidosa y cara de calibrar. Por eso los
productos reales (Suricata, los SIEM, y el propio NIST SP 800-94 en sus
recomendaciones) combinan las tres familias: firmas para bloquear rápido lo
conocido (la mayor parte del ruido de internet), una capa de anomalía/
protocolo para lo que ninguna firma anticipó, y análisis humano de logs para
lo que ninguna de las dos automatizó — que es exactamente lo que R5 del lab
nos obligó a hacer a mano. Es el mismo argumento de P1 y P4 del informe,
visto ahora con herramientas de producción en vez de con nuestro servidor de
juguete.

---

## Fuentes (mín. 3)

1. Scarfone, K., & Mell, P. (2007). *NIST SP 800-94 — Guide to Intrusion
   Detection and Prevention Systems (IDPS).* NIST.
   [https://csrc.nist.gov/pubs/sp/800/94/final](https://csrc.nist.gov/pubs/sp/800/94/final)
   — taxonomía de métodos de detección (firmas, anomalía, protocolo con
   estado) y las cuatro clases de IDPS.
2. Cisco / Snort. *Snort Rule Documentation Index.*
   [https://www.snort.org/documents](https://www.snort.org/documents) —
   ejemplos reales de firmas de producción, incluida detección de
   metacaracteres de SQLi por endpoint específico.
3. Open Information Security Foundation (OISF). *Suricata — Rule/Signature
   introduction.*
   [https://docs.suricata.io/en/latest/rules/intro.html](https://docs.suricata.io/en/latest/rules/intro.html)
   — buffers normalizados por protocolo, *content modifiers*/*sticky
   buffers*, buffer crudo (`http_raw_uri`) y `decode-event`.
4. Open Information Security Foundation (OISF). *What is Suricata.*
   [https://docs.suricata.io/en/latest/what-is-suricata.html](https://docs.suricata.io/en/latest/what-is-suricata.html)

---

## Reflexión

Lo que más conecta con lo que hicimos en R4 del lab es ver que el problema no
era "faltaba pensar en `/**/`": es estructural. Cualquier firma que compare
bytes crudos contra un patrón fijo va a quedar atrás de la próxima forma de
escribir lo mismo. Lo que hace Suricata (normalizar el protocolo antes de
matchear) no es "una regla más larga": es resolver de una sola vez toda una
clase de evasiones por encoding, al precio de tener que mantener un parser de
protocolo real en vez de un regex suelto. Y aun así, Suricata sigue
necesitando firmas, anomalía/protocolo, y en la práctica un analista: ninguna
capa sola alcanza. Eso cambió cómo pensamos la pregunta "¿se puede hacer una
firma perfecta?" del informe: no es que a nuestra regla ingenua le falte una
condición más, es que ese enfoque tiene un techo, y las herramientas reales lo
superan cambiando de estrategia (normalizar antes de comparar), no agregando
más parches al mismo regex.
