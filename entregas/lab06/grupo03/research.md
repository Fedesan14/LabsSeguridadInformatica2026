# Lab 06 — Mini-research

**Grupo:** 03

## Fingerprinting pasivo vs. activo: cómo WhatWeb deduce el stack

### 1. ¿Qué es el fingerprinting?

El fingerprinting consiste en identificar tecnologías utilizadas por un servicio a partir de las características que expone. En una aplicación web, estas características pueden incluir cabeceras HTTP, metadatos HTML, títulos de página y respuestas ante solicitudes específicas.

Identificar una tecnología y su versión ayuda a orientar la enumeración hacia recursos predeterminados y posibles configuraciones inseguras.

### 2. Fingerprinting pasivo

El fingerprinting pasivo analiza información que el servicio expone durante una interacción normal, sin necesitar pruebas específicas sobre múltiples rutas o comportamientos.

Por ejemplo, una página web puede incluir un metadato `generator` que identifique el CMS. Las cabeceras HTTP también pueden revelar el servidor o la tecnología utilizada.

En el laboratorio, la página principal de PhantomCorp expuso indicios como `MetaGenerator[PhantomCMS 3.7]` y `X-Powered-By[PhantomCMS/3.7]`.

### 3. Fingerprinting activo

El fingerprinting activo realiza solicitudes específicas para obtener más información sobre el objetivo. Puede incluir consultas a rutas conocidas, análisis de respuestas y comprobaciones de comportamientos característicos de un producto.

Estas pruebas permiten ampliar la información disponible, aunque sus resultados dependen de la configuración del servidor y de las medidas que utilice para ocultar o modificar sus respuestas.

### 4. ¿Cómo trabaja WhatWeb?

WhatWeb envía solicitudes HTTP y analiza elementos de las respuestas para buscar patrones asociados a tecnologías conocidas. Según las señales encontradas, puede identificar el servidor web, un CMS, bibliotecas u otros componentes.

La opción `-a 3` solicita un nivel de agresividad mayor que el modo predeterminado, lo que puede producir más solicitudes y comprobaciones. El resultado depende de las señales que el servicio exponga y de los detectores disponibles en la herramienta.

En PhantomCorp, WhatWeb identificó `PhantomCMS 3.7` a partir de los metadatos y las cabeceras observadas.

### 5. Limitaciones

- Una cabecera puede ocultarse, modificarse o falsificarse.
- Identificar un producto no demuestra que exista una vulnerabilidad.
- Una versión detectada puede no representar todos los componentes instalados.
- Los resultados deben verificarse mediante evidencias adicionales.
- Las pruebas deben limitarse al objetivo autorizado del laboratorio.

### 6. Relación con la enumeración

El fingerprinting permite orientar la búsqueda de archivos predeterminados y recursos asociados a una tecnología. En lugar de probar rutas completamente al azar, se utiliza la información obtenida para formular hipótesis y comprobarlas mediante solicitudes HTTP.

En este laboratorio, la identificación de PhantomCMS 3.7 sirvió como punto de partida para buscar un archivo predeterminado del CMS y completar el reto R5.

### 7. Conclusión

El fingerprinting reduce la incertidumbre sobre las tecnologías expuestas por un servidor. Sin embargo, sus resultados son indicios que deben validarse: identificar un CMS o una versión permite orientar la investigación, pero no constituye por sí mismo una prueba de vulnerabilidad.
