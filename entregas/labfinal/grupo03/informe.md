# Informe de Penetration Test — PhantomCorp "Clientes"

**Cliente:** PhantomCorp S.A.  ·  **Grupo auditor:** 03
**Integrantes:** [PENDIENTE: nombre — usuario GitHub de cada integrante]
**Fecha:** 2026-11-03 (reconocimiento automatizado) [PENDIENTE: fechas de la auditoría completa]  ·  **Modalidad:** Caja negra  ·  **Alcance:** host `phantomcorp` (lab)

> **Borrador.** Todo lo marcado como [PENDIENTE] se completará antes de abrir el PR. Lo que no está marcado cuenta con evidencia.

---

## 0. Declaración de uso de IA

**Herramienta:** Claude (asistente de IA de Anthropic), utilizado a través de Claude Code.

**Revisión posterior:** ChatGPT Codex, utilizado el 2026-11-19 para ejecutar la validación local disponible y revisar la consistencia del entregable. En esta revisión no se levantó Docker, no se envió tráfico al objetivo y no se generaron hallazgos ni flags.

**Usos:**
- Diseño de la arquitectura del swarm: agentes, orquestador, bitácora, sandbox y lista de permisos (RoE).
- Modificación del agente Enum para que consulte `robots.txt` y pruebe las rutas que allí figuran, con su test.
- Programación de `entregas/labfinal/grupo03/ptaas/`: `roe.py`, `bitacora.py`, `sandbox.py`, `agentes.py`, `orquestador.py`, `panel.py`, `panel.html` y `test_ptaas.py`.
- Elaboración de la guía de pruebas `PRUEBAS.md` y de este informe.

**Partes alcanzadas:** el código del swarm y del panel, y la guía de pruebas. Las decisiones sobre el alcance, la elección del objetivo y la interpretación de resultados son del grupo [PENDIENTE: confirmar que todos los integrantes están de acuerdo].

**Verificación del resultado entregado por la IA:**
- Pasa `test_ptaas.py` (determinismo, RoE, integridad de la bitácora y controles del panel).
- En la revisión del 2026-11-19 se ejecutó localmente `python test_ptaas.py`: finalizó con `OK`. OpenSSL no estaba disponible en el `PATH`, por lo que esa verificación independiente quedó pendiente de repetir en Git Bash o en una máquina con OpenSSL.
- La cadena de la bitácora se recalculó con `openssl dgst -hmac`, herramienta ajena al código, y el resultado coincide.
- Los comandos de la guía se corrieron en Git Bash exactamente como están escritos, sobre Docker Desktop 28.5.1.
- Los códigos HTTP del reconocimiento se contrastaron manualmente con la bitácora.
- El panel web se probó en el navegador con una ejecución real contra phantomcorp.

**Lo que NO está validado con evidencia:** [PENDIENTE: cada hallazgo se reproduce manualmente antes de incluirlo en la sección 4].

---

## 1. Resumen ejecutivo

- **Trabajo realizado:** reconocimiento automatizado del servidor de Clientes: relevamiento de los servicios expuestos y de las rutas web más habituales. [PENDIENTE: completar con el resto de la cadena]
- **Resultado general:** [PENDIENTE: hasta dónde se avanzó en los hitos R1 a R4]
- **Riesgo para el negocio:** [PENDIENTE: qué datos o servicios quedaron expuestos y qué consecuencias tiene]
- **Recomendación prioritaria:** [PENDIENTE: la primera medida que debería adoptar la empresa]

| Severidad | Cantidad de hallazgos |
|---|---|
| Crítica | [PENDIENTE] |
| Alta | [PENDIENTE] |
| Media | [PENDIENTE] |
| Baja | [PENDIENTE] |

---

## 2. Alcance y metodología

**Alcance:** exclusivamente el host `phantomcorp` del laboratorio.

**Fuera de alcance:** cualquier otro equipo. La prueba de la lista de permisos intentó deliberadamente atacar `8.8.8.8`; la lista lo rechazó antes de ejecutar nada, por lo que no se envió tráfico a esa IP.

**Reglas del engagement:** sin acciones destructivas ni denegación de servicio.

**Marco aplicado:** reconocimiento → enumeración → explotación → post-explotación → impacto.

**Reconocimiento (avance actual):**
- **Escaneo de puertos:** `nmap -sT -sV --version-light -Pn --top-ports 100`. Se optó por `--version-light` porque el `-sV` completo demoró cerca de 90 segundos contra este servicio, superando el tope de 60 segundos por acción definido en el sandbox.
- **Enumeración web:** se descarga `/robots.txt` de cada servicio web, se extraen las rutas que pide no indexar a los buscadores y se consultan junto con 7 rutas comunes. Se anota el código HTTP de cada una.

**Ejecución:** cada acción corre en un contenedor Docker descartable, sin privilegios de administrador, con el sistema de archivos en solo lectura y sin capacidades de red especiales. Al finalizar, el contenedor se elimina.

