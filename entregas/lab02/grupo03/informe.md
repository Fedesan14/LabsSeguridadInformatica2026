# Informe — Laboratorio 02 · Criptografía

**Grupo:** 03 · **Fecha:** `12-10-2026`

### Integrantes

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| Federico Sánchez | `13614` | @Fedesan14 |
| Elian Enria | `13245` | @elian-enria-id |
| Efraín Host | `18273` | @hostefrain |
| Lohana Rumis | `14646` | @Lohana-Rumis |

### Distribución del trabajo

Reparto por componente de la rúbrica. Cada integrante es responsable de su
componente de punta a punta —código, redacción y defensa oral— y commitea su
parte desde su propia cuenta.

| Integrante | Componente | Pts. | Qué produce |
|---|---|---:|---|
| Federico Sánchez | Parte A — análisis de la falla | 30 | Sección 1 completa de este informe (A.1 a A.5), incluida la verificación de las ocho fuentes |
| Efraín Host | Parte B.1 — romper el XOR | 25 | `src/cripto.py`: `romper_xor_1byte()` y el conjunto `_FRECUENTES`. Sección 2 de este informe |
| Elian Enria | Parte B.2 — MAC ingenuo vs HMAC | 30 | `src/cripto.py`: `mac_ingenuo()`, `mac_hmac()` y `verificar_mac()`. Sección 3 de este informe (B.2.1 a B.2.3) |
| Lohana Rumis | Mini-research y verificación | 10 | [`research.md`](research.md) completo (tema C). `test_cripto.py`. Secciones 0 y 4 de este informe |

Los 5 puntos restantes de la rúbrica son de **proceso Git** y son colectivos.
Federico Sánchez, como responsable del fork, se encarga de sincronizar `main`
con `upstream` y de abrir el Pull Request.

**Caso asignado (Parte A):** MD5 / colisiones — uso de una función de hash rota
para certificados. Asignación por la regla del enunciado: `3 mod 5 = 3`.

**Mini-research:** tema **C** — Derivación de claves desde contraseñas (PBKDF2, bcrypt, Argon2): por qué un sha256(password) no alcanza
([`research.md`](research.md)).

---

## 0. Declaración de uso de IA

**¿El grupo usó asistentes de IA en este trabajo?** **Sí.**

| Herramienta | Para qué se usó | Qué partes del entregable afectó | Cómo se verificó que lo devuelto era correcto |
|---|---|---|---|
| Claude Code (Anthropic, modelo Opus 5) | Consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis), ayuda para la redacción de algunas secciones del informe | informe.md; cripto.py; research.md | | Las respuestas conceptuales se contrastaron contra las fuentes primarias citadas en el informe; nada se incorporó al texto final sin que el integrante responsable de cada sección lo revisara |
| GitHub Copilot con modelo Claude Sonnet 5 | Consultas varias durante el desarrollo (dudas conceptuales, dudas de sintaxis) y revisiones de código ya escrito | informe.md; cripto.py; research.md; test_cripto.py | Cada sugerencia se leyó línea por línea antes de aceptarla, comparando el comportamiento propuesto contra lo que la función debía hacer |

**Cómo se repartió la revisión.** Cada integrante trabajó su componente según la distribución del trabajo, consultando a los asistentes de IA puntualmente para dudas conceptuales, de sintaxis o de resacción, y commiteó su parte desde su propia cuenta.

**Declaración.** El grupo declara que todo el contenido entregado fue revisado y comprendido por los integrantes responsables de cada parte, y que las herramientas de IA mencionadas se usaron como apoyo puntual y no como reemplazo del trabajo propio del equipo.

---

## 1. Parte A — Análisis de la falla

**Caso:** MD5 / colisiones — uso de una función de hash rota para firmar certificados. 

### A.1 — Qué prometía el sistema

La infraestructura de clave pública (PKI) utilizada por HTTPS se basa en certificados digitales X.509 firmados por Autoridades Certificadoras (CA). La firma de la CA permite al cliente verificar que el certificado fue emitido por una autoridad de confianza y que su contenido no fue modificado. Por lo tanto, el sistema buscaba garantizar principalmente la **autenticidad e integridad** del certificado presentado por un servidor. [1][2]

