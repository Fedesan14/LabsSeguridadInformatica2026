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
