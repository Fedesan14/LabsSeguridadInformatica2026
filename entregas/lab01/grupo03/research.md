# Laboratorio 01 — Mini-research

**Extensión:** 800 a 1000 palabras (sin contar bibliografía)
**Modalidad:** un tema por grupo, a elección
**Entrega:** `entregas/lab01/grupoXX/research.md`

---

## Por qué se pide esto

Un ingeniero en sistemas que trabaja en seguridad va a tener que leer
documentación técnica, informes de incidentes y normativa, y va a tener que
distinguir qué está respaldado de qué es marketing. Esa habilidad no se
adquiere leyendo resúmenes: se adquiere yendo a la fuente.

No se busca un resumen de Wikipedia con otras palabras. Se busca que tomen una
posición y la defiendan con evidencia.

---

## Temas a elección

Elegí **uno**. Indicá cuál al principio del documento.

### Tema 1 — La evolución del perfil del atacante, 1988 a hoy

De un estudiante de posgrado que libera un gusano por curiosidad a
organizaciones criminales con estructura empresarial, servicio de atención a
la víctima y programas de afiliados.

Cuestiones a abordar: qué motivaciones dominaron en cada etapa, cómo cambió la
relación costo/beneficio del ataque, qué papel jugó la aparición de las
criptomonedas, y qué implica este cambio para el modelo de amenaza de una PyME
argentina hoy.

### Tema 2 — La cadena de suministro de software como superficie de ataque

Comprometer al proveedor para llegar a miles de clientes de una sola vez.
Tomen como referencia el caso SolarWinds/SUNBURST (2020) y el caso Log4Shell
(2021) — que son distintos entre sí, y esa diferencia es parte del análisis.

Cuestiones a abordar: por qué el modelo de confianza tradicional falla acá,
qué proponen las iniciativas de **SBOM** (Software Bill of Materials) y
**SLSA**, y qué límites tienen esas propuestas.

### Tema 3 — La disponibilidad, la propiedad descuidada de la tríada

La confidencialidad se lleva los titulares. Pero para muchas organizaciones, un
día sin sistemas cuesta más que una filtración de datos.

Cuestiones a abordar: por qué la disponibilidad recibe menos atención en la
formación y en el presupuesto, cómo el ransomware la convirtió en el vector
económicamente más rentable, y qué relación tiene con conceptos como RTO, RPO y
continuidad del negocio.

### Tema 4 — Criptografía post-cuántica

El NIST publicó en 2024 sus primeros estándares de criptografía resistente a
computadoras cuánticas: **FIPS 203**, **FIPS 204** y **FIPS 205**.

Cuestiones a abordar: qué problema resuelven exactamente (y cuál **no**
resuelven), qué significa la estrategia *harvest now, decrypt later* para los
datos que una organización cifra hoy, y qué implica la migración para sistemas
en producción.

> Ojo con este tema: es el que más ruido tiene en la divulgación. Distinguir lo
> que dicen los documentos del NIST de lo que dicen los titulares es
> exactamente el ejercicio.

### Tema 5 — Ley 26.388 y las zonas grises de la divulgación responsable

La Ley 26.388 incorporó al Código Penal argentino las figuras de delitos
informáticos. La Ley 27.411 aprobó la adhesión al Convenio de Budapest.

Cuestiones a abordar: qué conductas quedaron tipificadas, qué situación tiene
en la Argentina quien descubre e informa de buena fe una vulnerabilidad en un
sistema de terceros, y cómo tratan otras jurisdicciones ese mismo problema.

> Trabajen con el texto de la ley, no con notas periodísticas sobre la ley. No
> hace falta ser abogado; hace falta leer la fuente.

---

## Requisitos

### Extensión

Entre **800 y 1000 palabras**, sin contar la bibliografía. Fuera de ese rango
se penaliza. La restricción es parte del ejercicio: obliga a decidir qué entra
y qué no.

### Fuentes

- **Mínimo 3 fuentes.**
- De ellas, **al menos 2 deben ser primarias o arbitradas**.

| Cuenta como primaria o arbitrada | No cuenta |
|---|---|
| Documentos del NIST, ISO, IETF (RFC) | Wikipedia |
| Texto de una ley o resolución oficial | Blogs de divulgación general |
| Papers con revisión por pares | Notas periodísticas |
| Informes técnicos oficiales de un fabricante o CERT | Videos de YouTube |
| Informes forenses de un incidente publicados por la organización afectada | Publicaciones de LinkedIn |

Las fuentes secundarias **se pueden usar** — de hecho son útiles para armar la
cronología de un hecho. Solo que no cuentan para el mínimo de dos.

### Citación

Formato **APA**. Citas en el cuerpo del texto donde corresponda, y lista
completa al final.

**Toda fuente citada tiene que existir y ser localizable.** Una cita inventada
o que no se puede encontrar es **causal de rechazo automático** de la entrega
completa. Esto no es una formalidad: es lo que distingue un trabajo técnico de
una opinión.

### Declaración de uso de IA

Obligatoria, al final del documento. Ver el modelo más abajo.

Advertencia específica para este trabajo: **los asistentes de IA fabrican citas
con mucha facilidad.** Producen referencias con formato impecable, autores
plausibles y años coherentes que no existen. Si usaste un asistente para
buscar bibliografía, **verificá cada referencia entrando a la fuente original**
antes de citarla. Una cita inexistente hunde el trabajo, y la responsabilidad
es de quien firma.

---

## Estructura sugerida

No es obligatoria, pero funciona:

1. **Planteo** (~100 palabras) — cuál es la pregunta y por qué importa.
2. **Desarrollo** (~600 palabras) — la evidencia, organizada. Acá van las citas.
3. **Tensión o límite** (~150 palabras) — qué no está resuelto, qué se discute,
   dónde falla la solución que describiste. Esta sección es la que distingue un
   trabajo bueno de uno correcto.
4. **Cierre** (~100 palabras) — qué implica para la práctica profesional.

---

## Evaluación

Vale **20 de los 100 puntos** del laboratorio. El desglose está en
[`rubrica.md`](rubrica.md).

Lo que más pesa: **calidad de las fuentes** y **el análisis propio**. Un
trabajo que resume correctamente tres fuentes buenas sin agregar nada llega a
la mitad del puntaje. Lo que sube la nota es la sección de tensión: mostrar que
entendieron dónde la respuesta no es limpia.

---

## Plantilla

```markdown
# Mini-research — Lab 01

**Grupo:** NN
**Tema elegido:** N — (título)
**Cantidad de palabras:** ___ (sin bibliografía)

---

## Planteo

(...)

## Desarrollo

(...)

## Tensión / límites

(...)

## Cierre

(...)

---

## Bibliografía

Formato APA. Marcá cada fuente como [PRIMARIA], [ARBITRADA] o [SECUNDARIA].

1. [PRIMARIA] ...
2. [ARBITRADA] ...
3. [SECUNDARIA] ...

---

## Declaración de uso de asistentes de IA

**¿Se usaron asistentes de IA en este trabajo?** Sí / No

| Herramienta | Para qué | Qué partes afectó | Cómo se verificó |
|---|---|---|---|
| | | | |

**Verificación de fuentes:** el grupo declara haber accedido y verificado
individualmente cada una de las referencias citadas.
```

---

## Cómo contar las palabras

```bash
# Contar palabras de un archivo markdown, aproximado
wc -w research.md
```

Restá a mano lo que ocupan la bibliografía y la declaración de IA, o contá solo
las secciones de contenido. No hace falta precisión al dígito: si están entre
780 y 1020 no hay problema. Si entregan 400 o 1800, sí.