En una firma basada en hash, la resistencia a colisiones de la función hash es una propiedad necesaria: no debería ser factible construir dos contenidos diferentes que produzcan el mismo resumen y, por lo tanto, puedan compartir efectivamente una misma firma. NIST identifica explícitamente la resistencia a colisiones como una propiedad requerida para las funciones hash utilizadas en aplicaciones de firma digital. [3]

### A.2 — El mal uso concreto

El problema concreto fue que algunas Autoridades Certificadoras **continuaron utilizando MD5 como función hash para firmar certificados digitales**, aun cuando ya se conocían ataques prácticos contra su resistencia a colisiones. El problema no era simplemente que “MD5 era malo”, sino utilizarlo específicamente en un contexto —firmas digitales de certificados— donde la resistencia a colisiones era una propiedad de seguridad indispensable. [2][4]

En 2008, investigadores demostraron que este uso podía explotarse en la práctica. Aprovecharon que una CA comercial todavía emitía certificados firmados mediante MD5 y construyeron dos estructuras de certificado cuyos contenidos eran diferentes pero cuyos hashes MD5 coincidían. Una correspondía a un certificado ordinario que la CA estaba dispuesta a firmar; la otra correspondía a un certificado preparado por los atacantes para funcionar como una **Autoridad Certificadora fraudulenta (rogue CA)**. [4][5]

### A.3 — Propiedad rota y cómo se explotó

Las propiedades comprometidas fueron principalmente la **autenticidad** y la **integridad**.

Los investigadores utilizaron un ataque de colisión de prefijo elegido (*chosen-prefix collision*) contra MD5 para preparar un certificado legítimo y un certificado CA fraudulento de manera que ambos produjeran el mismo hash MD5. Obtuvieron de una CA comercial una firma válida sobre el certificado legítimo; debido a la colisión, esa firma también resultaba válida para el certificado CA fraudulento. [4][5]

El resultado fue una CA controlada por los investigadores pero cuya cadena de confianza podía ser aceptada por los navegadores. Con ella era posible generar certificados para sitios arbitrarios que aparentaran ser legítimos. En un escenario de ataque, esto podía utilizarse para suplantar sitios o personas y facilitar ataques de intermediario (*man-in-the-middle*) o phishing sin que la validación normal del certificado detectara que éste había sido emitido por una CA fraudulenta. Microsoft describió precisamente que una colisión MD5 podía permitir generar un certificado fraudulento derivado de uno válido y utilizarlo para suplantar un sitio o una persona. [2][6]

La **confidencialidad no fue la propiedad criptográfica rota directamente**: el fallo inicial fue que ya no podía confiarse en la autenticidad e integridad proporcionadas por la firma del certificado. Sin embargo, una vez conseguida la suplantación, un atacante situado en condiciones de interceptar la comunicación podía comprometer posteriormente la confidencialidad del tráfico. [2][6]

### A.4 — La forma correcta de haberlo hecho

Las Autoridades Certificadoras debían dejar de utilizar MD5 para firmas digitales y emplear una función hash con resistencia a colisiones adecuada como lo es SHA-256. El IETF establece explícitamente que **MD5 ya no es aceptable cuando se requiere resistencia a colisiones, como ocurre en las firmas digitales**. [7]


## Fuentes

[1] Microsoft Security Advisory 961509, *Vulnerability in the certificate validation could allow spoofing*, Microsoft Security Response Center, 2008.
https://learn.microsoft.com/en-us/security-updates/securityadvisories/2008/961509

[2] Microsoft Security Response Center, *Information regarding MD5 collisions problem*, 30 de diciembre de 2008.
https://www.microsoft.com/en-us/msrc/blog/2008/12/information-regarding-md5-collisions-problem

[3] NIST Special Publication 800-106, *Randomized Hashing for Digital Signatures*. National Institute of Standards and Technology.
https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-106.pdf

[4] Stevens, M.; Sotirov, A.; Appelbaum, J.; Lenstra, A.; Molnar, D.; Osvik, D. A.; de Weger, B., *Short Chosen-Prefix Collisions for MD5 and the Creation of a Rogue CA Certificate*, CRYPTO 2009.
https://eprint.iacr.org/2009/111

[5] Stevens, M. et al., *MD5 considered harmful today — Creating a rogue CA certificate*.
https://marc-stevens.nl/research/hashclash/rogue-ca/

[6] Microsoft Security Response Center, *Information on Microsoft Security Advisory 961509*, 30 de diciembre de 2008.
https://www.microsoft.com/en-us/msrc/blog/2008/12/information-on-microsoft-security-advisory-961509

