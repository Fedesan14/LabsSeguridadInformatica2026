# Informe — Laboratorio 02 · Criptografía

> Copiala a `entregas/lab02/grupoXX/informe.md`. Borrá las notas en cursiva.

**Grupo:** XX · **Integrantes:** *(nombre — usuario GitHub)* · **Fecha:**

## 0. Declaración de uso de IA

## 1. Parte A — Análisis de la falla
**Caso:** *(el asignado)*
**A.1 — Qué prometía · A.2 — El mal uso · A.3 — Propiedad rota y explotación · A.4 — Lo correcto**

## 2. Parte B.1 — Romper el XOR
*(clave hallada, mensaje en claro, y por qué el cifrado clásico falla)*

Clave hallada: 0x37

Mensaje en claro: Memo interno PhantomCorp: la clave del wifi de invitados es Phantom-Guest-2026. No compartir fuera de la empresa.

¿Por qué falla el cifrado clásico?
El cifrado XOR utiliza una clave de solo un byte, por lo que existen únicamente 256 claves posibles. Esto permite probar todas las combinaciones mediante fuerza bruta y utilizar análisis de frecuencia para identificar cuál genera un texto con mayor probabilidad de ser lenguaje natural. Por este motivo, una clave tan corta no ofrece una protección adecuada.

## 3. Parte B.2 — Autenticación
**B.2.1 length-extension · B.2.2 cómo lo resuelve HMAC · B.2.3 tiempo constante**

## 4. Bitácora
```bash
# python3 src/cripto.py romper --hex ...
```
