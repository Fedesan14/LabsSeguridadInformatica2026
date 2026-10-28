# Mini-research — Laboratorio 05

**Grupo:** 03
**Tema elegido:** **A.** El CVE-2015-3306 de ProFTPD 1.3.5 — `mod_copy`, el abuso
de `SITE CPFR/CPTO`, y por qué un banner de versión alcanza para saber que el
servidor es vulnerable.

---

## Desarrollo

### El servicio y su banner

En el recon de PhantomCorp el puerto 21 nos saludó con
`220 ProFTPD 1.3.5 Server`. ProFTPD es un servidor FTP de código abierto muy
usado en Linux. La versión **1.3.5** es la pieza clave: no es "un FTP viejo", es
una versión concreta con una vulnerabilidad pública y catalogada.

### Qué es `mod_copy` y el ataque `SITE CPFR/CPTO`

`mod_copy` es un módulo de ProFTPD que agrega dos comandos `SITE` para copiar
archivos **dentro del servidor** sin tener que descargarlos y volver a subirlos:

- `SITE CPFR <origen>` — *copy from*: marca el archivo de origen.
- `SITE CPTO <destino>` — *copy to*: lo copia al destino.

El fallo (**CVE-2015-3306**) es que, en la 1.3.5 con `mod_copy` habilitado,
**estos comandos no exigen autenticación**: se pueden ejecutar antes de hacer
login. Un atacante remoto puede entonces copiar archivos arbitrarios del
servidor y, sobre todo, **escribir** archivos arbitrarios. El salto a ejecución
de código es directo: se copia contenido controlado por el atacante a una ruta
servida por el servidor web que convive con el FTP (por ejemplo un `.php` en el
*docroot*), y al pedirlo por HTTP, el server lo ejecuta. De lectura/escritura
arbitraria de archivos se pasa a **RCE**.

Eso explica el CVSS. NVD le asigna un **10.0 (crítico)**, tanto en v2 como en
v3.1, con vector `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`: explotable por
**red**, de **baja complejidad**, **sin privilegios** ni interacción del
usuario, con impacto total en confidencialidad, integridad y disponibilidad, y
cambio de alcance (*scope changed*) porque desde el FTP se compromete al sistema
entero.

### Por qué el banner de versión ya es suficiente

Acá está la lección de recon: **no hace falta explotar nada para clasificar el
riesgo**. El banner `ProFTPD 1.3.5` empareja exacto con el único rango afectado
por el CVE-2015-3306 (la 1.3.5; se corrige en 1.3.5a). Con solo leer ese saludo
—recon activo de bajísimo esfuerzo— ya sabemos que, *si* `mod_copy` está
cargado, el host tiene un RCE no autenticado con score 10. Herramientas
offline como `searchsploit proftpd 1.3.5` devuelven el módulo de Metasploit
listo. Por eso el fingerprinting de versión es el corazón del recon: convierte
un "hay un FTP abierto" en "hay un FTP con CVE-2015-3306", que es la diferencia
entre un puerto y un hallazgo.

La salvedad honesta: el banner prueba la **versión**, no que `mod_copy` esté
efectivamente habilitado. Confirmarlo requiere probar los comandos `SITE`, que
ya es la fase de explotación (Lab 07), fuera del alcance de este recon.

## Fuentes

1. NVD — CVE-2015-3306, descripción y CVSS v3.1/v2 (API oficial):
   https://nvd.nist.gov/vuln/detail/CVE-2015-3306
2. CVE Record (MITRE) CVE-2015-3306: https://www.cve.org/CVERecord?id=CVE-2015-3306
3. Exploit-DB #36803 — *ProFTPd 1.3.5 mod_copy Remote Command Execution*:
   https://www.exploit-db.com/exploits/36803
4. ProFTPD — documentación del módulo `mod_copy` (comandos `SITE CPFR/CPTO`):
   http://www.proftpd.org/docs/contrib/mod_copy.html

## Reflexión (3–5 líneas)

Lo que más nos quedó es que recon y clasificación son casi lo mismo cuando se
hace bien: el trabajo intelectual no fue "correr nmap" sino conectar un banner
de nueve caracteres con un CVE de score 10. También que la versión exacta manda:
"ProFTPD" no dice nada, "ProFTPD 1.3.5" dice RCE no autenticado. Y que hay un
límite honesto entre identificar (la versión es vulnerable) y confirmar (el
módulo está activo), y ese límite es justo donde termina el recon y empieza la
explotación.