[7] IETF, RFC 6151, *Updated Security Considerations for the MD5 Message-Digest and the HMAC-MD5 Algorithms*, 2011.
https://datatracker.ietf.org/doc/html/rfc6151
---

## 2. Parte B.1 — Romper el XOR

**Clave hallada:** 0x37

**Mensaje en claro recuperado:**

Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.

### Por qué falla el cifrado clásico

El cifrado XOR utiliza una clave de solo un byte, por lo que existen únicamente 256 claves posibles. Esto permite probar todas las combinaciones mediante fuerza bruta y utilizar análisis de frecuencia para identificar cuál genera un texto con mayor probabilidad de ser lenguaje natural. Por este motivo, una clave tan corta no ofrece una protección adecuada.

---

## 3. Parte B.2 — Autenticación

### B.2.1 — ¿Por qué `sha256(clave ‖ mensaje)` permite length-extension?

**Por la construcción interna de SHA-256.** SHA-256 es **Merkle–Damgård**:
rellena la entrada, la parte en bloques de 512 bits y encadena
`H_i = f(H_(i-1), M_i)`. La salida que devuelve es `H_n`, es decir **el estado
interno completo, sin ninguna finalización que lo oculte**. Un digest de SHA-256
no es un resumen opaco: es un *checkpoint* del que se puede seguir hasheando.
(SHA-3, por ser una esponja, y SHA-512/256, por truncar, no tienen esta
propiedad.)

Con `MAC = sha256(clave ‖ msg)`, el atacante recibe precisamente ese checkpoint.

**Qué puede falsificar sin conocer la clave.** Sobre nuestro propio ejemplo:
conoce `msg = "pago 100"` y su tag ingenuo
`a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725`. Sólo le
falta `len(clave)` —7 en el ejemplo— y si no la sabe la prueba de 1 a 64: son 64
intentos, no una fuerza bruta.

| # | Paso del ataque |
|---|---|
| 1 | Reconstruye el relleno que SHA-256 aplicó a `clave‖msg` (15 bytes): un byte `0x80`, luego ceros, y la longitud en bits en 64 bits *big-endian* (`0x0000000000000078` = 120), hasta completar los 64 bytes del bloque. Es determinístico y depende sólo de la **longitud**, no del contenido. |
| 2 | Inicializa la función de compresión **usando el tag como estado inicial** y le procesa su propio sufijo, por ejemplo `&monto=999999`. |
| 3 | Obtiene un tag válido para `clave ‖ "pago 100" ‖ relleno ‖ "&monto=999999"` **sin haber tocado la clave en ningún momento**. |
| 4 | Envía ese mensaje extendido con el tag nuevo. El servidor calcula `sha256(clave ‖ mensaje_recibido)`, obtiene el mismo valor y **acepta**. |

Los bytes de relleno quedan como basura binaria en medio del mensaje, y ahí está
el detalle que vuelve práctico el ataque: en cualquier formato tolerante —una
*query string*, un JSON laxo, un CSV, o un backend que ante un parámetro
repetido se queda con **el último**— esa basura se ignora y el sufijo del
atacante es el que manda. `user=bob&monto=100` + relleno + `&monto=999999`
autoriza una transferencia de un millón con la firma de una de cien.

**Lo que el ataque no permite:** recuperar la clave, modificar el prefijo
original ni acortar el mensaje. Pero pasar de "no puedo falsificar nada" a
"puedo falsificar cualquier cosa que **termine** con lo que yo elija" alcanza y
sobra para romper una autorización. Hay herramientas listas (`hash_extender`,
`HashPump`) y casos reales: la API de **Flickr** cayó en 2009 por usar
`md5(secreto ‖ parámetros)` [9].

### B.2.2 — ¿Cómo lo resuelve HMAC estructuralmente?

```
HMAC(K, m) = H( (K' ⊕ opad) ‖ H( (K' ⊕ ipad) ‖ m ) )
```

con `ipad` = `0x36` repetido, `opad` = `0x5c` repetido, y `K'` la clave rellenada
a un bloque (o `H(K)` si es más larga que un bloque).

