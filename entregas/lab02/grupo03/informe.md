# Informe — Laboratorio 02 · Criptografía

**Grupo:** 03 · **Fecha:** `TODO-FECHA-DE-ENTREGA`

### Integrantes

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| Federico Sánchez | `TODO-LEGAJO` | @Fedesan14 |
| Elian Enria | `TODO-LEGAJO` | `TODO-USUARIO` |
| Efraín Host | `TODO-LEGAJO` | @hostefrain |
| Lohana Rumis | `TODO-LEGAJO` | `TODO-USUARIO` |

### Distribución del trabajo

Reparto por componente de la rúbrica. Cada integrante es responsable de su
componente de punta a punta —código, redacción y defensa oral— y commitea su
parte desde su propia cuenta.

| Integrante | Componente | Pts. | Qué produce |
|---|---|---:|---|
| Federico Sánchez | Parte A — análisis de la falla | 30 | Sección 1 completa de este informe (A.1 a A.5), incluida la verificación de las ocho fuentes |
| Efraín Host | Parte B.1 — romper el XOR | 25 | `src/cripto.py`: `romper_xor_1byte()` y el conjunto `_FRECUENTES`. Sección 2 de este informe |
| Elian Enria | Parte B.2 — MAC ingenuo vs HMAC | 30 | `src/cripto.py`: `mac_ingenuo()`, `mac_hmac()` y `verificar_mac()`. Sección 3 de este informe (B.2.1 a B.2.3) |
| Lohana Rumis | Mini-research y verificación | 10 | [`research.md`](research.md) completo (tema D). `test_cripto.py`. Secciones 0 y 4 de este informe |

Los 5 puntos restantes de la rúbrica son de **proceso Git** y son colectivos.
Federico Sánchez, como responsable del fork, se encarga de sincronizar `main`
con `upstream` y de abrir el Pull Request.

**Caso asignado (Parte A):** MD5 / colisiones — uso de una función de hash rota
para certificados. Asignación por la regla del enunciado: `3 mod 5 = 3`.

**Mini-research:** tema **D** — cifrado asimétrico y firmas digitales
([`research.md`](research.md)).

---

## 0. Declaración de uso de IA

**¿El grupo usó asistentes de IA en este trabajo?** **Sí.**

| Herramienta | Para qué se usó | Qué partes del entregable afectó | Cómo se verificó que lo devuelto era correcto |
|---|---|---|---|
| Claude Code (Anthropic, modelo Opus 5) | Redacción y estructuración del análisis; implementación de los cuatro `TODO`; escritura del archivo de pruebas | `src/cripto.py` (las cuatro funciones), `test_cripto.py`, redacción de todas las secciones de este informe y de `research.md` | (a) `test_cripto.py` contrasta el HMAC contra el **vector 1 de la RFC 4231** y el SHA-256 contra **FIPS 180-4**, valores publicados y ajenos a esta implementación; (b) la salida de `mac` se cotejó contra `openssl dgst`, una implementación independiente (ver Bitácora, comando 5); (c) `romper` se validó contra el texto claro que produce `data/generar_datos.py`; (d) cada afirmación de la Parte A se verificó contra la fuente primaria citada, no contra el resumen del asistente |

**Cómo se repartió la revisión.** El asistente produjo un primer borrador
integral. Sobre ese borrador, cada integrante revisó, corrigió y asumió como
propio el componente que le corresponde según la tabla de *Distribución del
trabajo*, y lo commiteó desde su propia cuenta. La verificación de las fuentes
de la Parte A y la lectura del código de la Parte B se hicieron contra las
fuentes primarias y contra la ejecución real, no contra la explicación del
asistente.

**Declaración.** El grupo declara que comprende el contenido íntegro de lo
entregado y que puede explicar y defender oralmente cualquier parte del código y
del análisis, independientemente de la asistencia recibida.

---

## 1. Parte A — Análisis de la falla

**Caso:** MD5 / colisiones — uso de una función de hash rota para firmar
certificados. Se analiza el caso testigo: la **CA intermedia falsa** construida
contra RapidSSL, presentada en el 25C3 en diciembre de 2008 y publicada como
paper en CRYPTO 2009 [1]. Se usa como segundo episodio el malware **Flame**
(2012) [5], porque muestra el mismo error repetido cuatro años después.

### A.1 — Qué prometía el sistema

Un certificado X.509 firmado con `md5WithRSAEncryption` promete **autenticidad
de origen** e **integridad**: que una Autoridad de Certificación presente en el
almacén de confianza del navegador dio fe del vínculo entre una identidad (un
nombre de dominio) y una clave pública, y que ese vínculo —incluidas las
extensiones, entre ellas `basicConstraints: CA:TRUE/FALSE`, que decide si el
certificado puede firmar otros— no fue alterado después de la firma.

