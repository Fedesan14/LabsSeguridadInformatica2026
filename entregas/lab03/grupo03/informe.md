# Informe — Laboratorio 03 · Autenticación

**Grupo:** 03

**Mini-research:** tema **A**, PBKDF2 vs bcrypt vs scrypt vs Argon2: por qué
existen "hashes lentos" ([`research.md`](research.md)).

## 0. Declaración de uso de IA

Claude Code (Anthropic, modelo Opus 5) para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe.
GitHub Copilot con modelo Claude Sonnet 5 para consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito.

## 1. Parte A — Análisis de la brecha

### Introducción

La autenticación es el proceso mediante el cual una persona, un servicio o un
dispositivo demuestra que es la identidad que afirma ser. No alcanza con que el
algoritmo criptográfico sea sólido: la implementación completa también debe
evitar que sus tiempos de ejecución revelen información sobre los secretos que
compara. Este informe analiza los **ataques de timing** asignados al Grupo 03
(`3 mod 4 = 3`), en particular la comparación insegura de tokens y códigos de
autenticación de mensajes (MAC).

Un ataque de timing es un ataque de canal lateral. El atacante no rompe
directamente el algoritmo ni necesita leer la memoria del servidor; envía muchas
entradas elegidas, mide cuánto tarda cada respuesta y usa las diferencias para
inferir estado interno. MITRE clasifica esta debilidad como
[CWE-208: Observable Timing Discrepancy](https://cwe.mitre.org/data/definitions/208.html).
Aunque cada diferencia sea muy pequeña y la red agregue ruido, las mediciones
repetidas y su análisis estadístico pueden recuperar una señal útil. Brumley y
Boneh demostraron en 2003 que un ataque de timing remoto podía extraer una clave
RSA privada de un servidor basado en OpenSSL dentro de una red local, refutando
la idea de que estos ataques solo eran viables contra dispositivos físicos.

### Autenticación, autorización y factores

**Autenticación** responde «¿quién sos?»: establece confianza en una identidad a
partir del control de uno o más autenticadores. **Autorización** responde «¿qué
podés hacer?»: una vez identificada la entidad, decide si puede ejecutar una
acción o acceder a un recurso. Por ejemplo, iniciar sesión con contraseña y TOTP
autentica a una persona; permitirle leer su propia factura pero no la de otro
cliente es una decisión de autorización. Autenticarse correctamente no implica
tener permiso para todo. Las definiciones coinciden con el
[modelo de identidad digital de NIST SP 800-63-4](https://pages.nist.gov/800-63-4/sp800-63/model/)
y con la definición de
[autorización del glosario de NIST](https://csrc.nist.gov/glossary/term/authorization).

Los tres factores de autenticación son:

- **Algo que sabés:** una contraseña, frase de paso o PIN.
- **Algo que tenés:** un teléfono con una clave TOTP, una llave de seguridad o
  un dispositivo que almacena una clave criptográfica.
- **Algo que sos:** una característica biométrica, como una huella o el rostro.

Para que exista autenticación multifactor se deben combinar factores de clases
distintas. Contraseña más PIN siguen siendo un único factor de conocimiento;
contraseña más una llave de seguridad sí constituyen dos factores. NIST también
advierte que una biometría no es un secreto y, en sus guías, se usa junto con un
autenticador físico, no como autenticador único.

### Caso analizado: comparación insegura de un HMAC en Google Keyczar

En 2009, el investigador Nate Lawson informó una vulnerabilidad de timing en la
verificación HMAC de la biblioteca criptográfica Google Keyczar. Las
implementaciones afectadas comparaban el HMAC calculado con la firma recibida
mediante comparaciones generales: `==` en Python y `Arrays.equals` en Java. La
comparación se detenía al encontrar la primera diferencia. Por lo tanto, una
firma con un prefijo correcto tardaba, en condiciones vulnerables, un poco más
en rechazarse que otra cuyo primer byte ya era incorrecto. El problema no era
SHA-1 como función HMAC, sino **la manera de verificar su resultado**.

Un HMAC permite comprobar integridad y autenticidad: el servidor calcula una
etiqueta sobre un mensaje usando una clave secreta y acepta el mensaje solamente
si coincide con la etiqueta recibida. En una cookie de sesión o en un token, una
etiqueta válida puede ser la barrera que impide modificar una identidad, un rol
o cualquier otro dato protegido. Por eso, revelar progresivamente el valor del
MAC puede terminar en la falsificación de un mensaje que el servidor considere
auténtico.

### Cómo se explota

El atacante necesita poder enviar una gran cantidad de tokens o mensajes con
etiquetas elegidas y medir sus tiempos de respuesta. El ataque conceptual es el
siguiente:

1. Mantiene fijo el mensaje que quiere autenticar y prueba todos los valores
   posibles para el primer byte de la etiqueta.
2. Repite cada prueba muchas veces y compara distribuciones o promedios para
   reducir el ruido producido por la red, la carga y el planificador.
3. El candidato que tarda consistentemente más indica que la comparación avanzó
   al byte siguiente; el atacante lo conserva.
4. Repite el procedimiento para cada posición hasta reconstruir una etiqueta
   aceptada por el servidor.

En un oráculo ideal que filtra un byte por vez, el trabajo pasa de adivinar de
una vez uno entre `256^n` valores a probar aproximadamente 256 candidatos por
cada una de las `n` posiciones, además de las repeticiones estadísticas. El
ruido puede volver el ataque costoso o incluso impráctico en un entorno dado,
pero no elimina la vulnerabilidad. En la prueba de Keyczar se distinguieron los
tiempos en un servidor local; la investigación previa de Brumley y Boneh ya
había establecido que los canales temporales también podían explotarse a través
de una red. La consecuencia de Keyczar era poder forjar firmas HMAC para datos
elegidos, lo que, según el uso del token, podía permitir suplantar identidades o
alterar mensajes protegidos.

### Implementación correcta y controles complementarios

La etiqueta recibida y la calculada deben compararse con una **primitiva de
comparación en tiempo constante** provista por una biblioteca criptográfica. En
Python corresponde usar `hmac.compare_digest()`:

```python
import hmac

def verificar_etiqueta(mensaje: bytes, recibida: bytes, clave: bytes) -> bool:
    esperada = hmac.digest(clave, mensaje, "sha256")
    return hmac.compare_digest(esperada, recibida)
```

Esta función evita el cortocircuito dependiente del contenido. No se debe
reemplazar por `esperada == recibida`, por un bucle artesanal que retorna ante
la primera diferencia ni por una pausa aleatoria: el ruido añadido puede
promediarse y el código manual es fácil de optimizar o implementar
incorrectamente. La documentación oficial de Python aclara que diferencias de
tipo o longitud todavía podrían revelar esos metadatos; por eso el formato y la
longitud esperados deben validarse, y el sistema debe devolver errores uniformes
sin revelar qué etapa falló.

La comparación constante es necesaria, pero no suficiente. La implementación
completa también debería:

- usar un algoritmo MAC estándar, por ejemplo HMAC-SHA-256, y claves aleatorias
  de longitud adecuada, separadas por propósito y almacenadas como secretos;
- autenticar una codificación inequívoca de todos los campos relevantes, no
  concatenaciones ambiguas;
- limitar intentos y monitorear fallos repetidos para dificultar la recolección
  masiva de muestras;
- usar TLS, expiración y un `nonce` o número de secuencia cuando corresponda,
  para reducir interceptación y repetición;
- aplicar el control en el servidor y no confiar en validaciones del cliente.

OWASP recomienda expresamente recomputar el HMAC y compararlo con una función de
tiempo constante. La limitación de intentos y los errores uniformes son defensa
en profundidad: no corrigen por sí solos una comparación que filtra información.

### Conclusiones de la Parte A

El caso demuestra que la seguridad de un sistema de autenticación depende tanto
de sus detalles de implementación como de sus primitivas criptográficas. Un HMAC
correctamente calculado puede perder su finalidad si se verifica con una
comparación que abandona el trabajo al encontrar el primer byte distinto. Los
tiempos de rechazo se convierten entonces en un oráculo que permite aprender el
secreto de forma incremental y eventualmente fabricar un token aceptado.

La solución principal es simple de expresar pero debe aplicarse de manera
sistemática: usar comparaciones criptográficas de tiempo constante, validar
formatos sin producir respuestas distinguibles y acompañar la verificación con
limitación de intentos, registro de eventos y gestión segura de claves. Por
último, autenticar una identidad no autoriza automáticamente ninguna operación;
los permisos deben comprobarse por separado, en el servidor y en cada acceso a
un recurso protegido.

### Fuentes de la Parte A

1. MITRE. [*CWE-208: Observable Timing Discrepancy*](https://cwe.mitre.org/data/definitions/208.html).
2. Brumley, D. y Boneh, D. (2003). [*Remote Timing Attacks Are Practical*](https://www.usenix.org/conference/12th-usenix-security-symposium/remote-timing-attacks-are-practical), 12th USENIX Security Symposium.
3. Lawson, N. (2009). [*Timing attack in Google Keyczar library*](https://rdist.root.org/2009/05/28/timing-attack-in-google-keyczar-library/).
4. Python Software Foundation. [`hmac.compare_digest`](https://docs.python.org/3/library/hmac.html#hmac.compare_digest), documentación de la biblioteca estándar.
5. NIST (2025). [*Digital Identity Guidelines, SP 800-63-4 — Digital Identity Model*](https://pages.nist.gov/800-63-4/sp800-63/model/).
6. NIST. [*Computer Security Resource Center Glossary — authorization*](https://csrc.nist.gov/glossary/term/authorization).
7. OWASP. [*Webhook Security Cheat Sheet — Signature Verification*](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html#signature-verification).

## 2. Parte B.1 — Contraseñas (por qué salt por usuario, por qué muchas iteraciones)

### Implementación

```python
if salt is None:
    salt = secrets.token_bytes(16)
dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters)
return f"pbkdf2_sha256${iters}${salt.hex()}${dk.hex()}"
```

`hash_password()` guarda un registro con cuatro campos separados por `$`: el
algoritmo, las iteraciones, el salt y la clave derivada, todo en hexadecimal.
El salt se genera con `secrets.token_bytes()` y no con `random`, porque
`random` usa un generador no criptográfico (Mersenne Twister), predecible si
se conoce parte de su estado; `secrets` usa la fuente de aleatoriedad del
sistema operativo. `verify_password()` separa esos cuatro campos del registro
almacenado, vuelve a derivar la clave con el mismo salt y la misma cantidad de
iteraciones, y compara el resultado con `hmac.compare_digest()` en vez de
`==`, por la misma razón de la Parte A: una comparación que corta al primer
byte distinto es un oráculo de tiempo.

### ¿Por qué un salt aleatorio por usuario?

Sin salt, `hash(password)` da el mismo resultado para dos usuarios con la
misma contraseña, y ese mismo resultado se repite en cualquier otro sistema
que use la misma función de hash. Esto permite dos ataques distintos:

- **Tablas precalculadas (rainbow tables).** Un atacante puede calcular de
  antemano el hash de millones de contraseñas comunes una sola vez y después
  buscar coincidencias instantáneas contra toda una base de datos filtrada.
  RFC 8018 (PKCS#5 v2.1) describe exactamente este problema: sin salt "es
  difícil para un atacante precalcular todas las claves, o incluso las más
  probables, correspondientes a un diccionario de contraseñas". El salt
  rompe esa posibilidad porque cada contraseña necesita su propia tabla.
- **Reconocimiento de contraseñas repetidas.** Con el mismo salt (o sin
  salt), dos hashes idénticos en la base de datos delatan que dos usuarios
  comparten contraseña, sin que haga falta romper ninguna. Con salt por
  usuario, `hash_password("misma")` da un resultado distinto cada vez; la
  prueba automática del lab (`t_pwd_salt` en `verificar.py`) comprueba
  justamente esto.

El salt no es secreto: se guarda junto al hash, en texto plano. Su función no
es esconder nada, es forzar a que el costo del ataque escale con la cantidad
de usuarios, en vez de pagarse una sola vez para toda la base.

### ¿Por qué 200.000 iteraciones y no una sola?

Una sola iteración de SHA-256 es barata: una GPU de gama media calcula miles
de millones de hashes SHA-256 por segundo, y las contraseñas reales tienen
poca entropía (patrones, palabras de diccionario, variantes predecibles), así
que un atacante con la base de datos filtrada puede probar un diccionario
completo en minutos. PBKDF2 repite la derivación miles de veces
deliberadamente para que cada intento sea miles de veces más caro, sin que la
persona que inicia sesión legítimamente note la diferencia (sigue siendo del
orden de milisegundos).

El número concreto subió con el tiempo porque el hardware se abarata: NIST
SP 800-63B (2017) pedía un mínimo histórico de 10.000 iteraciones, y OWASP
recomienda hoy, para PBKDF2-HMAC-SHA256, al menos 600.000 iteraciones si se
necesita cumplir FIPS 140 (y prioriza Argon2id o scrypt para los casos sin esa
restricción). El valor por defecto del lab, 200.000, es un punto intermedio
razonable para el ejercicio, pero en un sistema real conviene medir el tiempo
de verificación en el hardware del servidor y subir las iteraciones hasta el
máximo que la latencia tolere, como indica RFC 8018.

### Verificación

```bash
$ python3 src/auth.py hash --password 'Phantom-2026!'
pbkdf2_sha256$200000$36021bcf00b059401e2d040b0cdbcd0b$91f3d2c2eec0c474a9fcb34c3e60d1776907b68f06e9c44d0cad891b5ddee449

$ python3 src/auth.py verify --password 'Phantom-2026!' --registro 'pbkdf2_sha256$200000$36021bcf00b059401e2d040b0cdbcd0b$91f3d2c2eec0c474a9fcb34c3e60d1776907b68f06e9c44d0cad891b5ddee449'
OK            # exit code 0

$ python3 src/auth.py verify --password 'otra-cosa' --registro 'pbkdf2_sha256$200000$36021bcf00b059401e2d040b0cdbcd0b$91f3d2c2eec0c474a9fcb34c3e60d1776907b68f06e9c44d0cad891b5ddee449'
FALLO         # exit code 1
```

### Fuentes de B.1

| # | Fuente |
|---|---|
| [1] | Moriarty, K., Kaliski, B., & Rusch, A. (2017). *RFC 8018 — PKCS #5: Password-Based Cryptography Specification Version 2.1.* IETF. Define PBKDF2 y el rol del salt y las iteraciones. |
| [2] | NIST (2017, actualizada). *SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management.* Sección 5.1.1.2: requisitos de salt (≥32 bits) e iteraciones (≥10.000) para verificadores de secretos memorizados. |
| [3] | OWASP Foundation. *Password Storage Cheat Sheet.* Recomendación actual de parámetros para PBKDF2, bcrypt, scrypt y Argon2id. |
| [4] | Python Software Foundation. [`hashlib.pbkdf2_hmac`](https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac) y [`secrets`](https://docs.python.org/3/library/secrets.html), documentación de la biblioteca estándar. |

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

### Verificación en el servidor y control de acceso

*Responsable: Lohana Rumis — Integración, pruebas y entrega.*

Todo lo anterior (hash con salt, comparación en tiempo constante, código TOTP)
solo cierra la autenticación. Queda una pregunta distinta: una vez que el
servidor sabe **quién** está del otro lado, ¿quién decide **qué** puede hacer
esa identidad con cada recurso? Esa decisión es autorización, y tiene que
tomarse exclusivamente en el servidor.

- **El cliente no es confiable.** Cualquier chequeo que viva en el navegador o
  en la app, ocultar un botón, deshabilitar un campo, un `if rol === "admin"`
  en JavaScript, es cosmético: el atacante controla por completo las
  peticiones que su cliente envía (`curl`, Burp Suite, las DevTools) y puede
  mandar exactamente la petición que el control visual intentaba impedir. El
  servidor tiene que volver a comprobar el permiso sobre cada petición que
  recibe, sin asumir que si "no se mostraba el botón" nadie va a pedirlo.
- **Un login válido no autoriza todo lo que sigue.** El código TOTP, al igual
  que la contraseña, solo se usa una vez, al autenticar la sesión. Cada acción
  posterior sobre un recurso (leer la factura de un cliente, borrar un
  usuario, cambiar una contraseña ajena) necesita su propio chequeo de
  autorización en el servidor: que la sesión sea válida identifica a la
  persona, no le da automáticamente acceso a los datos de otra. Omitir esta
  verificación por recurso es la causa típica de un **IDOR** (*Insecure Direct
  Object Reference*): el usuario autenticado cambia un identificador en la URL
  o el payload (por ejemplo `factura_id=1042` por `factura_id=1043`) y el
  servidor entrega el recurso de otra cuenta porque solo chequeó que había
  sesión, no que esa sesión fuera dueña de ese recurso. OWASP agrupa esta
  familia de fallas bajo **A01:2021 — Broken Access Control**, la categoría más
  frecuente de su Top 10 2021.
- **Por qué esto conecta con la Parte A y la B.2.** La Parte A mostró que
  autenticar mal (comparación insegura de un MAC) permite falsificar una
  identidad; esta sección muestra el otro lado: aunque la autenticación sea
  perfecta, contraseña con PBKDF2, 2FA con TOTP, un control de acceso que
  confía en el cliente, o que no revalida permisos en cada acción, deja pasar
  a cualquier usuario autenticado (legítimo o atacante que ya robó una sesión)
  hacia recursos que no le corresponden. Autenticación y autorización son
  controles independientes y los dos tienen que estar bien para que el
  sistema sea seguro.
- **Regla práctica.** Denegar por defecto (*fail closed*): si el servidor no
  puede verificar explícitamente que la identidad autenticada tiene permiso
  sobre ese recurso específico, la respuesta es rechazar, no permitir.

### Fuentes de B.2

| # | Fuente |
|---|---|
| [1] | M'Raihi, D., Machani, S., Pei, M., & Rydell, J. (2011). *RFC 6238 — TOTP: Time-Based One-Time Password Algorithm.* IETF. Apéndice B: vectores de prueba. |
| [2] | M'Raihi, D., Bellare, M., Hoornaert, F., Naccache, D., & Ranen, O. (2005). *RFC 4226 — HOTP: An HMAC-Based One-Time Password Algorithm.* IETF. |
| [3] | NIST (2017, actualizada). *SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management.* Autenticadores OTP y resistencia a phishing. |
| [4] | OWASP. *Multifactor Authentication Cheat Sheet.* |
| [5] | OWASP Foundation. (2021). [*A01:2021 — Broken Access Control.*](https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/) OWASP Top 10. |

## 4. Bitácora de comandos

*Control de calidad: Lohana Rumis — Integración, pruebas y entrega. Corrida
completa con Python 3.12 sobre `entregas/lab03/grupo03/`.*

```bash
$ python3 src/verificar.py

== Lab 03 · Autenticación ==
  ✓ hash_password / verify_password
  ✓ salt por usuario (hashes distintos)
  ✓ totp coincide con el vector del RFC 6238

3 OK · 0 a revisar · 0 sin implementar

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

Los comandos de `hash`/`verify` (B.1) quedaron junto a su explicación, en la
sección 2, para no repetir la misma transcripción dos veces.