**Dos capas, y la clave entra en las dos.** Ahí está todo. El hash **externo**
funciona como la etapa de finalización que Merkle–Damgård no tiene: el valor que
el atacante recibe ya **no es** el estado interno de un hash que contiene el
mensaje, sino la salida de un hash cuyo **primer bloque es `K' ⊕ opad`**, que
depende de la clave y que él no conoce.

Para extender necesitaría el estado interno del hash externo, y para calcularlo
tendría que haber procesado `K' ⊕ opad`. No puede. Y aunque intentara extender
el hash externo desde su salida, esa entrada tiene **longitud fija** —un bloque
más los 32 bytes del hash interno— y termina ahí: no hay nada que el atacante
pueda concatenar y que el verificador vaya a recalcular. **La superficie de
ataque desaparece por construcción, no por un parche.**

**No es sólo intuición: hay demostración.** Bellare, Canetti y Krawczyk (1996)
[8], y luego Bellare (2006), reducen la seguridad de HMAC como PRF a que la
función de compresión sea una PRF — **sin exigir resistencia a colisiones del
hash**. Ese resultado explica el hecho que aparece en la Parte A.3: HMAC-MD5
siguió siendo aceptable después de que las colisiones de MD5 destruyeran las
firmas de certificados. Mismo algoritmo roto, dos usos, dos destinos distintos,
porque cada uso apoya su seguridad en una propiedad diferente.

**En la práctica:** `hmac.new(clave, msg, hashlib.sha256)` es una línea de la
biblioteca estándar. No hay ninguna razón de ingeniería para escribir
`sha256(clave + msg)` en su lugar.

### B.2.3 — ¿Qué ataque evita comparar en tiempo constante?

**Evita un *timing attack* que reconstruye el tag carácter por carácter.**

`==` sobre `str` o `bytes` termina en un `memcmp` que **retorna en el primer
byte distinto**. El tiempo de la comparación es entonces una función de cuántos
caracteres iniciales acertó el atacante: el propio tiempo de respuesta se
convierte en un oráculo que le dice "vas bien hasta acá".

**El ataque, concreto.** Un endpoint `POST /transferir` con
`monto=999999&tag=<64 hex>` que valida con `tag_recibido == tag_esperado`:

1. El atacante manda 64 caracteres cualesquiera y varía **sólo el primero** entre
   los 16 valores hexadecimales, midiendo el tiempo de respuesta y promediando
   muchas repeticiones de cada uno.
2. El valor correcto tarda un poco más: el `memcmp` hace una iteración extra
   antes de cortar. Lo fija.
3. Repite con el segundo carácter, el tercero, y así.

**Costo total: 16 × 64 = 1024 grupos de mediciones**, en lugar de 16^64 ≈ 2^256
intentos. Un espacio de búsqueda astronómico se vuelve lineal.

**Realismo del ataque.** Sobre una red, el *jitter* es órdenes de magnitud mayor
que la diferencia de un byte, así que hace falta estadística: muchas muestras
por candidato, y quedarse con el **mínimo** observado, que filtra mejor que el
promedio. Crosby, Wallach y Riedi (2009) [10] midieron que así se distinguen
diferencias del orden de **100 ns en una LAN** y de decenas de microsegundos
sobre Internet. Si el atacante es un proceso local, o un vecino en el mismo host
de nube, el ataque es directamente cómodo.

**Qué hace `hmac.compare_digest`.** Recorre **siempre la longitud completa**,
acumulando las diferencias en lugar de cortar:

```python
resultado = 0
for x, y in zip(a, b):
    resultado |= x ^ y
return resultado == 0
```

El tiempo depende de la longitud del tag —que es pública— y no de su contenido.
Por eso `verificar_mac()` lo usa, y por eso codifica a `bytes` antes de
comparar: `recibido` es un dato que viene de afuera y `compare_digest` rechaza
`str` con caracteres no ASCII.

**Lo que `compare_digest` no arregla:** no salva un tag demasiado corto, no
protege el secreto de otros canales de filtración, y no sirve si hay una
diferencia de tiempo *antes* de la comparación (por ejemplo, consultar la base
de datos sólo cuando el `key_id` existe). El tiempo constante hay que mirarlo en
todo el camino de validación, no sólo en la última línea.

### Fuentes de la Parte B

