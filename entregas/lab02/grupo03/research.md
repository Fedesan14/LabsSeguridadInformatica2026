# Mini-research — Laboratorio 02

**Grupo:** 03

**Tema elegido:** **C.** Derivación de claves desde contraseñas (PBKDF2, bcrypt, Argon2): por qué un sha256(password) no alcanza

- [ ] **A.** Modos de operación de cifrado por bloques (ECB vs CBC vs GCM) y por
  qué ECB filtra estructura (el "pingüino" de Adobe).
- [ ] **B.** HMAC y el ataque de length-extension: cómo funciona el ataque y por
  qué HMAC lo previene.
- [x] **C.** Derivación de claves desde contraseñas (PBKDF2, bcrypt, scrypt,
  Argon2): por qué un `sha256(password)` no alcanza.
-  [ ] **D.** Cifrado asimétrico y firmas digitales: qué problema resuelven que el
  simétrico no.

## Desarrollo

### Por qué un hash "normal" no sirve para guardar contraseñas

sha256(password) parece razonable a primera vista: no guardás la contraseña en texto plano, guardás su hash. El problema es que SHA-256 fue diseñado para ser rápido, eso es justamente lo que se necesita para verificar integridad de archivos o firmas digitales, pero es exáctamente lo contrario de lo que se necesita para proteger contraseñas.
Las contraseñas tienen poca entropía real (la gente reutiliza patrones, palabras de diccionario, variantes predecibles). Si el hash es rápido, un atacante que obtiene la base de datos puede probar miles de millones de contraseñas candidatas por segundo contra ese hash, usando GPUs o hardware dedicado, hasta encontrar una que coincida. Esto es un ataque de fuerza bruta offline, y es viable precisamente porque hashear es barato computacionalmente.

### La solución: funciones de derivación de claves (KDF)

Una KDF (Key Derivation Function) para contraseñas está diseñada para ser deliberadamente lenta y/o costosa en memoria, de forma controlable mediante un parámetro de costo. La idea es que verificar una contraseña legítima ("probar una sola vez") sea tolerable para el usuario real, pero probar miles de millones de candidatas sea prohibitivamente caro para un atacante.
Las funciones más usadas:
- **PBKDF2**: aplica una función pseudoaleatoria (normalmente HMAC-SHA256) repetidamente, miles de veces, sobre la contraseña y un salt. Es la más antigua y la más simple de las cuatro, pero solo endurece el costo en CPU, no en memoria.
- **bcrypt**: basado en el cifrado Blowfish, con un factor de costo configurable. Más resistente que PBKDF2 frente a hardware especializado, pero tampoco es memory-hard.
- **scrypt**: diseñada explícitamente para ser memory-hard, además de tiempo de CPU, exige una cantidad configurable de memoria RAM por intento, lo que encarece mucho el uso de GPUs/ASICs en pararelo.
- **Argon2 (específicamente Argon2id)**: ganador de la Password Hashing Competition (2015)
y la recomendación actual por defecto, combina resistencia a ataques de memoria y de canal lateral, con parámetros independientes de tiempo, memoria y pararelismo.

### El rol del salt

Todas estas funciones tequieren un salt único por contraseña (no secreto, pero sí aleatorio y distinto para cada usuario). Sin salt, dos usuarios con la misma contraseña tendrían el mismo hash, y un atacante podría precalcular tablas de hashes conocidos (rainbow tables) para acelerar el ataque contra toda la base de datos a la vez. Con salt, cada hash hay que atacarlo de forma independiente.

### Qué tiene que ver esto con la Parte A del lab

Esto conecta directo con la falla de MD5 para certificados que se analiza en la parte A: en ambos casos, el error es usar una función con propiedades equivocadas para el problema. MD5 tenía, entre otras cosas, la velocidad necesaria para firmar certificados masivamente, pero perdió resistencia a colisiones; sha256(password) tiene resistencia a coliciones perfectamente intacta, pero es rápido, y rápido es precisamente lo que no se quiere cuando el input que estás protegiendo tiene poca entropía, como una contraseña.

## Fuentes

| # | Fuente | Tipo |
|---|---|---|

| [1] | OWASP Foundation. (2023). *Password Storage Cheat Sheet.* OWASP Cheat Sheet Series. https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html | Secundaria (guía de referencia de la industria) |
| [2] | Grassi, P. A., Fenton, J. L., Newton, E. M., Perlner, R. A., Regenscheid, A. R., Burr, W. E., Richer, J. P., Lefkovitz, N. B., Danker, J. M., Choong, Y.-Y., Greene, K. K., & Theofanos, M. F. (2017). *NIST SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management.* NIST. https://doi.org/10.6028/NIST.SP.800-63b | Primaria (norma) — *superseded por SP 800-63-4 (2025)* |
| [3] | Biryukov, A., Dinu, D., Khovratovich, D., & Josefsson, S. (2021). *RFC 9106 — Argon2 Memory-Hard Function for Password Hashing and Proof-of-Work Applications.* IETF. https://www.rfc-editor.org/rfc/rfc9106 | Primaria (norma) |

## Reflexión

Antes de este research pensábamos en "hashear vs. no hashear" como la línea divisoria de seguridad, y nos quedó claro que esa línea en realidad pasa por otro lado: qué tan caro es el hash, no si existe o no. Lo que más nos sorprendió es que la propiedad que hace bueno a SHA-256 para integridad (que sea rápido) es exáctamente la que lo inhabilita para contraseñas, no es que falte una propiedad, es que sobra la contraria. Reflexionamos en cuántos sistemas reales todavía mezclan estos dos usos sin darse cuenta.