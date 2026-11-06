# Informe de Penetration Test — PhantomCorp "Clientes"

**Cliente:** PhantomCorp S.A.  ·  **Auditor (grupo):** 03
**Integrantes:** [PENDIENTE: nombre — usuario GitHub de cada integrante]
**Fecha:** 2026-11-03 (reconocimiento automatizado) [PENDIENTE: fechas de la auditoría completa]  ·  **Tipo:** Caja negra  ·  **Alcance:** host `phantomcorp` (lab)

> **Borrador.** Lo marcado como [PENDIENTE] se completa antes de abrir el PR. Nada de lo que está sin marcar es una afirmación sin evidencia.

---

## 0. Declaración de uso de IA

**Herramienta:** Claude (asistente de IA de Anthropic), usado desde Claude Code.

**Para qué se usó:**
- Diseño de la arquitectura del swarm: agentes, orquestador, bitácora, sandbox y lista de permisos (RoE).
- Cambio al agente Enum para que lea `robots.txt` y pruebe sus rutas, con su caso de prueba.
- Escritura del código de `entregas/labfinal/grupo03/ptaas/`: `roe.py`, `bitacora.py`, `sandbox.py`, `agentes.py`, `orquestador.py`, `panel.py`, `panel.html` y `test_ptaas.py`.
- Redacción de la guía de pruebas `PRUEBAS.md` y de este informe.

**Qué partes afectó:** el código del swarm y del panel, y la guía de pruebas. Las decisiones de alcance, la elección del target y la interpretación de los resultados son nuestras [PENDIENTE: confirmar que todo el grupo está de acuerdo con esto].

**Cómo se verificó lo que devolvió:**
- `test_ptaas.py` (determinismo, RoE, integridad de la bitácora y controles del panel) pasa.
- La cadena de la bitácora se recalculó con `openssl dgst -hmac`, una herramienta independiente del código, y coincide.
- Los comandos de la guía se ejecutaron en Git Bash tal como están escritos, sobre Docker Desktop 28.5.1.
- Los códigos HTTP que devolvió el reconocimiento se revisaron a mano contra la bitácora.
- El panel web se probó en el navegador con una corrida real contra phantomcorp.

**Qué NO se validó con evidencia:** [PENDIENTE: cada hallazgo se reproduce a mano antes de incluirlo en la sección 4].

---

## 1. Resumen ejecutivo

- **Qué se hizo:** un reconocimiento automatizado del servidor de Clientes. Se revisaron los servicios que están expuestos y las rutas web más comunes. [PENDIENTE: completar con el resto de la cadena]
- **Resultado global:** [PENDIENTE: hasta dónde se llegó en los hitos R1 a R4]
- **Riesgo de negocio:** [PENDIENTE: qué datos o servicios quedaron expuestos, y qué implica]
- **Recomendación prioritaria:** [PENDIENTE: la acción número 1 que debería tomar la empresa]

| Severidad | Cantidad de hallazgos |
|---|---|
| Crítica | [PENDIENTE] |
| Alta | [PENDIENTE] |
| Media | [PENDIENTE] |
| Baja | [PENDIENTE] |

---

## 2. Alcance y metodología

**Alcance:** únicamente el host `phantomcorp` del lab.

**Fuera de alcance:** cualquier otro host. La prueba de la lista de permisos intentó atacar `8.8.8.8` a propósito; la lista lo bloqueó antes de ejecutar nada, así que no salió tráfico hacia esa IP.

**Reglas del engagement:** sin acciones destructivas y sin denegación de servicio.

**Marco seguido:** reconocimiento → enumeración → explotación → post-explotación → impacto.

**Reconocimiento (lo que se hizo hasta ahora):**
- **Escaneo de puertos:** `nmap -sT -sV --version-light -Pn --top-ports 100`. Se usó `--version-light` porque el `-sV` completo tardó unos 90 segundos contra este servicio, más que el límite de 60 segundos por acción que fijamos en el sandbox.
- **Enumeración web:** se lee `/robots.txt` de cada servicio web, se extraen las rutas que ese archivo le pide a los buscadores que no indexen, y se piden esas rutas junto con 7 rutas típicas. Se registra el código HTTP de cada una.

