# Delta — authorization

## Requirement: Enforcement de alcance
El sistema DEBE rechazar toda acción activa sobre un activo fuera del RoE vigente.

### Scenario: activo fuera de alcance
- GIVEN un RoE que autoriza 10.0.0.0/24
- WHEN un agente intenta escanear 10.0.1.5
- THEN la acción es bloqueada y registrada en la bitácora

## Requirement: Vigencia del token
El sistema NO DEBE ejecutar acciones con un scope token vencido.

### Scenario: token vencido
- GIVEN un token cuya ventana terminó
- WHEN un agente invoca una acción en el activo autorizado
- THEN la acción es bloqueada (BLOCKED) y registrada

## Requirement: Fase del token
Un token DEBE habilitar únicamente acciones de su fase.

### Scenario: acción de otra fase
- GIVEN un token de fase ANALYZE
- WHEN se invoca una acción de VALIDATE
- THEN la acción es bloqueada y registrada

## Requirement: Kill switch
El sistema DEBE detener toda ejecución al activar el kill switch.

### Scenario: kill switch activo
- GIVEN un engagement en curso y el kill switch activado
- WHEN cualquier agente invoca una acción
- THEN se registra ABORTED y no se ejecuta la herramienta
