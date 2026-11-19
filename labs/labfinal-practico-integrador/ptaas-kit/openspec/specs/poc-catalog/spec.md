# Spec — poc-catalog

Tests: `tests/test_poc_catalog.py`
Datos: `harness/poc/catalog.yaml` · Código: `harness/poc/catalog.py`

## Requirement: Verificaciones inertes
Toda entrada del catálogo DEBE ser de tipo `inert_check`: confirma una debilidad observando la respuesta, sin ejecutar código en el objetivo ni extraer datos.

### Scenario: entrada de otro tipo
- GIVEN una entrada con `kind` distinto de `inert_check`
- WHEN se carga el catálogo
- THEN se rechaza

## Requirement: Solo laboratorio
Toda entrada DEBE ser `lab_only`.

### Scenario: entrada no marcada como laboratorio
- GIVEN una entrada con `lab_only: false`
- WHEN se carga el catálogo
- THEN se rechaza

## Requirement: Aprobación registrada
Toda entrada DEBE tener `approved_by` y `approved_at`.

### Scenario: entrada sin aprobación
- GIVEN una entrada sin `approved_at`
- WHEN se carga el catálogo
- THEN se rechaza

## Requirement: Parámetros declarados
La ejecución DEBE aceptar exactamente los parámetros declarados por la entrada, con valores de texto acotados y sin saltos de línea.

### Scenario: parámetro extra
- GIVEN un parámetro no declarado (por ejemplo `payload`)
- WHEN se ejecuta la verificación
- THEN se rechaza y no se envía nada

## Requirement: Aprobación humana previa
La ejecución NO DEBE enviar tráfico sin la aprobación del Reviewer para ese hallazgo.

### Scenario: sin aprobación
- GIVEN una verificación sin aprobación
- WHEN se intenta ejecutar
- THEN se rechaza y el sender no es invocado

## Requirement: Canario inerte
La verificación de reflexión DEBE usar un canario único sin marcado ejecutable y concluir solo observando la respuesta.

### Scenario: canario reflejado sin codificar
- GIVEN una respuesta que refleja el canario sin codificar
- WHEN se evalúa
- THEN el resultado es `validated`

### Scenario: canario codificado
- GIVEN una respuesta que codifica el canario
- WHEN se evalúa
- THEN el resultado es `not_validated`