| # | Fuente |
|---|---|
| [8] | Bellare, M., Canetti, R., & Krawczyk, H. (1996). *Keying hash functions for message authentication.* CRYPTO 1996, LNCS 1109, 1–15. |
| [9] | Duong, T., & Rizzo, J. (2009). *Flickr's API signature forgery vulnerability.* |
| [10] | Crosby, S. A., Wallach, D. S., & Riedi, R. H. (2009). *Opportunities and limits of remote timing attacks.* ACM TISSEC, 12(3). |
| [11] | Krawczyk, H., Bellare, M., & Canetti, R. (1997). *RFC 2104 — HMAC: Keyed-hashing for message authentication.* IETF. |
| [12] | NIST (2015). *FIPS 180-4: Secure Hash Standard* — construcción y relleno de SHA-256. |
| [13] | Nystrom, M., & Kaliski, B. (2005). *RFC 4231 — Identifiers and test vectors for HMAC-SHA-224/256/384/512.* IETF (vectores usados en `test_cripto.py`). |

---

## 4. Bitácora

Secuencia completa de comandos corridos desde entregas/lab02/grupo03/, en el ordern en que se fueron necesitando para resolver la Parte B y después verificarla.

```bash
# Paso 0 - generar el reto de la Parte B.1
$ python3 data/generar_datos.py
Creado data/muestra/reto_xor.hex — rompelo con: python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)

# Paso 2 - chequeo de que el esqueleto corre (xor_cifrar viene dado en el enunciado)
$ python3 src/cripto.py xor --texto hola --clave K
2324272a

# Paso 2 - Parte B.1: fuerza bruta de la clave de 1 byte + análisis de frecuencia
$ python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)
clave=0x37
Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.

# Paso 3 - Parte .2: el MAC "ingenuo" (sha256(clave||msg)), el que NO hay que usar
$ python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo ingenuo
a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725

# Paso 4 - Parte B.2: HMAC-SHA256, la construcción correcta
$ python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo hmac
5ec4a52407221836a66e8d654d914aaa4b18bd31cf31907348bcd292677b902e

# Paso 5 - no alcanza con que el resultado sea consistente consigo mismo: se
# recalculan los dos valores con una herramienta externa (openssl) para
# confirmar que coinciden bit a bit
$ printf 'pago 100' | openssl dgst -sha256 -hmac secreta
SHA2-256(stdin)= 5ec4a52407221836a66e8d654d914aaa4b18bd31cf31907348bcd292677b902e

$ printf 'secretapago 100' | openssl dgst -sha256
SHA2-256(stdin)= a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725

# Paso 6 - suite de tests propia, contra vectores publicados (RFC 4231 / FIPS 180-4)
$ python3 test_cripto.py
  ok  test_ingenuo_y_hmac_no_son_lo_mismo
  ok  test_mac_hmac_contra_vector_rfc4231
  ok  test_mac_ingenuo_es_sha256_de_la_concatenacion
  ok  test_romper_no_explota_con_entrada_vacia
  ok  test_romper_recupera_clave_y_mensaje
  ok  test_verificar_mac

6 pruebas OK

$ echo "codigo de salida: $?"
codigo de salida: 0
```

**Los dos MAC del mismo par (clave, mensaje) dan valores distintos**, como tiene
que ser: son construcciones diferentes, no dos nombres de lo mismo. Y los dos
coinciden con `openssl`, que es una implementación ajena a este código: eso es
lo que permite afirmar que están bien, y no sólo que son consistentes consigo
mismos.
## 3. MD5 / colisiones — uso de una función de hash rota para certificados

### A.1 — ¿Qué prometía el sistema?

La infraestructura de clave pública (PKI) utilizada por HTTPS se basa en certificados digitales X.509 firmados por Autoridades Certificadoras (CA). La firma de la CA permite al cliente verificar que el certificado fue emitido por una autoridad de confianza y que su contenido no fue modificado. Por lo tanto, el sistema buscaba garantizar principalmente la **autenticidad e integridad** del certificado presentado por un servidor. [1][2]

En una firma basada en hash, la resistencia a colisiones de la función hash es una propiedad necesaria: no debería ser factible construir dos contenidos diferentes que produzcan el mismo resumen y, por lo tanto, puedan compartir efectivamente una misma firma. NIST identifica explícitamente la resistencia a colisiones como una propiedad requerida para las funciones hash utilizadas en aplicaciones de firma digital. [3]

### A.2 — ¿Cuál fue el mal uso concreto?

