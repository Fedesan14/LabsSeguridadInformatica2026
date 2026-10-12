# Research — Lab Extra 4: Cracking de contraseñas

> Copiá a `entregas/labextra4/grupoXX/research.md`. Extensión: 1 a 2 carillas.
> Citá las fuentes. Declaración de IA obligatoria.

## Opción A — Un volcado real

Elegí una filtración real de hashes documentada (RockYou 2009, LinkedIn 2012,
Have I Been Pwned tiene el catálogo) y contala en formato lección:

1. ¿Qué algoritmo usaba el sitio? ¿Con salt?
2. ¿Qué porcentaje de las contraseñas terminó crackeado y en cuánto tiempo?
3. ¿Qué habría cambiado con el algoritmo correcto?

## Opción B — La herramienta profesional

Tu cracker es un juguete al lado de hashcat. Investigá:

1. ¿Cómo paraleliza hashcat en GPU y qué velocidades alcanza por algoritmo
   (compará MD5 vs bcrypt/argon2 en benchmarks públicos)?
2. ¿Qué son los ataques de *mask* y *combinator* y en qué se diferencian de tu
   `aplicar_reglas()`?
3. ¿Qué es una *rainbow table* y por qué el salt la mata?

## Pregunta de cierre (obligatoria en ambas opciones)

NIST SP 800-63B recomienda verificar contraseñas nuevas contra listas de
contraseñas filtradas conocidas ("have I been pwned" lo implementa con
k-anonymity). Explicá cómo funciona ese chequeo sin enviar la contraseña al
servicio, y por qué es mejor política que "mayúscula + número + símbolo".
