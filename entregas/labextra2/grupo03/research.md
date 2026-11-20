# Research — Lab Extra 2: El repo que delata

## 1. Introducción

La exposición accidental de credenciales en repositorios Git representa un riesgo de seguridad porque los secretos pueden permanecer accesibles incluso después de eliminarlos de los archivos actuales. Para reducir este riesgo existen herramientas que cumplen funciones diferentes: algunas detectan credenciales y otras permiten limpiar el historial.

En este trabajo se comparan **Gitleaks**, orientada a la detección, y **git-filter-repo**, destinada a la reescritura del historial.

## 2. Gitleaks — Detección de secretos

**¿Qué busca?**

Gitleaks es una herramienta de código abierto que analiza repositorios, archivos y datos de entrada para detectar posibles secretos, como contraseñas, claves API y tokens. Puede inspeccionar tanto el contenido actual como el historial Git mediante el análisis de los parches de los commits.

Una característica importante es que permite buscar secretos en commits anteriores, lo que resulta útil para situaciones como R1, donde una credencial fue eliminada del código, pero continuó presente en el historial.

Para que el análisis histórico sea completo, es necesario configurar el alcance del escaneo de acuerdo con las ramas y los commits que se quieren inspeccionar. Un análisis limitado a los archivos actuales no garantiza detectar secretos presentes únicamente en versiones anteriores.

**¿Cómo se utilizaría en un pipeline de CI/CD?**

Se puede integrar de dos maneras complementarias:

- **Antes del commit:** instalarlo como un hook `pre-commit`, para analizar los cambios preparados y bloquear commits que contengan posibles credenciales.
- **Durante CI:** ejecutar un análisis automático cuando se crea un pull request o se realiza un push. Si se detecta un secreto, el pipeline puede fallar y evitar que el cambio avance hasta su integración.

Ejemplo de ejecución:

```bash
gitleaks git -v --log-opts="--all" .
```

**¿Qué no resuelve?**

Gitleaks detecta posibles secretos, pero no los revoca ni los invalida. Tampoco elimina automáticamente los datos de forks, clones o copias externas. Su efectividad depende de las reglas de detección y de que los controles estén correctamente configurados.

Además, los hooks locales pueden omitirse, por lo que conviene complementarlos con controles del lado del servidor.

**Estado del proyecto:** el repositorio oficial de Gitleaks informa que el proyecto está completo en cuanto a nuevas funcionalidades y que el mantenimiento futuro se centra en parches de seguridad. Es importante tener en cuenta este aspecto al evaluar su adopción y mantenimiento a largo plazo.

Fuente: [Gitleaks — Repositorio oficial](https://github.com/gitleaks/gitleaks).

## 3. git-filter-repo — Limpieza del historial

**¿Qué busca y qué permite hacer?**

`git-filter-repo` es una herramienta que permite reescribir el historial de un repositorio Git. Puede eliminar archivos completos, rutas específicas o reemplazar cadenas de texto sensibles en los commits.

Por ejemplo, permite quitar un archivo `.env` de todas las versiones del repositorio o reemplazar una credencial que aparece en diferentes commits.

Esto resulta útil cuando un secreto ya fue incorporado al historial y es necesario reducir su exposición.

**¿Cómo se utilizaría en un pipeline de CI/CD?**

No es una herramienta que deba ejecutarse automáticamente en cada build o push normal, porque reescribe la historia y modifica los hashes de los commits.

Su utilización corresponde a un procedimiento controlado de respuesta ante incidentes:

1. Revocar o rotar primero las credenciales comprometidas.
2. Crear un clon de trabajo del repositorio.
3. Ejecutar `git-filter-repo` para eliminar los archivos o reemplazar los secretos.
4. Revisar el historial resultante y verificar que los datos sensibles ya no aparezcan.
5. Actualizar las referencias remotas y coordinar la limpieza de los clones y forks.

Ejemplo para eliminar un archivo de todo el historial:

```bash
git-filter-repo --sensitive-data-removal \
  --invert-paths \
  --path .env
```

**¿Qué no resuelve?**

La herramienta no revoca credenciales ni impide que alguien utilice un secreto que ya obtuvo. Tampoco puede limpiar automáticamente las copias que otras personas tienen en sus equipos, los forks externos o todas las referencias almacenadas por plataformas de alojamiento.

Además, reescribir el historial modifica los identificadores de los commits y puede afectar ramas, etiquetas y solicitudes de integración. Por eso requiere coordinación con los colaboradores.

Fuente: [git-filter-repo — Documentación oficial](https://github.com/newren/git-filter-repo) y [GitHub — Eliminación de datos confidenciales](https://docs.github.com/es/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## 4. Comparación

| Característica | Gitleaks | git-filter-repo |
|---|---|---|
| Función principal | Detectar secretos | Reescribir el historial |
| Analiza archivos actuales | Sí | No es su función principal |
| Analiza historial Git | Sí | Modifica el historial |
| Uso en CI | Escaneo en cada cambio | Procedimiento controlado de remediación |
| Revoca credenciales | No | No |
| Limpia forks y clones externos | No | No |
| Previene nuevos secretos | Ayuda a detectarlos antes de integrar cambios | No |

Las herramientas son complementarias: Gitleaks ayuda a encontrar credenciales expuestas, mientras que git-filter-repo permite limpiar el historial del repositorio. Ninguna reemplaza la revocación o rotación de las credenciales comprometidas.

## 5. Pregunta de cierre: ¿Por qué el escaneo de GitHub no alcanza?

GitHub ofrece dos mecanismos relacionados, pero diferentes. **Secret Scanning** analiza repositorios para detectar credenciales compatibles y generar alertas. **Push Protection**, por su parte, puede bloquear determinados secretos antes de que sean incorporados al repositorio mediante un push. La disponibilidad y cobertura de estos controles dependen de los tipos de secretos admitidos y de la configuración.

Sin embargo, esto no garantiza una protección completa. Existen varias ventanas de exposición:

**1. Tiempo entre publicación y detección o revocación.**

Desde que se publica una credencial hasta que se detecta, se notifica al proveedor y se revoca, puede existir un intervalo durante el cual un atacante puede utilizarla. La notificación no equivale necesariamente a una revocación instantánea.

**2. Copias externas del repositorio.**

Un atacante puede clonar el repositorio, descargar una rama o guardar el contenido antes de que se elimine o reescriba el historial. Los forks, clones locales y copias de seguridad pueden conservar la información incluso después de limpiar el repositorio original.

**3. Cobertura limitada de la detección.**

No todos los secretos tienen formatos reconocibles o están incluidos entre los patrones admitidos. También pueden existir configuraciones incorrectas o mecanismos de protección que hayan sido omitidos o desactivados.

Por estos motivos, el escaneo automático debe considerarse una capa de defensa y no una solución completa. La respuesta correcta ante una filtración es revocar o rotar inmediatamente la credencial, investigar su posible utilización, limpiar el historial cuando corresponda y controlar las copias externas.

## 6. Declaración de uso de inteligencia artificial

Se utilizó ChatGPT como herramienta de apoyo para organizar la investigación, comparar las funcionalidades y limitaciones de las herramientas seleccionadas y estructurar el documento. Se consultaron las documentaciones oficiales de los proyectos y de GitHub, que se incluyen como fuentes. La selección de herramientas y las conclusiones fueron revisadas en el contexto del laboratorio.