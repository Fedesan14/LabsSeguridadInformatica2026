# Mini-research — Laboratorio 07

**Tema elegido:** A. Consultas parametrizadas / prepared statements.

- [x] **A.** Consultas parametrizadas / prepared statements: cómo separan datos de código y por qué eliminan la SQLi de raíz (con ejemplo en Python).
- [ ] **B.** sqlmap por dentro: cómo detecta la inyección.
- [ ] **C.** Un caso real de RCE por command injection.
- [ ] **D.** Broken Access Control (OWASP A01).

## Desarrollo

### 1. ¿Qué es una consulta parametrizada?

Las consultas parametrizadas, también conocidas como *prepared statements*, son un mecanismo de seguridad que permite separar las instrucciones SQL de los datos proporcionados por el usuario.

El problema aparece cuando una aplicación construye consultas SQL concatenando directamente los valores ingresados por el usuario. Si esos valores contienen instrucciones SQL, el motor de base de datos podría interpretarlas como parte de la consulta y modificar su comportamiento.

En cambio, al utilizar parámetros, la estructura de la consulta se define por separado y los valores se envían mediante marcadores de posición (*placeholders*). De esta manera, los datos ingresados se interpretan como valores y no como instrucciones SQL.

### 2. Ejemplo vulnerable

El siguiente ejemplo utiliza Python y SQLite. La consulta concatena directamente el nombre ingresado:

```python
usuario = input("Ingrese su usuario: ")

consulta = "SELECT * FROM usuarios WHERE nombre = '" + usuario + "'"

cursor.execute(consulta)
```

Este enfoque es vulnerable porque un atacante podría introducir caracteres especiales y expresiones SQL para alterar la consulta original.

### 3. Ejemplo seguro con parámetros

La forma correcta es utilizar un marcador `?` y pasar el valor por separado:

```python
usuario = input("Ingrese su usuario: ")

consulta = "SELECT * FROM usuarios WHERE nombre = ?"

cursor.execute(consulta, (usuario,))
```

En este caso, SQLite recibe la consulta y el valor como elementos separados. Aunque el usuario ingrese texto que contenga instrucciones SQL, ese contenido será tratado como un dato y no podrá modificar la estructura de la consulta.

### 4. ¿Por qué previene SQL Injection?

La parametrización evita que los datos proporcionados por un usuario sean interpretados como código SQL. Esto impide que caracteres como las comillas o expresiones como `OR 1=1` puedan modificar la lógica de una consulta correctamente parametrizada.

Es importante aclarar que la parametrización protege los valores de las consultas, pero no reemplaza los controles de autorización. También se deben utilizar listas permitidas para elementos dinámicos que no admiten parámetros, como nombres de columnas o direcciones de ordenamiento.

Además, se recomienda aplicar el principio de mínimo privilegio a las cuentas utilizadas por la aplicación para conectarse a la base de datos.

### 5. Relación con el laboratorio

En los retos R1 y R2 del Laboratorio 07 comprobamos cómo una aplicación vulnerable puede permitir alterar consultas SQL.

En R1, modificamos la consulta de autenticación para acceder como administrador. En R2, utilizamos UNION para obtener información de otra tabla.

Si la aplicación hubiera utilizado consultas parametrizadas correctamente, los valores ingresados no habrían podido modificar la estructura de esas consultas.

## Fuentes (mínimo 3, verificables)

1. **OWASP — SQL Injection Prevention Cheat Sheet.** Explica el funcionamiento de las consultas parametrizadas y las principales medidas para prevenir SQL Injection.  
   https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

2. **Python — Documentación oficial de sqlite3.** Presenta el uso de placeholders y la sustitución de parámetros, además de ejemplos de consultas vulnerables y seguras.  
   https://docs.python.org/3/library/sqlite3.html

3. **MITRE — CWE-89: Improper Neutralization of Special Elements used in an SQL Command.** Describe la debilidad SQL Injection y recomienda utilizar consultas parametrizadas y prepared statements.  
   https://cwe.mitre.org/data/definitions/89.html

## Reflexión (3–5 líneas)

Este tema nos permitió comprender que SQL Injection no se soluciona simplemente filtrando caracteres especiales, sino evitando que los datos del usuario formen parte del código SQL. Los retos R1 y R2 demostraron las consecuencias de no implementar esta separación. Consideramos que utilizar consultas parametrizadas desde el desarrollo inicial es una medida fundamental para proteger las aplicaciones que trabajan con bases de datos.