# Mini-research — Laboratorio 08

**Grupo:** 03  
**Tema:** SUID, secretos y segmentación después del acceso inicial

## SUID: excepción de privilegio

En Unix, SUID permite que un programa se ejecute con el UID efectivo de su
propietario. Es necesario sólo en casos puntuales: un binario demasiado general
con SUID puede entregar una escalada completa. MITRE ATT&CK identifica el abuso
de Setuid/Setgid como T1548.001. En el lab, Bash con SUID es crítico porque una
shell permite ejecutar operaciones arbitrarias como el propietario del archivo.

La defensa es minimizar los binarios SUID/SGID, verificar que no sean
escribibles por usuarios sin privilegio, auditar sus permisos y quitar el bit si
la función no lo requiere. Ser propiedad de root no vuelve seguro a un binario:
importa qué puede hacer cuando lo invoca otro usuario.

## Secretos como superficie de ataque

Un `.env` legible y el historial del shell son fuentes de credenciales. Una vez
que un proceso comprometido las lee, el atacante puede ampliar acceso sin otra
vulnerabilidad. OWASP recomienda centralizar almacenamiento, provisión,
auditoría y rotación; también usar vida corta, revocación y mínimo privilegio.
Ante una filtración hay que revocar y rotar: ocultar el archivo no invalida una
copia ya obtenida.

## Segmentación y pivoting

La segmentación evita acceso directo desde Internet, pero falla como contención
si un front-end comprometido puede hacer requests arbitrarios a la base. MITRE
ubica el uso de servicios remotos para moverse entre sistemas en movimiento
lateral (T1021). La mejora es controlar tráfico este-oeste por identidad,
servicio y puerto; autenticar al cliente ante la base y registrar flujos
anómalos. Comprometer el front-end no debe equivaler a confiar en su red.

## Reflexión

Recon, loot, escalada y pivoting se potencian entre sí: un secreto legible, una
shell SUID y una red interna permisiva eliminan capas sucesivas. La mitigación
efectiva aplica mínimo privilegio y verificación en cada capa.

## Fuentes

1. MITRE ATT&CK, **T1548.001 — Setuid and Setgid**.  
   https://attack.mitre.org/techniques/T1548/001/
2. MITRE ATT&CK, **T1021 — Remote Services**.  
   https://attack.mitre.org/techniques/T1021/
3. OWASP Foundation, **Secrets Management Cheat Sheet**.  
   https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
