# Laboratorio Extra 5 — JWT inseguro

**Actividad extra** (posterior al Lab 07; cierra el hueco de web moderna)
**Modalidad:** grupos de 4 a 5 integrantes
**Entrega:** fork + Pull Request, en `entregas/labextra5/grupoXX/`
**Entorno:** sin Docker — Python puro (stdlib)

> PhantomCorp modernizó su portal: ahora usa **JWT**, "porque es lo que usan
> todos". El equipo de desarrollo está tranquilo: *"el token está firmado, no
> se puede tocar"*. Tu trabajo es demostrarles que **firmado no significa
> cifrado, y una firma con clave débil no significa nada**.

---

## Por qué este laboratorio

JWT está en todas partes: APIs, OAuth, sesiones de microservicios. Y tiene dos
malentendidos que caen en producción todo el tiempo:

1. **"Está firmado, entonces es secreto."** FALSO. El payload es base64url:
   cualquiera lo lee. La firma solo garantiza *integridad* (no lo modificaste),
   nunca *confidencialidad* (no lo leíste).
2. **"La firma lo protege."** Solo si el secreto es fuerte. Con HMAC-SHA256 y
   un secreto de diccionario, cualquiera que tenga **un solo token válido**
   puede crackear el secreto **offline**, sin tocar el servidor, y después
   **firmar lo que quiera**: `role:admin`, `sub:otro_usuario`, `exp:+10 años`.

Y el tercero, más profundo: en JWT **la identidad es un claim**. El servidor no
"sabe" quién sos: confía en lo que dice el token firmado. Quien firma, gobierna.

## Objetivos de aprendizaje

1. Explicar la estructura de un JWT (header.payload.firma) y qué garantiza y
   qué NO garantiza la firma.
2. Crackear un secreto HMAC **offline** con diccionario: el token es el oráculo.
3. Forjar tokens: escalar privilegios (`role`) y suplantar identidad (`sub`).
4. Conectar con IDOR (Lab 07): el control de acceso roto ahora vive en un claim.
5. Prescribir las defensas correctas: secretos fuertes, algoritmos asimétricos
   (RS256/EdDSA), rotación, qué nunca poner en un payload.

## El caso

El portal corre con `python3 labs/labextra5-jwt/objetivo/server.py`. Credenciales
de demo en la home (`diego / diego123`, `maria / maria456`). Endpoints:

| Endpoint | Qué hace |
|---|---|
| `/login` | devuelve un JWT firmado (HS256) |
| `/perfil` | datos del usuario del claim `sub` (requiere token) |
| `/admin` | solo `role=admin` (requiere token) |

Tu navaja: `src/jwt_tool.py`, con cuatro TODO (`decodificar`,
`firma_es_valida`, `crackear_secreto`, `forjar`) y el base64url ya resuelto.

## Parte 1 · TEORÍA — anatomía de un JWT

```
eyJhbGciOiJIUzI1NiJ9 . eyJzdWIiOiJkaWVnbyJ9 . SflKxwRJSMeKKF2QT4fwpM...
└── header ────────┘   └── payload ───────┘   └─── firma HMAC ───────┘
     base64url               base64url          HMAC-SHA256(secreto,
     (se lee!)                (se lee!)          "header.payload")
```

- **Header**: algoritmo (`HS256` = HMAC simétrico: la misma clave firma y
  verifica).
- **Payload**: los *claims* (`sub`, `role`, `exp`...). **Base64, no cifrado.**
- **Firma**: lo único entre vos y `role:admin` es HMAC con el secreto.

El ataque offline es brutal en su simplicidad: con un token válido, probás
candidatos de secreto recalculando la firma **en tu máquina**. Sin rate limit,
sin logs, sin lockout. El servidor ni se entera.

## Parte 2 · EJEMPLOS — cómo se ve en la vida real

**Ejemplo A — El secreto "secret".** Un framework de ejemplo usaba
`JWT_SECRET=secret` en su tutorial. Miles de apps lo llevaron a producción.
Cualquier token de esas apps se firma a mano.

**Ejemplo B — `alg:none`.** Versiones viejas de librerías aceptaban tokens con
`"alg":"none"` (sin firma). El atacante borraba la firma y ponía lo que
quería. Hoy las librerías serias lo rechazan por defecto — pero "pinneá el
algoritmo" sigue siendo la recomendación: nunca confíes en el `alg` que dice
el token.

**Ejemplo C — La filtración en el claim.** Un equipo metió el connection string
de la base en un claim "para tenerlo a mano". Cualquier cliente con F12 lo leía.
Base64 no es cifrado.

## Parte 3 · PRÁCTICA — cazá las 3 flags

Levantá el portal, conseguí un token con las credenciales de demo, y a operar:

| Reto | Técnica | Pista |
|---|---|---|
| **R1** | Decodificación | El token tiene un claim que no debería viajar. Ni herramientas hacen falta: los dos primeros tramos son base64url. |
| **R2** | Crack offline + forja de rol | El secreto está en `caso/diccionario.txt`. Crackealo verificando firmas localmente, después firmá un token con `role=admin` y visitá `/admin`. |
| **R3** | Forja de identidad | Con el mismo secreto: sos `diego`, pero tus datos no son interesantes. Los de `maria` sí. La identidad es un claim. |

```bash
python3 src/jwt_tool.py crackear <token> caso/diccionario.txt
python3 src/jwt_tool.py forjar <secreto> --sub diego --role admin
curl -H "Authorization: Bearer <token-forjado>" localhost:8080/admin
./ctf submit extra5 R2 'FLAG{...}'
```

## Preguntas de análisis (en `entregable.md`)

1. **P1.** El equipo de PhantomCorp decía "está firmado, no se puede tocar".
   Separá las dos propiedades (integridad vs. confidencialidad) y explicá cuál
   tenían y cuál creían tener.
2. **P2.** ¿Por qué el crack es *offline* y qué implica eso? Comparalo con un
   ataque de fuerza bruta contra el `/login` (rate limit, logs, lockout).
3. **P3.** R3 es un IDOR (Lab 07) pero sin `?id=`. Explicá por qué el control
   de acceso roto "migra" al token cuando la identidad es un claim.
4. **P4.** Probá forjar con `"alg":"none"` (firma vacía). ¿Lo acepta este
   servidor? Explicá por qué y qué debería hacer un servidor correcto con el
   claim `alg` del header.
5. **P5.** Defensor: listá las defensas en orden de prioridad para este portal
   (secreto, algoritmo, rotación, claims mínimos, expiración, revocación).
   Para cada una: ¿qué ataque de este lab bloquea?

## Qué se entrega

En `entregas/labextra5/grupoXX/`:

- `jwt_tool.py` — tu implementación completa.
- `informe.md` — a partir de `docs/entregable.md`: cadena de los 3 retos con
  comandos y salidas, las 5 preguntas, captura de `./ctf status extra5`.
- **Evidencia** según `docs/PROTOCOLO-EVIDENCIA.md`: `evidencia/comandos.txt`,
  `evidencia/salidas/`, declaración de IA.

La rúbrica está en [`docs/rubrica.md`](docs/rubrica.md).

## Uso responsable

La app corre en tu máquina. Forjar tokens contra sistemas ajenos es acceso no
autorizado (Ley 26.388) aunque el secreto sea `secret`: la debilidad del
sistema no es una invitación.
