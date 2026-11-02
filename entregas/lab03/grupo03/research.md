# Mini-research — Laboratorio 03

**Grupo:** 03

**Tema elegido:** **A.** PBKDF2 vs bcrypt vs scrypt vs Argon2: por qué existen
"hashes lentos".

- [x] **A.** PBKDF2 vs bcrypt vs scrypt vs Argon2: por qué existen "hashes lentos".
- [ ] **B.** TOTP vs FIDO2/WebAuthn: por qué las passkeys superan al TOTP.
- [ ] **C.** Autenticación vs autorización; modelos RBAC y ABAC.
- [ ] **D.** Ataques de timing reales y cómo se mitigan.

---

## Desarrollo

### El problema de origen: un hash rápido es un hash malo para contraseñas

Una función de hash criptográfica "normal" (SHA-256, SHA-3) está diseñada
para ser lo más **rápida** posible, porque sus usos típicos, verificar
integridad de un archivo, calcular una firma digital, un HMAC, se benefician
de eso. Si se usa esa misma velocidad para almacenar contraseñas
(`SHA256(password)`), el resultado es contraproducente: un atacante que
obtiene la base de datos filtrada puede probar miles de millones de
candidatas por segundo contra ese hash usando GPUs, porque las contraseñas
reales tienen poca entropía (patrones, palabras de diccionario, variantes
predecibles) y el hash no opone ninguna resistencia computacional al
intento repetido.

Las funciones de derivación de claves para contraseñas (KDF, por sus
siglas en inglés) resuelven esto al revés: están **deliberadamente
diseñadas para ser lentas**, con un parámetro de costo ajustable. Verificar
una contraseña legítima una sola vez sigue siendo tolerable para el
usuario; probar miles de millones de candidatas se vuelve, en cambio,
prohibitivamente caro para el atacante. Esa es la razón de ser de los
"hashes lentos": no es una característica accidental, es el objetivo de
diseño.

### Las cuatro funciones, en orden cronológico

