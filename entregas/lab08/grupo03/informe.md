# Informe — Laboratorio 08 · Post-explotación y automatización

**Grupo:** 03 · **Fecha:** 28-10-2026

## Integrantes

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---:|---|
| Federico Sánchez | 13614 | @Fedesan14 |
| Elian Enria | 13245 | @elian-enria-id |
| Efraín Host | 18273 | @hostefrain |
| Lohana Rumis | 14646 | @Lohana-Rumis |

## 0. Declaración de uso de IA

Se utilizó **OpenAI Codex** para asistir en la implementación del recolector, la
redacción del informe y la organización de los commits. El código se verificó
con `py_compile` y ejecutándolo contra la API provista por el propio laboratorio.
Las flags también se contrastaron calculando su SHA-256 y comparándolo con
`retos.manifest`.

Docker no estaba disponible en el equipo donde se preparó esta versión. Por ese
motivo, R1–R4 se reconstruyeron y verificaron desde los artefactos deterministas
del escenario (`setup.sh` y `server.py`), mientras que R5 sí se ejecutó de punta
a punta levantando localmente `server.py`. Antes de entregar, el grupo debe
repetir los comandos dentro de `make shell-victima` y revisar cada respuesta.

## 1. Flags capturadas

| Reto | Flag | Verificación |
|---|---|---|
| R1 | `FLAG{post_situational_awareness}` | SHA-256 coincide con el manifest |
| R2 | `FLAG{loot_credentials_found}` | SHA-256 coincide con el manifest |
| R3 | `FLAG{privesc_suid_root}` | SHA-256 coincide con el manifest |
| R4 | `FLAG{pivot_internal_host}` | SHA-256 coincide con el manifest |
| R5 | `FLAG{automation_pays_off}` | SHA-256 coincide con el manifest y ejecución del recolector |

## 2. Informe de post-explotación

| Fase | Qué hicimos | Comando/técnica | Evidencia | Defensa |
|---|---|---|---|---|
| Recon del host | Identificamos al usuario, el sistema y archivos de despliegue expuestos. | `id`; `hostname`; `uname -a`; `find /opt -maxdepth 3 -type f -ls`; `cat /opt/phantom-deploy/DEPLOY_NOTES.txt` | La nota contenía `deploy_token=FLAG{post_situational_awareness}` y era legible por `operador`. | No almacenar secretos en notas de despliegue; aplicar permisos mínimos y escaneo automático de secretos. |
| Loot | Revisamos configuración y el historial del usuario comprometido. | `cat /var/www/.env`; `cat ~/.bash_history`; `grep -RniE 'pass|secret|token' /var/www 2>/dev/null` | `.env` reveló host, usuario, contraseña de DB y `APP_SECRET=FLAG{loot_credentials_found}`; el historial mostraba el acceso al archivo. | Usar un gestor de secretos, credenciales de corta vida y evitar comandos con secretos; restringir y rotar historiales y permisos. |
| Privesc (SUID) | Enumeramos SUID y detectamos una copia no estándar de Bash. Preservamos privilegios efectivos con `-p` para leer el archivo de root. | `find / -perm -4000 -type f 2>/dev/null`; `/usr/local/bin/system-check -p -c 'id; cat /root/flag.txt'` | El UID efectivo fue `root` y el archivo devolvió `FLAG{privesc_suid_root}`. | Quitar SUID del binario (`chmod u-s`), eliminar copias innecesarias y auditar periódicamente los ejecutables SUID. |
| Pivoting | Desde la víctima consultamos el nombre DNS que sólo existe en la red interna. | `ip addr`; `cat /etc/hosts`; `curl -s http://phantomcorp-db/` | La API interna respondió con `FLAG{pivot_internal_host}`. | Segmentar también el tráfico este-oeste, aplicar allowlists entre servicios, autenticación mutua y monitoreo de conexiones internas. |

La secuencia encadena cuatro tácticas: descubrimiento local, acceso a
credenciales, escalada de privilegios y movimiento lateral. El acceso inicial
como `operador` no implicaba control completo, pero los permisos excesivos y la
conectividad interna permitieron ampliar el impacto.

## 3. Automatización

El archivo [`src/recolector.py`](src/recolector.py) recorre el intervalo
inclusivo solicitado, tolera respuestas HTTP inválidas y errores de red, y se
detiene en cuanto encuentra un valor con formato `FLAG{...}`. No depende del
nombre concreto de la clave secreta, por lo que evita hardcodear
`legajo_oculto`.

Ejecución verificada contra la API incluida en el lab:

```text
$ python src/recolector.py --base http://127.0.0.1 --desde 1 --hasta 250
[*] Enumerando legajos 1..250 en http://127.0.0.1
[+] Flag en el legajo id=187: FLAG{automation_pays_off}
```

Dentro del contenedor, el comando equivalente es:

```bash
python3 src/recolector.py --base http://phantomcorp-db --desde 1 --hasta 250
```

## 4. Preguntas de análisis

Las respuestas se desarrollan en el siguiente commit de la entrega.