**Registro:** cada propuesta y cada resultado se asientan en una bitácora donde cada línea lleva un sello criptográfico (HMAC-SHA256) calculado sobre la anterior. Si se altera una línea, la verificación falla en ese punto.

---

## 3. Relato del ataque

El agente de reconocimiento escaneó los 100 puertos más comunes de phantomcorp y halló el **puerto 80 abierto**, con un servicio web que nmap no logró identificar con certeza. Luego, el agente de enumeración leyó `/robots.txt` (HTTP 200), que contiene `Disallow: /portal-rrhh`: una ruta que ninguna página del sitio enlaza, pero que se pide a los buscadores no indexar. El agente la probó junto con 7 rutas comunes. Las 7 devolvieron 404 (no existen) y `/portal-rrhh` devolvió **200**, con el título **Portal interno RRHH** y un formulario de login. Así se cumple el hito R1, y la flag se envió con `./ctf submit final R1`.

Este paso lo realizó el swarm en una ejecución automática (anexo A). Antes de que Enum leyera `robots.txt`, ya habíamos llegado a la misma ruta manualmente (anexo D).

[PENDIENTE: R2 (foothold), R3 (post-explotación) y R4 (impacto), en prosa, de modo que un colega pueda seguir el recorrido completo]

```
recon/enum + robots.txt  ->  R1 portal interno (hecho)  ->  [PENDIENTE] foothold  ->  [PENDIENTE] loot  ->  [PENDIENTE] impacto
```

---

## 4. Hallazgos (detalle técnico)

> Ordenados por severidad, primero los críticos. Este borrador aún no tiene hallazgos confirmados.

**Nota:** el portal `/portal-rrhh`, con el que se completó R1, todavía no fue evaluado como hallazgo. [PENDIENTE: determinar si el login permite ingresar sin credenciales (R2) y con qué severidad y CVSS]

### H-01 · [PENDIENTE: título del hallazgo]
- **Severidad:** [PENDIENTE: Crítica/Alta/Media/Baja] · **CVSS:** [PENDIENTE: vector y puntaje, justificados]
- **Ubicación:** [PENDIENTE: endpoint, parámetro o archivo]
- **Descripción:** [PENDIENTE: en qué consiste la vulnerabilidad]
- **Evidencia (reproducible):**
  ```bash
  # [PENDIENTE: el comando exacto y su salida]
  ```
- **Impacto:** [PENDIENTE: qué obtiene un atacante, en ESTE sistema]
- **Remediación:** [PENDIENTE: corrección de raíz, concreta y correcta]

---

## 5. Conclusión

[PENDIENTE: postura general de seguridad del sistema. ¿Se podía evitar la cadena? ¿Qué eslabón, de haberse corregido, la habría cortado antes?]

---

## 6. Anexo

### A. Resultado del reconocimiento

- **Puertos abiertos:** `80/tcp` (servicio web, sin identificar con certeza)
- **Contenido de `/robots.txt`:** `Disallow: /portal-rrhh`
- **Rutas que no devolvieron 404:** `/portal-rrhh` (HTTP 200)
- **Cabeza de la bitácora:** `6cd15fd14a9534314e9548702165df9cd417b1cde72e705f351d5f999a880d9c` (archivo `bitacora-5.jsonl`, verificado con `bitacora.py`)

### B. Comandos ejecutados

```bash
nmap -sT -sV --version-light -Pn --top-ports 100 phantomcorp
```

```bash
curl -s -m 10 --max-filesize 65536 http://phantomcorp:80/robots.txt
```

```bash
curl -s -m 10 -o /dev/null -w '%{http_code}' http://phantomcorp:80/admin
# el mismo comando para /interno, /portal, /intranet, /login, /api, /backup y /portal-rrhh
```

### C. Estado de los hitos

Salida de `./ctf status final` tras enviar la flag de R1:

```
   ✓  R1     Recon/enum: portal interno localizado
   ·  R2     Explotacion: foothold por SQLi
   ·  R3     Post: token de API looteado
   ·  R4     Impacto: crown jewels (datos de clientes)

  ███████░░░░░░░░░░░░░░░░░░░░░░░  1/4 (25%)
```

[PENDIENTE: captura de pantalla de este estado cuando R2 a R4 estén completos]

### D. Pasos manuales del hito R1

Se hicieron en la primera pasada, antes de que Enum leyera `robots.txt`. Ambos pedidos salieron desde el sandbox, con las mismas restricciones del swarm:

```bash
curl -s -m 10 -i http://phantomcorp:80/robots.txt
```

```bash
curl -s -m 10 -i http://phantomcorp:80/portal-rrhh
```

La respuesta de `/portal-rrhh` trae la flag de R1 en un comentario HTML. Se envió con `./ctf submit final R1`.
