# Research — Lab Extra 4 · Grupo 03

**Opción B: la herramienta profesional. Fecha de consulta: 19/11/2026.**

**Declaración de IA:** se utilizó OpenAI Codex para investigar fuentes primarias, redactar y revisar este documento. Los benchmarks citados pertenecen a sus autores; las únicas mediciones propias son las guardadas en `evidencia/salidas/mediciones.json`. No se ejecutó hashcat ni se midió una GPU en este trabajo.

## 1. Cómo cambia el ataque con una GPU

Nuestro cracker ejecuta una verificación por vez desde Python. Hashcat distribuye candidatos independientes entre muchos hilos de GPU y ejecuta kernels especializados. La CPU organiza el ataque y alimenta los dispositivos; parte de la generación y transformación de candidatos puede realizarse en la GPU para reducir transferencias. Varias GPU permiten repartir trabajo cuando hay suficientes candidatos. Las iteraciones de una misma cadena PBKDF2 dependen de las anteriores: el paralelismo aprovecha sobre todo cadenas de candidatos distintos. Véanse la [presentación oficial de hashcat](https://hashcat.net/hashcat/) y la [explicación de Chick3nman sobre su uso del hardware](https://hashcat.net/forum/thread-11041-post-56364.html).

Como referencia histórica reproducible, blazer midió una **Asus Strix RTX 4090 a frecuencias de fábrica**, con hashcat 6.2.6, CUDA 11.8 y kernels optimizados. Chick3nman publicó la [salida completa del benchmark, del 14/10/2022](https://gist.github.com/Chick3nman/32e662a5bb63bc4f51b847bb422222fd):

| Modo | Algoritmo y parámetros | Velocidad publicada |
|---|---|---:|
| 0 | MD5 sin salt | 164,1 GH/s |
| 20 | MD5(salt + contraseña), comparable con la receta de R1 | 84.654,8 MH/s |
| 3200 | bcrypt, 32 iteraciones, costo logarítmico 5 | 184,0 kH/s |

La razón MD5 sin salt / bcrypt es `164,1 × 10⁹ / (184 × 10³) ≈ 891.848`: casi seis órdenes de magnitud. El costo 5 de ese benchmark es bajo y debe indicarse; no describe bcrypt con costo 12. Aumentar el costo de bcrypt en uno duplica aproximadamente el trabajo. Los resultados dependen del kernel, los parámetros y el tamaño del ataque; tampoco miden la latencia de procesar solo 49 palabras.

La comparación elegida es MD5 frente a bcrypt. Argon2id agrega un costo de memoria configurable, de modo que su evaluación también exige informar memoria, pasadas y paralelismo; no corresponde asignarle la velocidad de bcrypt. Para defensa, [OWASP distingue los parámetros de cada familia](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

## 2. Mask, combinator y reglas

| Ataque | Cómo construye candidatos | Ejemplo |
|---|---|---|
| Mask (`-a 3`) | Define el conjunto de caracteres permitido en cada posición. | `?u?l?l?l?d?d` recorre una mayúscula, tres minúsculas y dos dígitos. |
| Combinator (`-a 1`) | Concatena cada entrada del primer diccionario con cada entrada del segundo. | `mate` + `cocido` → `matecocido`; con tamaños N y M produce hasta N × M combinaciones. |
| Reglas (`-r`) | Transforma las palabras existentes mediante operaciones como capitalizar o agregar caracteres. | `phantom` → `phantom2026`. |

Nuestro `aplicar_reglas()` implementa un conjunto fijo de transformaciones: no recorre todos los caracteres por posición ni combina dos diccionarios arbitrarios. Una máscara puede acertar una contraseña ausente del diccionario si conoce su patrón; también puede omitirla si el patrón es incorrecto. Fuentes: documentación oficial de [mask](https://hashcat.net/wiki/doku.php?id=mask_attack), [combinator](https://hashcat.net/wiki/doku.php?id=combinator_attack) y [reglas](https://hashcat.net/wiki/doku.php?id=rule_based_attack).

## 3. Qué es una rainbow table y qué cambia el salt

Una rainbow table intercambia almacenamiento y trabajo previo por búsquedas posteriores más rápidas. Construye cadenas que alternan hashes y funciones de reducción; almacena extremos y reconstruye tramos al buscar un hash. Las reducciones convierten resúmenes en candidatos, sin invertir criptográficamente la función. La propuesta original es de [Philippe Oechslin, CRYPTO 2003](https://link.springer.com/chapter/10.1007/978-3-540-45146-4_36).

Una tabla preparada para `H(password)` no sirve directamente para `H(salt || password)`. Cada salt distinto define otra función y exige otra precomputación. Un salt aleatorio y suficientemente grande impide amortizar una tabla universal entre usuarios. No vuelve imposible construir una tabla para un salt concreto, ni evita probar un diccionario con el salt publicado. Por eso las cuentas débiles del laboratorio caen aunque tengan salts diferentes.

## 4. Cierre obligatorio: contraseñas filtradas sin enviar el secreto

En Pwned Passwords se calcula localmente SHA-1 de la contraseña codificada en UTF-8 y se envían por HTTPS solo los primeros cinco caracteres hexadecimales. La respuesta devuelve sufijos y cantidades; el cliente compara localmente el sufijo restante. `Add-Padding: true` añade registros de cantidad cero para disimular el tamaño de respuesta. Se consulta al terminar la entrada, evitando revelar prefijos sucesivos. El prefijo revela información parcial; no garantiza anonimato absoluto. SHA-1 identifica entradas del catálogo y no reemplaza el almacenamiento seguro de contraseñas. Fuente: [API oficial de HIBP](https://haveibeenpwned.com/api/v3#SearchingPwnedPasswordsByRange).

Rechazar una contraseña conocida como comprometida evita reutilizar un secreto ya disponible para los atacantes. Exigir clases de caracteres puede producir variantes predecibles. La lista se complementa con longitud suficiente y claves únicas; no demuestra que una contraseña ausente sea fuerte. Es coherente con [NIST SP 800-63B-4, sección 3.1.1.2](https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver).
