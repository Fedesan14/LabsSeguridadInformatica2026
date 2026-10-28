# Mini-research — Laboratorio 04

**Tema elegido:** **D.** Análisis de riesgo cuantitativo vs cualitativo: ventajas y límites.
- [ ] **A.** ISO/IEC 27001: qué es un SGSI y el ciclo PDCA.
- [ ] **B.** NIST Cybersecurity Framework: las cinco funciones y cómo se usan.
- [ ] **C.** Ley 26.388 y marco legal argentino de delitos informáticos.
- [x] **D.** Análisis de riesgo cuantitativo vs cualitativo: ventajas y límites.

## Desarrollo

### Las dos (en realidad tres) formas de evaluar riesgo

NIST SP 800-30 Rev. 1 distingue tres enfoques de evaluación [1]:

- **Cuantitativo:** el riesgo se expresa en números con unidad, normalmente
  dinero por año. Es lo que hicimos en la Parte B: `ALE = SLE × ARO`.
- **Cualitativo:** el riesgo se expresa en categorías ordinales
  (bajo/medio/alto) que salen del juicio de expertos, y se ubica en una
  **matriz de riesgo** probabilidad × impacto.
- **Semicuantitativo:** escalas numéricas (1–5, 0–100) que se pueden ordenar y
  sumar, pero que no representan una magnitud real: un "4" no es el doble de
  un "2".

ISO/IEC 27005:2022, la guía de gestión de riesgos que acompaña a ISO/IEC
27001, admite los dos enfoques y deja la elección a la organización según el
propósito y los datos disponibles [2].

### Qué gana el enfoque cuantitativo

1. **Habla el idioma de quien decide la inversión.** "Este control cuesta
   $6 000 y evita $24 000 por año" se compara directo contra cualquier otro
   gasto de la empresa. "El riesgo pasa de alto a medio" no se puede comparar
   contra un presupuesto.
2. **Permite calcular el ROI de un control** y, sobre todo, el valor
   **incremental** de agregar otro. En la Parte B eso mostró que sumar un WAF
   encima de la tokenización tenía ROI negativo; con una matriz de colores los
   dos controles habrían "bajado el riesgo" y la diferencia no se vería.
3. **Obliga a explicitar supuestos.** Un ARO de 0,3 se puede discutir,
   comparar con datos de la industria y corregir. Un "probabilidad media" se
   discute mucho menos porque nadie sabe exactamente qué significa.

### Qué limita al enfoque cuantitativo

1. **Los datos son pobres.** Para un PyME no hay historia propia de
   incidentes: el ARO casi siempre es una estimación de expertos con un número
   puesto. La precisión de `36000.00` es **falsa precisión** si la entrada
   podía ser 0,1 o 0,5.
2. **ALE es un promedio y esconde la cola.** Un evento raro y catastrófico y
   uno frecuente y chico pueden dar el mismo ALE. Para una empresa chica
   importa más el peor año posible que el año promedio. FAIR (*Factor Analysis
   of Information Risk*), el modelo cuantitativo estandarizado por The Open
   Group, responde a esto usando **rangos y distribuciones** (mínimo, más
   probable, máximo) y simulación Monte Carlo en vez de un único número, y
   reporta una curva de excedencia de pérdidas [3].
3. **Asume riesgos independientes.** En el lab, el ransomware entra por el
   acceso remoto sin MFA y su costo depende de dónde está el backup. Sumar ALE
   de riesgos correlacionados cuenta dos veces o no cuenta nada.
4. **Algunos impactos no tienen precio fácil:** reputación, daño a las
   personas cuyos DNI se filtraron, obligaciones legales.

### Y los límites del cualitativo

El enfoque cualitativo es rápido, no necesita datos y sirve para una primera
pasada. Pero tiene problemas propios, documentados:

- Cox mostró que las matrices de riesgo pueden asignar **la misma categoría a
  riesgos cuantitativamente muy distintos**, e incluso una categoría mayor a un
  riesgo menor; su resolución es tan baja que en algunos casos es "peor que
  azar" para ordenar [4].
- Hubbard y Seiersen argumentan que las escalas ordinales **no reducen la
  incertidumbre, la esconden**: si los expertos pueden decir "alto", pueden
  dar un rango numérico calibrado, y ese rango sí se puede operar [5].
- Distintos evaluadores interpretan "probable" de forma muy distinta, así que
  dos matrices del mismo sistema no son comparables.

### Conclusión práctica

No es "uno u otro": se usan **en secuencia**. El cualitativo sirve para el
barrido inicial (¿qué ni siquiera vale la pena cuantificar?) y el cuantitativo
para las decisiones de inversión que importan. Y cuando se cuantifica, conviene
hacerlo con rangos y no con un único número, para que la incertidumbre quede a
la vista en lugar de disfrazada de decimales.

## Fuentes (mín. 3)

1. NIST, *SP 800-30 Rev. 1 — Guide for Conducting Risk Assessments*, 2012, §2.3.2 "Assessment Approaches". https://doi.org/10.6028/NIST.SP.800-30r1
2. ISO/IEC 27005:2022, *Information security, cybersecurity and privacy protection — Guidance on managing information security risks*.
3. J. Freund y J. Jones, *Measuring and Managing Information Risk: A FAIR Approach*, Butterworth-Heinemann, 2014. Ver también The Open Group, *Risk Taxonomy (O-RT)* y *Risk Analysis (O-RA)*.
4. L. A. Cox Jr., "What's Wrong with Risk Matrices?", *Risk Analysis*, 28(2), 2008, pp. 497–512. https://doi.org/10.1111/j.1539-6924.2008.01030.x
5. D. W. Hubbard y R. Seiersen, *How to Measure Anything in Cybersecurity Risk*, Wiley, 2016.

## Reflexión

Al hacer la Parte B, lo más incómodo fue que el código es trivial (una
multiplicación) y todo el peso está en los números que se le dan. El ranking
cambió de orden con sólo mover un ARO de 0,25 a 0,5, y ninguno de los dos
valores es más "verdadero" que el otro. Eso no hace inútil al análisis: lo
útil fue que, al tener que escribir un número, tuvimos que justificarlo, y esa
justificación expuso relaciones (backup ↔ ransomware, MFA ↔ ransomware) que un
cuadro de colores no nos habría obligado a ver. La lección que nos llevamos es
que el valor del análisis cuantitativo está menos en el resultado que en la
discusión que obliga a tener, y que el resultado hay que presentarlo con su
incertidumbre.
