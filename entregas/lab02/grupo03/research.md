# Mini-research — Laboratorio 02

**Grupo:** 03

**Tema elegido:** **D.** Cifrado asimétrico y firmas digitales: qué problema
resuelven que el simétrico no.

- [ ] **A.** Modos de operación de cifrado por bloques (ECB vs CBC vs GCM) y por
  qué ECB filtra estructura (el "pingüino" de Adobe).
- [ ] **B.** HMAC y el ataque de length-extension: cómo funciona el ataque y por
  qué HMAC lo previene.
- [ ] **C.** Derivación de claves desde contraseñas (PBKDF2, bcrypt, scrypt,
  Argon2): por qué un `sha256(password)` no alcanza.
- [x] **D.** Cifrado asimétrico y firmas digitales: qué problema resuelven que el
  simétrico no.

## Desarrollo

### Dos problemas que el simétrico no puede resolver

El cifrado simétrico y los MAC son rápidos, están bien entendidos y, cuando se
usan bien, son seguros. Pero los dos comparten un supuesto que no se puede
levantar desde adentro: **las partes ya comparten un secreto**. De ahí salen dos
problemas que ninguna mejora del algoritmo simétrico puede arreglar.

**El primero es de escala y de arranque.** Para que *n* participantes puedan
hablar de a pares hacen falta `n(n-1)/2` claves distintas; con mil participantes
son casi medio millón. Peor: para establecer la primera clave hace falta un canal
seguro previo, y si ese canal existiera no haría falta cifrar. Diffie y Hellman
(1976) [1] lo plantearon exactamente así y propusieron partir la clave en dos
piezas asimétricas, una publicable. Su protocolo permite que dos desconocidos
acuerden un secreto compartido sobre un canal público, y reduce el problema de
`n²` claves secretas a *n* claves públicas.

**El segundo es el no repudio, y es más profundo porque es estructural.** Un
HMAC lo pueden calcular *las dos* partes que comparten la clave. Si Alice
presenta un mensaje con un tag válido y dice "esto lo firmó Bob", Bob puede
responder con toda razón que Alice también podía generarlo: el tag no prueba
autoría ante un tercero, sólo prueba que **alguien del par** lo produjo. Es
autenticación, no atribución. Y esto no es un defecto de HMAC que se pueda
parchear: es una consecuencia de que la capacidad de verificar y la de generar
sean **la misma capacidad**.

La firma digital rompe justamente esa simetría. Sólo el titular de la clave
privada puede producir la firma; cualquiera con la clave pública puede
verificarla. Verificar deja de implicar poder falsificar, y con eso aparece algo
que el simétrico no ofrece: una prueba que un tercero puede evaluar. Eso es lo
que hace posibles los certificados, la firma de código, los repositorios de
paquetes firmados y los documentos con validez legal.

### Se firma el hash, y ahí está el punto de contacto con la Parte A

Ningún esquema práctico firma el mensaje entero. RSA opera sobre enteros módulo
`n`, así que no podría firmar nada más largo que su módulo; y hashear es órdenes
de magnitud más rápido que exponenciar. Lo que se firma es
`Firma(sk, H(mensaje))`.

Esa decisión de ingeniería tiene una consecuencia que conviene decir en voz
alta: **la firma no puede ser más fuerte que el hash**. Si existen dos mensajes
`m1 ≠ m2` con `H(m1) = H(m2)`, entonces una firma de `m1` **es** una firma
válida de `m2`, y ninguna propiedad de RSA lo evita, porque RSA nunca vio los
mensajes. Eso es literalmente el caso analizado en la Parte A de este
laboratorio: la CA intermedia falsa de 2008 no rompió RSA ni robó ninguna clave
privada; construyó dos certificados con el mismo MD5 y **trasplantó la firma**
de uno al otro [6]. La firma digital es el mecanismo que convierte una colisión
de hash en una falsificación de identidad.

### Los esquemas, y por qué los que fallan fallan en el uso

- **RSA PKCS#1 v1.5 vs RSA-PSS** (ambos en la RFC 8017 [3]). El relleno v1.5 es
  determinístico y arrastra un historial de implementaciones que parseaban el
  padding con tolerancia y aceptaban firmas mal formadas; el mismo estándar en su
  variante de cifrado dio lugar al ataque de Bleichenbacher (1998). PSS agrega
  un salt aleatorio y tiene demostración de seguridad. Hoy, para diseños nuevos,
  se recomienda PSS.