El punto crítico es **cómo** se cumple esa promesa: la CA no firma el documento,
firma su **digest**. El verificador hace
`RSA-verify(firma, clave_pública_CA) == MD5(tbsCertificate)`. Toda la
autenticidad de la cadena de confianza de TLS quedaba, por lo tanto, reducida a
una sola propiedad: la **resistencia a colisiones** de MD5. Si existen dos
`tbsCertificate` distintos con el mismo MD5, la firma de uno es una firma válida
del otro, y el verificador no tiene forma de notarlo.

### A.2 — El mal uso concreto

No es que MD5 fuera "un algoritmo malo" desde el principio, ni que se rompiera
de un día para el otro. Fueron **tres decisiones de uso**, encadenadas.

**1. Seguir firmando con MD5 después de doce años de advertencias.** Dobbertin
colisionó la función de compresión de MD5 en 1996; Wang, Feng, Lai y Yu
publicaron **colisiones completas y prácticas** en 2004–2005, computables en
horas [2]; Lenstra, Wang y de Weger mostraron en 2005 dos certificados X.509
colisionantes; Stevens, Lenstra y de Weger extendieron el ataque a **colisiones
de prefijo elegido** en 2007. RapidSSL seguía emitiendo con MD5 en 2008. La
norma que lo prohíbe explícitamente, la RFC 6151 [3], llegó recién en 2011:
**tres años después** del ataque. El mal uso fue de gestión del ciclo de vida
criptográfico, no de matemática.

**2. Firmar sobre datos predecibles.** Éste es el mal uso decisivo, y el que
suele pasarse por alto. Una colisión de prefijo elegido sólo sirve si el
atacante puede **saber de antemano el mensaje exacto que la CA va a firmar**. El
proceso de emisión de RapidSSL se lo regalaba: los números de serie eran
**secuenciales** y el campo `notBefore` se fijaba **exactamente seis segundos
después** de recibido el pedido [1]. Con eso, los autores pudieron calcular el
`tbsCertificate` futuro, construir la colisión con antelación y pedir el
certificado en el momento justo. Un número de serie aleatorio habría dejado el
ataque sin base **aun usando MD5**.

**3. Confiar campos de autorización a un digest colisionable.** El bit
`CA:TRUE`, que convierte un certificado de hoja en una autoridad capaz de emitir
certificados para cualquier dominio del mundo, viajaba dentro del mismo bloque
cubierto por un resumen de 128 bits del que ya se sabía cómo generar colisiones.

**Y el patrón se repitió.** En 2012 el malware Flame firmó código como si fuera
Microsoft, porque el servicio interno **Terminal Server Licensing** todavía
emitía certificados firmados con MD5; el ataque usó una variante de colisión de
prefijo elegido más avanzada que la pública [5][6]. Cuatro años después del
25C3, el mismo mal uso, en la infraestructura de un fabricante que ya conocía
todo esto.

### A.3 — Propiedad rota y cómo se explotó

**Propiedad rota: autenticidad.** Y con ella la **integridad** del certificado,
porque en una firma digital las dos vienen del mismo mecanismo: si podés
sustituir el documento sin invalidar la firma, rompiste ambas a la vez.

- **Confidencialidad:** *no* la rompió la colisión. Se pierde **después**, como
  consecuencia: con la CA falsa el atacante emite certificados válidos para
  cualquier dominio y hace *man-in-the-middle* de TLS sin que el navegador
  avise. El orden importa, y confundirlo es el error típico.
- **Disponibilidad:** no se vio afectada.

**Lo que no se rompió, y por qué importa.** La **resistencia a preimagen** de
MD5 sigue en pie: dado un hash, nadie sabe hallar un mensaje que lo produzca.
Por eso **HMAC-MD5 no quedó roto** por este ataque — su demostración de
seguridad no depende de la resistencia a colisiones, sino de que la función de
compresión sea una PRF [8]. La RFC 6151 [3] es explícita: prohíbe MD5 para
firmas y sólo desaconseja HMAC-MD5 para diseños nuevos. **Ésta es la prueba de
que el problema era el uso y no el algoritmo:** la misma primitiva debilitada es
fatal firmando certificados y sigue siendo aceptable autenticando mensajes,
porque cada uso apoya su seguridad en una propiedad distinta.

**Mecánica de la explotación** (colisión de prefijo elegido, [1]):