**bcrypt** (1999), presentado por Niels Provos y David Mazières en el
paper *"A Future-Adaptable Password Scheme"* (USENIX Annual Technical
Conference, Freenix Track), se basa en una variante del cifrado Blowfish
(Eksblowfish) adaptada para ser costosa de calcular. Su aporte principal
frente a un hash simple fue introducir un **factor de costo ("work
factor")** ajustable, pensado explícitamente para que la función pudiera
"escalar" con el tiempo a medida que el hardware se vuelve más rápido, sin
cambiar de algoritmo. bcrypt no es *memory-hard*: endurece el cálculo pero
no exige memoria RAM significativa, lo que deja margen a la paralelización
en hardware dedicado.

**PBKDF2** (2000, formalizado en RFC 2898 y luego en RFC 8018) es la base
de referencia del grupo. Su mecanismo es simple: aplica repetidamente una
función pseudoaleatoria (normalmente HMAC-SHA256) sobre la contraseña y un
*salt*, miles de veces. El único parámetro de costo es el número de
iteraciones. Es ampliamente compatible y está certificada para entornos
que requieren FIPS 140, pero tiene una debilidad estructural: solo
endurece el costo en **tiempo de CPU**, no en memoria. Esto la hace
relativamente vulnerable frente a hardware especializado (GPUs, ASICs,
FPGAs), que puede paralelizar el cálculo de HMAC con mucha eficiencia.

**scrypt** (2009), diseñado por Colin Percival y presentado en el paper
*"Stronger Key Derivation via Sequential Memory-Hard Functions"*
(BSDCan 2009), fue la primera de las tres en resolver directamente el
problema de la paralelización: es **memory-hard** por diseño. Además de
tiempo de CPU, exige una cantidad configurable de memoria RAM por cada
intento de cálculo. Como la memoria es un recurso caro de replicar en
paralelo (a diferencia de los núcleos de cómputo), esto encarece mucho
construir hardware especializado (GPU/ASIC) para atacar scrypt a gran
escala.

**Argon2** (2015) ganó la *Password Hashing Competition*, un concurso
abierto organizado por la comunidad criptográfica para elegir un sucesor
estándar, y quedó formalizado en la **RFC 9106** del IETF. Su variante
recomendada, **Argon2id**, combina resistencia a ataques de memoria con
resistencia a ataques de canal lateral, y expone **tres parámetros
independientes**: tiempo, memoria y paralelismo. Es la recomendación por
defecto actual cuando está disponible, según la guía de referencia de
OWASP.

### Resumen comparativo

| Función  | Año  | Memory-hard | Parámetros de costo               | Estado actual                       |
|----------|------|-------------|------------------------------------|--------------------------------------|
| PBKDF2   | 2000 | No          | Iteraciones                        | Aceptable si se requiere FIPS 140   |
| bcrypt   | 1999 | No          | Factor de costo                    | Aceptable para sistemas legacy      |
| scrypt   | 2009 | Sí          | CPU/memoria, bloque, paralelismo   | Alternativa si no hay Argon2id      |
| Argon2id | 2015 | Sí          | Tiempo, memoria, paralelismo       | Recomendación por defecto           |

### Por qué ninguna reemplaza al salt

Las cuatro funciones, sin excepción, **requieren un salt único por
contraseña** (no secreto, pero sí aleatorio y distinto por usuario). El
salt no vuelve el hash más lento; evita que un atacante precalcule una
tabla de hashes conocidos (*rainbow table*) y la reutilice contra toda la
base de datos a la vez, ya que sin salt dos usuarios con la misma
contraseña tendrían exactamente el mismo hash. El costo computacional
(PBKDF2/bcrypt/scrypt/Argon2) y el salt resuelven problemas distintos y
complementarios: uno encarece cada intento individual, el otro impide
atacar todos los usuarios con el mismo trabajo precalculado.

---

## Fuentes (mín. 3)

1. **Provos, N., & Mazières, D. (1999).** *A Future-Adaptable Password
   Scheme.* USENIX Annual Technical Conference. Paper original que
   presenta bcrypt y el concepto de factor de costo ajustable.
   [https://www.usenix.org/conference/1999-usenix-annual-technical-conference/presentation/future-adaptable-password-scheme](https://www.usenix.org/conference/1999-usenix-annual-technical-conference/presentation/future-adaptable-password-scheme)
2. **Percival, C. (2009).** *Stronger Key Derivation via Sequential
   Memory-Hard Functions.* BSDCan. Paper original de scrypt, que
   introduce formalmente el concepto de función *memory-hard* aplicada
   a derivación de claves.
   [https://passwordresearch.com/papers/paper207.html](https://passwordresearch.com/papers/paper207.html)
3. **Biryukov, A., Dinu, D., Khovratovich, D., & Josefsson, S. (2021).**
   *RFC 9106 — Argon2 Memory-Hard Function for Password Hashing and
   Proof-of-Work Applications.* IETF.
   [https://www.rfc-editor.org/rfc/rfc9106](https://www.rfc-editor.org/rfc/rfc9106)
4. **OWASP Foundation.** *Password Storage Cheat Sheet.* OWASP Cheat
   Sheet Series. Guía de referencia de la industria que resume el
   estado actual de recomendaciones entre las cuatro funciones.
   [https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## Reflexión

Lo que más me llamó la atención investigando esto es que no hay una sola
función "ganadora" en términos absolutos, hay una evolución donde cada una
resolvió el límite de la anterior: PBKDF2 y bcrypt endurecieron el tiempo de
cómputo, pero dejaron la puerta abierta a la paralelización en hardware;
scrypt y Argon2 cerraron esa puerta exigiendo memoria, que es mucho más cara
de paralelizar. Me quedó claro además que el salt y el "costo" no son la
misma defensa: uno evita el ataque masivo precalculado, el otro encarece
cada intento individual, y hace falta tener los dos.
