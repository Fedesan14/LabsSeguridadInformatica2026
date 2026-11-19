# Research — Lab Extra 5: JWT inseguro

> Copiá a `entregas/labextra5/grupoXX/research.md`. Extensión: 1 a 2 carillas.
> Citá las fuentes. Declaración de IA obligatoria.

## Opción A — El catálogo de ataques a JWT

Investigá los ataques clásicos contra JWT más allá de este lab:

1. `alg:none` y confusión de algoritmo (RS256→HS256: firmar con la clave
   PÚBLICA como si fuera el secreto HMAC).
2. Inyección por `kid` (key id) y `jku`/`x5u` (URL de la clave).
3. Para cada uno: condición que lo habilita y defensa.

## Opción B — JWT bien hecho

Leé las buenas prácticas actuales (RFC 8725 "JWT Best Current Practices", o
la cheat sheet de OWASP) y respondé:

1. ¿Qué claims de validación exige (exp, iss, aud, nbf) y qué atajo ataca
   cada uno si falta?
2. ¿Cuándo conviene RS256/EdDSA sobre HS256 en una arquitectura de
   microservicios? (¿Quién tiene la clave de verificación en cada caso?)
3. ¿Por qué "guardá el JWT en localStorage" es discutido? (XSS vs CSRF)

## Pregunta de cierre (obligatoria en ambas opciones)

En este lab el secreto era `mate123`. Suponé que PhantomCorp rota a un secreto
de 32 bytes aleatorios pero **sigue metiendo datos sensibles en el payload**.
¿El problema quedó resuelto? Argumentá con la diferencia entre los retos R1 y
R2 de este lab.