| # | Paso |
|---|---|
| 1 | Se eligen dos prefijos: `P1`, el `tbsCertificate` legítimo que RapidSSL va a firmar para un dominio que los atacantes controlan, y `P2`, el de una **CA intermedia falsa** con `CA:TRUE`. |
| 2 | Se calculan bloques de colisión `C1`, `C2` tales que `MD5(P1‖C1) = MD5(P2‖C2)`. Costo real: un clúster de **~200 PlayStation 3** (procesador Cell), del orden de uno a dos días. |
| 3 | Los bloques de colisión se esconden en campos tolerantes a basura: dentro del **módulo RSA** de la clave pública del certificado legítimo, y en una extensión `netscape-comment` del falso. Ningún verificador los mira. |
| 4 | Se pide el certificado legítimo **en el segundo exacto** previsto, para que el serial y el `notBefore` coincidan con lo asumido en el paso 1. La CA firma `MD5(P1‖C1)` con su clave privada. |
| 5 | Se **copia la firma, bit por bit**, al certificado falso. Verifica: el hash coincide, y el verificador sólo compara el hash. |
| 6 | Resultado: una CA intermedia con la firma de una raíz presente en el almacén de confianza de todos los navegadores de la época. Poder de emitir certificados válidos para cualquier dominio. |

El paso 4 es la bisagra, y es la que conecta con A.2: los autores **fallaron
tres veces** antes de acertar el fin de semana correcto. Si el serial hubiera
tenido entropía, no habría habido paso 4 posible.

### A.4 — La forma correcta de haberlo hecho

**En dos oraciones.** Firmar con una función cuya resistencia a colisiones esté
vigente —SHA-256, nunca MD5 ni SHA-1— y con **agilidad criptográfica**: poder
rotar el algoritmo de firma años antes de que se rompa, tratando la fecha de las
primeras colisiones académicas como el inicio de la migración y no como una
curiosidad. Y, en la misma jerarquía de importancia, inyectar al menos **64 bits
de un CSPRNG** en el número de serie del certificado —hoy exigido por los
*Baseline Requirements* del CA/Browser Forum [4]— porque eso le quita al
atacante la capacidad de predecir el mensaje a firmar y **neutraliza el ataque
de prefijo elegido incluso mientras la primitiva se debilita**.

La lección de ingeniería: un control de proceso barato (unos bytes de azar en un
campo que a nadie le importaba) compra el margen de tiempo que la primitiva ya
no da. La criptografía no falla sola: falla dentro de un proceso.

### A.5 — Fuentes

| # | Fuente | Tipo |
|---|---|---|
| [1] | Stevens, M., Sotirov, A., Appelbaum, J., Lenstra, A., Molnar, D., Osvik, D. A., & de Weger, B. (2009). *Short chosen-prefix collisions for MD5 and the creation of a rogue CA certificate.* CRYPTO 2009, LNCS 5677, 55–69. | Primaria (autores del ataque) |
| [2] | Wang, X., & Yu, H. (2005). *How to break MD5 and other hash functions.* EUROCRYPT 2005, LNCS 3494, 19–35. | Primaria (paper original de las colisiones) |
| [3] | Turner, S., & Chen, L. (2011). *RFC 6151 — Updated security considerations for the MD5 message-digest and the HMAC-MD5 algorithms.* IETF. | Primaria (norma) |
| [4] | CA/Browser Forum. *Baseline Requirements for the Issuance and Management of Publicly-Trusted Certificates* — requisito de entropía en el número de serie. | Primaria (norma de la industria) |
| [5] | Microsoft (2012). *Security Advisory 2718704: Unauthorized digital certificates could allow spoofing.* | Primaria (aviso del fabricante) |
| [6] | Stevens, M. (2013). *Counter-cryptanalysis.* CRYPTO 2013 — análisis de la variante de colisión usada por Flame. | Primaria |
| [7] | CVE-2004-2761 — *MD5 is not collision resistant, which makes it easier to conduct spoofing attacks.* | Secundaria (registro de vulnerabilidad) |
| [8] | Bellare, M., Canetti, R., & Krawczyk, H. (1996). *Keying hash functions for message authentication.* CRYPTO 1996 — demostración de seguridad de HMAC. | Primaria |

---

## 2. Parte B.1 — Romper el XOR

**Clave hallada:** `0x37` (55 decimal; el carácter `7` en ASCII).

**Mensaje en claro recuperado:**

> Memo interno PhantomCorp: la clave del wifi de invitados es
> Phantom-Guest-2026. No compartir fuera de la empresa.

**Cifrado de entrada** (`data/muestra/reto_xor.hex`, regenerable con
`python3 data/generar_datos.py`):

```
7a525a58175e59435245595817675f565943585a745845470d175b5617545b5641521753525b17
405e515e175352175e59415e435653584417524417675f565943585a1a70425244431a05070501
191779581754585a475645435e45175142524556175352175b5617525a474552445619
```

