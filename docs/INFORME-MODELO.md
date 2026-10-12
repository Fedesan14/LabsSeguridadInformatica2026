# Informe modelo — el molde de lo que se entrega

> **Esto NO es la solución de ningún lab.** Es un informe de ejemplo sobre un
> objetivo FICTICIO (`Nimbus Logística S.A.`), escrito para que veas la
> ESTRUCTURA, el nivel de detalle y el tono que espera la rúbrica. Cuando
> entregues un lab real, tu informe tiene que leerse así: no "capturé la flag",
> sino *qué* encontraste, *cómo* lo probaste, *qué impacto* tiene y *cómo se
> arregla*. La flag es la prueba de que llegaste; el informe es lo que se evalúa.
>
> Las flags acá (`FLAG{ejemplo_ficticio}`) son inventadas. Copiá el ESQUELETO,
> no el contenido.

---

# Informe de Pentesting — Portal Nimbus

| | |
|---|---|
| **Objetivo** | `portal.nimbus.test` (entorno de laboratorio) |
| **Tipo** | Caja negra, aplicación web |
| **Autor** | Grupo 07 — Pérez, Gómez, Díaz, Ruiz |
| **Fecha** | 12/09/2026 |
| **Autorización** | Laboratorio de cátedra. Pruebas SOLO contra el contenedor provisto. Ley 26.388. |

## 1. Resumen ejecutivo

*(Para quien NO es técnico: un jefe, un cliente. Sin jerga. Tres párrafos máximo.)*

Se evaluó la seguridad del portal de Nimbus Logística en un entorno controlado.
Se identificaron **4 vulnerabilidades**, dos de ellas **críticas**: un atacante
sin credenciales puede acceder a la base de datos de clientes y ejecutar comandos
en el servidor.

El riesgo es alto: con las fallas encontradas, un tercero podría robar la base de
datos completa de clientes y tomar control del servidor sin necesidad de usuario
ni contraseña. Se recomienda **detener el pase a producción** hasta remediar los
dos hallazgos críticos.

Ninguna de las fallas requiere herramientas sofisticadas ni conocimiento interno:
son explotables desde internet con utilidades públicas.

## 2. Alcance y metodología

**Alcance.** Únicamente el host `portal.nimbus.test` y sus servicios expuestos.
No se atacó infraestructura de red, ni se realizaron pruebas de denegación de
servicio, ni ingeniería social.

**Metodología.** Se siguió el flujo estándar en capas:

1. **Reconocimiento** — mapeo de servicios y puertos expuestos.
2. **Enumeración** — descubrimiento de rutas, endpoints y tecnología.
3. **Explotación** — validación de vulnerabilidades con prueba de concepto.
4. **Post-explotación** — evaluación del alcance real del compromiso.

## 3. Resumen de hallazgos

| # | Hallazgo | Severidad | CVSS | Estado |
|---|---|---|---|---|
| H-01 | Inyección SQL en el buscador (sin autenticación) | **Crítica** | 9.8 | Confirmada |
| H-02 | Inyección de comandos en la utilidad de diagnóstico | **Crítica** | 9.1 | Confirmada |
| H-03 | Referencia directa insegura a objetos (IDOR) en facturas | Alta | 7.5 | Confirmada |
| H-04 | Fuga de información de versión en cabeceras HTTP | Baja | 3.1 | Confirmada |

## 4. Hallazgos detallados

*(Así se documenta CADA hallazgo. Mostramos H-01 completo como referencia.)*

### H-01 · Inyección SQL en el buscador (sin autenticación)