- **ECDSA y el nonce `k`.** ECDSA necesita un `k` aleatorio, secreto y **nunca
  reutilizado** por firma. Si se repite en dos firmas, la clave privada se
  despeja con álgebra elemental. Es el caso de la PS3 (fail0verflow, 27C3, 2010):
  Sony usó un `k` constante y el grupo recuperó la clave con la que Sony firmaba
  el código de la consola. Mismo error que el caso 2 del enunciado de este lab.
- **Ed25519** (RFC 8032 [4]). Deriva `k` de forma **determinística** a partir de
  la clave privada y del mensaje, con lo cual la clase entera de bugs por nonce
  malo deja de ser posible. Es el mismo patrón de diseño que HMAC frente a
  `sha256(clave‖msg)`: en vez de documentar cómo no equivocarse, se construye el
  esquema para que el error no exista.

### El costo, y por qué en la práctica todo es híbrido

El asimétrico es entre dos y tres órdenes de magnitud más lento que el simétrico
y expande el tamaño de los datos. Por eso nadie cifra un flujo de video con RSA.
TLS 1.3 [7] es el ejemplo canónico de reparto de tareas: usa asimétrico para lo
que sólo él puede hacer —autenticar al servidor con la firma de su certificado y
acordar un secreto con ECDHE— y a partir de ahí cifra todo el tráfico con un
AEAD simétrico (AES-GCM o ChaCha20-Poly1305). Cada primitiva donde rinde. Y
notemos que el orden importa: sin la firma que autentica el intercambio, un
Diffie-Hellman puro es vulnerable a un intermediario que negocie dos secretos,
uno con cada punta.

### Los límites, que son los que se suelen omitir

1. **La firma vale lo que vale el vínculo identidad↔clave.** La matemática
   garantiza que quien firmó tenía *esa* clave privada; que esa clave pertenezca
   a quien dice el certificado es una afirmación de la PKI, es decir un problema
   **organizacional**. El rogue CA de 2008 lo demuestra: nadie rompió RSA, se
   rompió el proceso de emisión.
2. **No repudio criptográfico ≠ no repudio legal.** Una firma prueba que la clave
   firmó, no que la persona firmó. Si la clave se filtró o estaba en un dispositivo
   compartido, la atribución se cae, y por eso las normativas de firma digital
   exigen resguardo de la clave en hardware.
3. **Computación cuántica.** El algoritmo de Shor rompe factorización y logaritmo
   discreto, es decir RSA y ECDSA por igual. En cambio Grover sólo reduce a la
   mitad el margen efectivo del simétrico, y eso se compensa duplicando el
   tamaño de clave. La asimetría es importante: la urgencia post-cuántica está en
   firmas e intercambio de claves, no en AES ni en HMAC. NIST estandarizó ML-DSA
   para firmas en FIPS 204 [5] en 2024.

## Fuentes (mín. 3, verificables)

| # | Fuente | Tipo |
|---|---|---|
| [1] | Diffie, W., & Hellman, M. E. (1976). *New directions in cryptography.* IEEE Transactions on Information Theory, 22(6), 644–654. | Primaria |
| [2] | Rivest, R. L., Shamir, A., & Adleman, L. (1978). *A method for obtaining digital signatures and public-key cryptosystems.* Communications of the ACM, 21(2), 120–126. | Primaria |
| [3] | Moriarty, K. (Ed.), Kaliski, B., Jonsson, J., & Rusch, A. (2016). *RFC 8017 — PKCS #1: RSA Cryptography Specifications Version 2.2.* IETF. | Primaria (norma) |
| [4] | Josefsson, S., & Liusvaara, I. (2017). *RFC 8032 — Edwards-Curve Digital Signature Algorithm (EdDSA).* IETF. | Primaria (norma) |
| [5] | NIST (2024). *FIPS 204 — Module-Lattice-Based Digital Signature Standard (ML-DSA).* | Primaria (norma) |
| [6] | Stevens, M., Sotirov, A., Appelbaum, J., Lenstra, A., Molnar, D., Osvik, D. A., & de Weger, B. (2009). *Short chosen-prefix collisions for MD5 and the creation of a rogue CA certificate.* CRYPTO 2009. | Primaria |
| [7] | Rescorla, E. (2018). *RFC 8446 — The Transport Layer Security (TLS) Protocol Version 1.3.* IETF. | Primaria (norma) |

## Reflexión (3–5 líneas)

El asimétrico no es "el simétrico pero mejor": resuelve dos problemas puntuales
—arrancar sin secreto compartido y atribuir autoría ante un tercero— y en todo
lo demás es más lento y más frágil. Como se firma el hash y no el mensaje, la
firma nunca es más fuerte que el hash: ahí una colisión de MD5 se vuelve una CA
falsa. Y los esquemas que sobreviven no documentan cómo no errar: lo impiden.