El problema concreto fue que algunas Autoridades Certificadoras **continuaron utilizando MD5 como función hash para firmar certificados digitales**, aun cuando ya se conocían ataques prácticos contra su resistencia a colisiones. El problema no era simplemente que “MD5 era malo”, sino utilizarlo específicamente en un contexto —firmas digitales de certificados— donde la resistencia a colisiones era una propiedad de seguridad indispensable. [2][4]

En 2008, investigadores demostraron que este uso podía explotarse en la práctica. Aprovecharon que una CA comercial todavía emitía certificados firmados mediante MD5 y construyeron dos estructuras de certificado cuyos contenidos eran diferentes pero cuyos hashes MD5 coincidían. Una correspondía a un certificado ordinario que la CA estaba dispuesta a firmar; la otra correspondía a un certificado preparado por los atacantes para funcionar como una **Autoridad Certificadora fraudulenta (rogue CA)**. [4][5]

### A.3 — ¿Qué propiedad se rompió y cómo se explotó?

Las propiedades comprometidas fueron principalmente la **autenticidad** y la **integridad**.

Los investigadores utilizaron un ataque de colisión de prefijo elegido (*chosen-prefix collision*) contra MD5 para preparar un certificado legítimo y un certificado CA fraudulento de manera que ambos produjeran el mismo hash MD5. Obtuvieron de una CA comercial una firma válida sobre el certificado legítimo; debido a la colisión, esa firma también resultaba válida para el certificado CA fraudulento. [4][5]

El resultado fue una CA controlada por los investigadores pero cuya cadena de confianza podía ser aceptada por los navegadores. Con ella era posible generar certificados para sitios arbitrarios que aparentaran ser legítimos. En un escenario de ataque, esto podía utilizarse para suplantar sitios o personas y facilitar ataques de intermediario (*man-in-the-middle*) o phishing sin que la validación normal del certificado detectara que éste había sido emitido por una CA fraudulenta. Microsoft describió precisamente que una colisión MD5 podía permitir generar un certificado fraudulento derivado de uno válido y utilizarlo para suplantar un sitio o una persona. [2][6]

La **confidencialidad no fue la propiedad criptográfica rota directamente**: el fallo inicial fue que ya no podía confiarse en la autenticidad e integridad proporcionadas por la firma del certificado. Sin embargo, una vez conseguida la suplantación, un atacante situado en condiciones de interceptar la comunicación podía comprometer posteriormente la confidencialidad del tráfico. [2][6]

### A.4 — ¿Cuál era la forma correcta de hacerlo?

Las Autoridades Certificadoras debían dejar de utilizar MD5 para firmas digitales y emplear una función hash con resistencia a colisiones adecuada como lo es SHA-256. El IETF establece explícitamente que **MD5 ya no es aceptable cuando se requiere resistencia a colisiones, como ocurre en las firmas digitales**. [7]

## Fuentes

[1] Microsoft Security Advisory 961509, *Vulnerability in the certificate validation could allow spoofing*, Microsoft Security Response Center, 2008.
https://learn.microsoft.com/en-us/security-updates/securityadvisories/2008/961509

[2] Microsoft Security Response Center, *Information regarding MD5 collisions problem*, 30 de diciembre de 2008.
https://www.microsoft.com/en-us/msrc/blog/2008/12/information-regarding-md5-collisions-problem

[3] NIST Special Publication 800-106, *Randomized Hashing for Digital Signatures*. National Institute of Standards and Technology.
https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-106.pdf

[4] Stevens, M.; Sotirov, A.; Appelbaum, J.; Lenstra, A.; Molnar, D.; Osvik, D. A.; de Weger, B., *Short Chosen-Prefix Collisions for MD5 and the Creation of a Rogue CA Certificate*, CRYPTO 2009.
https://eprint.iacr.org/2009/111

[5] Stevens, M. et al., *MD5 considered harmful today — Creating a rogue CA certificate*.
https://marc-stevens.nl/research/hashclash/rogue-ca/

[6] Microsoft Security Response Center, *Information on Microsoft Security Advisory 961509*, 30 de diciembre de 2008.
https://www.microsoft.com/en-us/msrc/blog/2008/12/information-on-microsoft-security-advisory-961509

[7] IETF, RFC 6151, *Updated Security Considerations for the MD5 Message-Digest and the HMAC-MD5 Algorithms*, 2011.
https://datatracker.ietf.org/doc/html/rfc6151