**Cómo se ejecutó:** cada acción corre en un contenedor Docker descartable, sin privilegios de administrador, con el sistema de archivos de solo lectura y sin capacidades de red especiales. El contenedor se borra al terminar.

**Cómo se registró:** cada propuesta y cada resultado quedan en una bitácora en la que cada línea lleva un sello criptográfico (HMAC-SHA256) calculado a partir de la línea anterior. Si alguien modifica una línea, la verificación falla en esa línea.

---

## 3. Narrativa del ataque

El agente de reconocimiento escaneó los 100 puertos más comunes de phantomcorp y encontró el **puerto 80 abierto**, con un servicio web que nmap no pudo identificar con certeza. Después, el agente de enumeración leyó `/robots.txt` (HTTP 200). Ese archivo contiene `Disallow: /portal-rrhh`: una ruta que el sitio no enlaza desde ninguna página, pero que le pide a los buscadores no indexar. El agente la probó junto con 7 rutas típicas. Las 7 respondieron 404 (no existen), y `/portal-rrhh` respondió **200**, con el título **Portal interno RRHH** y un formulario de login. Con eso se completa el hito R1, y la flag se envió con `./ctf submit final R1`.

Este paso lo hizo el swarm en una corrida automática (anexo A). Antes de que Enum leyera `robots.txt`, habíamos llegado a la misma ruta a mano (anexo D).

[PENDIENTE: R2 (foothold), R3 (post-explotación) y R4 (impacto), en prosa, para que un colega pueda seguir el camino de principio a fin]

```
recon/enum + robots.txt  ->  R1 portal interno (hecho)  ->  [PENDIENTE] foothold  ->  [PENDIENTE] loot  ->  [PENDIENTE] impacto
```

---

## 4. Hallazgos (detalle técnico)

> Ordenados por severidad, críticos primero. Este borrador todavía no tiene hallazgos confirmados.

**Nota:** el portal `/portal-rrhh`, que completó R1, todavía no se evaluó como hallazgo. [PENDIENTE: evaluar si el formulario de login permite entrar sin credenciales (R2), y con qué severidad y CVSS]

### H-01 · [PENDIENTE: título del hallazgo]
- **Severidad:** [PENDIENTE: Crítica/Alta/Media/Baja] · **CVSS:** [PENDIENTE: vector y score, justificados]
- **Ubicación:** [PENDIENTE: endpoint, parámetro o archivo]
- **Descripción:** [PENDIENTE: qué es la vulnerabilidad]
- **Evidencia (reproducible):**
  ```bash
  # [PENDIENTE: el comando exacto y su salida]
  ```
- **Impacto:** [PENDIENTE: qué logra un atacante con esto, en ESTE sistema]
- **Remediación:** [PENDIENTE: cómo se corrige de raíz, concreto y correcto]

---

## 5. Conclusión

[PENDIENTE: postura de seguridad general del sistema. ¿La cadena era evitable? ¿Cuál fue el eslabón que, arreglado, la habría cortado antes?]

---

## 6. Anexo

### A. Salida del reconocimiento

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

Salida de `./ctf status final` después de enviar la flag de R1:

```
   ✓  R1     Recon/enum: portal interno localizado
   ·  R2     Explotacion: foothold por SQLi
   ·  R3     Post: token de API looteado
   ·  R4     Impacto: crown jewels (datos de clientes)

  ███████░░░░░░░░░░░░░░░░░░░░░░░  1/4 (25%)
```

[PENDIENTE: la captura de pantalla de este estado, cuando estén R2 a R4]

### D. Pasos manuales del hito R1

Esta fue la primera vez, antes de que Enum leyera `robots.txt`. Los dos pedidos se hicieron desde el sandbox, con las mismas restricciones que usa el swarm:

```bash
curl -s -m 10 -i http://phantomcorp:80/robots.txt
```

```bash
curl -s -m 10 -i http://phantomcorp:80/portal-rrhh
```

La respuesta de `/portal-rrhh` incluye la flag de R1 en un comentario HTML. Se envió con `./ctf submit final R1`.
