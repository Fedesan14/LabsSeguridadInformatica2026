# Informe — Laboratorio 03 · Autenticación

**Grupo:** XX · **Integrantes:** *(nombre — usuario GitHub)*

## 0. Declaración de uso de IA
## 1. Parte A — Análisis de la brecha (caso, falla, explotación, lo correcto; con fuentes)
## 2. Parte B.1 — Contraseñas (por qué salt por usuario, por qué muchas iteraciones)
## 3. Parte B.2 — TOTP (por qué frena el robo de contraseña; qué NO protege)

*Responsable: Elian Enria.*

### Implementación

```python
return hotp(secret, int(time.time() if t is None else t) // paso, digitos)
```

TOTP (RFC 6238) es HOTP (RFC 4226) con un contador que no se guarda ni se
sincroniza: es `t // 30`, la cantidad de pasos de 30 segundos desde la época
Unix. Servidor y teléfono comparten un secreto una sola vez —el QR del alta— y
a partir de ahí cada uno calcula el contador con su propio reloj. HOTP hace un
HMAC-SHA1 del contador con el secreto y lo trunca a 6 dígitos.

La comparación es `t is None` y no `not t`, porque `t = 0` es un instante válido
y `not 0` es verdadero: con `not t` se usaría el reloj en vez de la época.

**Verificación contra el vector oficial.** Con el secreto ASCII
`12345678901234567890` y `t = 59`, el contador es `59 // 30 = 1` y el código da
**287082**; con 8 dígitos da **94287082**, que es el valor de la tabla del
Apéndice B de la RFC 6238. `test_totp.py` contrasta además los otros cinco
instantes de esa tabla.

### ¿Por qué el TOTP frena a quien robó la contraseña?

Porque convierte la autenticación en **dos factores de naturaleza distinta**: la
contraseña es *algo que sabés*; el secreto TOTP es *algo que tenés*, y vive en
el teléfono, no en la base de datos de contraseñas ni en la cabeza del usuario.

- **La contraseña robada ya no alcanza.** Una filtración como las de la Parte A,
  o un ataque de *credential stuffing* con contraseñas reutilizadas, le da al
  atacante el primer factor y nada del segundo.
- **El código robado vence solo.** Vale para una ventana de 30 segundos (más una
  o dos ventanas de tolerancia al desfase de reloj). Un código interceptado no
  se puede guardar y usar mañana.
- **El código no revela el secreto.** Es la salida truncada de un HMAC: ver uno o
  muchos códigos no permite calcular los siguientes sin el secreto.

### ¿Qué NO protege el TOTP?

- **Phishing en tiempo real.** Un sitio falso que hace de intermediario pide la
  contraseña y el código, y los usa contra el sitio real dentro de los 30
  segundos (herramientas como Evilginx automatizan esto). El código es válido:
  TOTP no sabe **a qué sitio** se lo están dando. Lo que sí resiste esto son las
  credenciales ligadas al origen, como FIDO2/WebAuthn (passkeys).
- **El robo del secreto.** Si se filtra la base de secretos TOTP del servidor, o
  el atacante ve el QR del alta o accede a la app del teléfono, puede generar
  códigos válidos para siempre: el secreto es simétrico y está en los dos lados.
- **Lo que pasa después del login.** Un malware en el equipo que roba la cookie
  de sesión, o un token de API filtrado, se saltea el segundo factor porque ya
  está autenticado.
- **La recuperación de cuenta.** Si "olvidé mi 2FA" se resuelve por mail o SMS,
  el segundo factor efectivo es esa cuenta de mail o esa línea (SIM swapping).
- **La autorización.** TOTP confirma **quién** sos, no **qué** podés hacer. Un
  usuario legítimo con 2FA igual tiene que pasar por controles de acceso en el
  servidor.
- **Fuerza bruta sin límite de intentos.** Son 10⁶ combinaciones: sin bloqueo o
  limitación de intentos en el servidor, un atacante con la contraseña puede
  recorrer los códigos dentro de la ventana.

### Fuentes de B.2

| # | Fuente |
|---|---|
| [1] | M'Raihi, D., Machani, S., Pei, M., & Rydell, J. (2011). *RFC 6238 — TOTP: Time-Based One-Time Password Algorithm.* IETF. Apéndice B: vectores de prueba. |
| [2] | M'Raihi, D., Bellare, M., Hoornaert, F., Naccache, D., & Ranen, O. (2005). *RFC 4226 — HOTP: An HMAC-Based One-Time Password Algorithm.* IETF. |
| [3] | NIST (2017, actualizada). *SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management.* Autenticadores OTP y resistencia a phishing. |
| [4] | OWASP. *Multifactor Authentication Cheat Sheet.* |
## 4. Bitácora de comandos

### B.2 — TOTP

```bash
$ python3 src/auth.py totp --secret 12345678901234567890 --t 59
287082

$ python3 test_totp.py
  ok  test_el_codigo_tiene_seis_digitos_con_ceros_a_la_izquierda
  ok  test_mismo_paso_mismo_codigo
  ok  test_sin_t_usa_el_reloj
  ok  test_t_cero_es_un_instante_valido
  ok  test_vector_del_enunciado_6_digitos
  ok  test_vectores_rfc6238_8_digitos

6 pruebas OK
```