**Cómo se rompió.** `romper_xor_1byte()` prueba las 256 claves posibles de un
byte y puntúa cada texto candidato por cuántos de sus bytes caen en el conjunto
`" eaosrnidlctump"` (el espacio más las catorce letras más frecuentes del
español, en ambas cajas). Ese conjunto cubre alrededor del 85 % de un texto
natural en español, así que el candidato correcto puntúa muy por encima de los
otros 255 y un simple `max()` alcanza. No hizo falta ninguna heurística más
fina.

### Por qué falla el cifrado clásico

**1. El espacio de claves es enumerable.** Ocho bits son 256 posibilidades: el
ataque completo corre en microsegundos en una notebook. AES-128 tiene 2^128, y
la diferencia no es de grado sino de naturaleza: ese espacio **no se puede
recorrer**. Ninguna cantidad de ingenio en el algoritmo compensa una clave
chica.

**2. No hay difusión ni confusión** (los dos criterios de Shannon). Cada byte
del texto claro depende de **exactamente un** byte de clave y de ninguno de sus
vecinos. No existe efecto avalancha: cambiar un byte del cifrado cambia un byte
del claro y nada más. Eso permite atacar el cifrado **posición por posición**,
en lugar de obligar a atacarlo como un todo.

**3. Preserva la estadística del texto plano.** El XOR con una clave fija no es
más que un **reetiquetado** de bytes: la distribución de frecuencias del español
sobrevive intacta, sólo con las etiquetas permutadas. El atacante no necesita la
clave, ni que el algoritmo sea secreto: necesita saber en qué idioma está
escrito el mensaje. Toda la información para romperlo está **en el propio
criptograma**.

**4. Es exactamente el escenario de Kerckhoffs.** El principio pide que el
sistema siga siendo seguro con todo público excepto la clave. Acá el algoritmo
era público —lo teníamos delante, en `xor_cifrar()`— y eso fue suficiente,
porque la clave no aportaba secreto real. Un sistema cuya seguridad venía de que
nadie mirara el código no tenía seguridad.

**5. Alargar la clave no arregla el problema: lo encarece linealmente.** Con una
clave de *N* bytes (el Vigenère binario) se estima *N* con el índice de
coincidencia o el test de Kasiski, se parte el criptograma en *N* columnas según
`posición mod N`, y **se aplica este mismo ataque de un byte a cada columna**. El
costo crece con *N*, no con 256^N. La única variante segura de esta familia es el
*one-time pad*: clave tan larga como el mensaje, aleatoria y jamás reutilizada —
y ahí el problema pasa a ser distribuir esa clave, que es justamente el problema
que resuelve el cifrado asimétrico (ver [`research.md`](research.md)).

**6. El impacto concreto.** El mensaje era una credencial de WiFi. Una
confidencialidad mal implementada no "protege un poco": no protege nada. Acá el
resultado fue una credencial reutilizable, expuesta a cualquiera que capturara
el criptograma.

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

Salida real de la terminal. Todos los comandos se corren desde
`entregas/lab02/grupo03/`.

```bash
# 0. Generar el reto de la Parte B
$ python3 data/generar_datos.py
Creado data/muestra/reto_xor.hex — rompelo con: python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)

# 1. El esqueleto corre (referencia del enunciado)
$ python3 src/cripto.py xor --texto hola --clave K
2324272a

# 2. B.1 — romper el XOR de 1 byte
$ python3 src/cripto.py romper --hex $(cat data/muestra/reto_xor.hex)
clave=0x37
Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.

# 3. B.2 — MAC ingenuo: sha256(clave || msg)
$ python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo ingenuo
a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725

# 4. B.2 — HMAC-SHA256, la forma correcta
$ python3 src/cripto.py mac --clave secreta --msg "pago 100" --modo hmac
5ec4a52407221836a66e8d654d914aaa4b18bd31cf31907348bcd292677b902e

# 5. Cotejo contra una implementacion INDEPENDIENTE (openssl), para descartar
#    que el resultado sea correcto solo respecto de si mismo
$ printf 'pago 100' | openssl dgst -sha256 -hmac secreta
SHA2-256(stdin)= 5ec4a52407221836a66e8d654d914aaa4b18bd31cf31907348bcd292677b902e

$ printf 'secretapago 100' | openssl dgst -sha256
SHA2-256(stdin)= a8cc54c07b3acb7470c25ab9eea5234bfa2562e37298eee275e39a457004b725

# 6. Suite de verificacion propia (vectores publicados: RFC 4231 y FIPS 180-4)
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