**Severidad:** Crítica — CVSS 9.8 (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`)

**Descripción.**
El parámetro `q` del endpoint `/buscar` se concatena directamente en una consulta
SQL sin parametrizar. Un atacante puede inyectar SQL arbitrario y leer cualquier
tabla de la base, incluida la de credenciales, sin estar autenticado.

**Reproducción (prueba de concepto).**

```bash
# 1) Se confirma la inyección: una comilla rompe la consulta (error SQL).
curl -s -G http://portal.nimbus.test/buscar --data-urlencode "q=Router'"

# 2) Se enumeran las bases de datos.
sqlmap -u "http://portal.nimbus.test/buscar?q=Router" --batch --dbs

# 3) Se extrae la tabla de secretos.
sqlmap -u "http://portal.nimbus.test/buscar?q=Router" --batch --dump -T secrets
```

**Evidencia.**

```
Database: nimbus
Table: secrets
+----+---------------------------+
| id | valor                     |
+----+---------------------------+
| 1  | FLAG{ejemplo_ficticio_h01}|
+----+---------------------------+
```

**Impacto.**
Exposición total de la confidencialidad de los datos. Un atacante lee la base
completa de clientes y credenciales sin autenticarse. Con las credenciales
obtenidas, el compromiso se extiende a otros sistemas.

**Remediación.**
- Usar **consultas parametrizadas** (prepared statements); nunca concatenar input.
- Aplicar el **principio de menor privilegio** al usuario de base de datos.
- Agregar un WAF como control compensatorio, no como reemplazo del fix.

---

### H-02 · Inyección de comandos en la utilidad de diagnóstico

**Severidad:** Crítica — CVSS 9.1
**Descripción.** El endpoint `/herramientas/ping` pasa el parámetro `host` a un
comando de shell sin sanitizar, permitiendo ejecución de comandos arbitrarios.
**Reproducción.**

```bash
curl -s -G http://portal.nimbus.test/herramientas/ping \
  --data-urlencode "host=127.0.0.1; id"
```

**Evidencia.** La respuesta incluye `uid=33(www-data)`, confirmando ejecución.
**Impacto.** Control del servidor con los privilegios del servicio web.
**Remediación.** Evitar `shell=True`; validar el input contra una lista blanca
(solo IP/hostname válidos); usar APIs que no invoquen la shell.

---

*(H-03 e H-04 se documentan con la misma plantilla: descripción, reproducción,
evidencia, impacto, remediación. Se omiten acá por brevedad — en tu entrega van
completos.)*

## 5. Línea de tiempo

| Hora | Acción |
|---|---|
| 14:02 | Inicio del reconocimiento (`nmap -Pn -sV`) |
| 14:15 | Descubierto el endpoint `/buscar` |
| 14:31 | Confirmada la inyección SQL (H-01) |
| 14:48 | Extraída la tabla `secrets` |
| 15:10 | Confirmada la inyección de comandos (H-02) |

## 6. Conclusiones

El portal no está listo para producción. Las dos fallas críticas comparten una
misma causa raíz: **confianza ciega en el input del usuario.** Parametrizar
consultas y validar/escapar toda entrada elimina H-01, H-02 y H-03 de un plumazo.
No es un problema de herramientas: es un problema de fundamentos.

## 7. Anexos

**Flags capturadas** (prueba de resolución):

| Reto | Flag |
|---|---|
| R1 | `FLAG{ejemplo_ficticio_h01}` |
| R2 | `FLAG{ejemplo_ficticio_h02}` |

**Herramientas utilizadas:** nmap, curl, sqlmap.

---

## Checklist de tu informe (autoevaluación antes de entregar)

- [ ] Resumen ejecutivo entendible por alguien que NO es técnico.
- [ ] Alcance y autorización explícitos (Ley 26.388).
- [ ] Cada hallazgo con: severidad, reproducción, evidencia, impacto, remediación.
- [ ] Los comandos exactos para reproducir (que otro los corra y le dé igual).
- [ ] Causa raíz, no solo síntoma.
- [ ] Remediación concreta y accionable (no "poner un firewall" a secas).
- [ ] Las flags como anexo/prueba, NO como el cuerpo del informe.

> ¿Ves la diferencia? "Capturé FLAG{...}" no es un informe. ESTO es un informe.
> El pentester que sabe explicar el riesgo y cómo arreglarlo vale diez veces más
> que el que solo sabe apretar `sqlmap`. Ponete las pilas con esta parte.
