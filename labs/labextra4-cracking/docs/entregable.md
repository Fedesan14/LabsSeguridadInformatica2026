# Entregable — Lab Extra 4: Cracking de contraseñas

> Copiá este archivo a `entregas/labextra4/grupoXX/informe.md` y completalo.

**Grupo:** XX · **Integrantes:** (apellido, nombre — usuario de GitHub)

**Declaración de uso de IA:** (obligatoria)

---

## 1. Tabla de resultados

| Usuario | Algoritmo | ¿Cayó? | Técnica (diccionario / regla: cuál) | Contraseña | Tiempo aprox. |
|---|---|---|---|---|---|
| operador | md5 | | | | |
| analista | sha256 | | | | |
| admin | sha256 | | | | |
| root | pbkdf2 | | — | — | — |

## 2. Medición de velocidad (P1)

Medí intentos/segundo por algoritmo con tu cracker (20–100 intentos alcanzan
para estimar). Mostrá cómo mediste.

| Algoritmo | Intentos/segundo (tu máquina) | Diccionario completo tardaría… |
|---|---|---|
| md5 | | |
| sha256 | | |
| pbkdf2-200k | | |

## 3. El loot

Para cada cuenta crackeada: qué contenía su `.enc` (pegá la salida del
descifrado) y qué impacto tendría en la empresa ficticia.

## 4. Las flags

Captura de `./ctf status extra4` con los 3 ✓.

## 5. Preguntas P1–P5

(Desarrollá las 5 del README. P2 y P4 son las que más pesan: salt y trabajo
por intento.)

## 6. Conclusión

Como defensor: redactá en 5 líneas la política de almacenamiento de
contraseñas que le propondrías a PhantomCorp (algoritmo, parámetros, y qué
hacer con las cuentas existentes).
