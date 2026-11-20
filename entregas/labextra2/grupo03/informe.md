# Informe forense â€” Lab Extra 2: El repo que delata

**Materia:** Seguridad Informática
**Laboratorio:** Extra 2 El repo que delata (forense Git)
**Grupo:** 03
**Repositorio:** `LabsSeguridadInformatica2026`
**Rama de trabajo:** `labextra2-grupo03`

## 1. Integrantes

| Apellido y nombre | Usuario de GitHub |
|---|---|
| Sanchez, Federico | `Fedesan14` |
| Host, Efrai­n | `hostefrain` |
| Rumis, Lohana | `Lohana-Rumis` |
| Enria, Elian | `elian-enria-id` |

## 2. Declaración de uso de inteligencia artificial

Se utilizó ChatGPT como herramienta de apoyo para organizar la investigación, interpretar resultados de comandos Git, estructurar el informe y revisar explicaciones técnicas sobre el modelo de objetos de Git y las herramientas de prevención y remediación de filtraciones.

Los comandos de investigación fueron ejecutados sobre el repositorio del caso por los integrantes del grupo. Las conclusiones y evidencias incluidas en este informe se basan en las salidas obtenidas durante esa investigación. La herramienta de IA no reemplaza las evidencias ni se considera autora de los hallazgos.

## 3. Objetivo y metodologÃ­a

El objetivo fue realizar un anÃ¡lisis forense del repositorio de PhantomCorp para identificar secretos expuestos, reconstruir eventos de Git y comprobar si las operaciones realizadas para eliminar informaciÃ³n fueron suficientes.

La investigaciÃ³n se dividiÃ³ en tres lÃ­neas:

- **R1 â€” Historial de commits:** bÃºsqueda de secretos en versiones anteriores mediante `git log -p`.
- **R2 â€” Objetos y reflog:** recuperaciÃ³n de informaciÃ³n que dejÃ³ de estar referenciada despuÃ©s de un `reset`.
- **R3 â€” Ramas abandonadas:** inspecciÃ³n de ramas que no forman parte de la rama principal.

Se utilizaron comandos de inspecciÃ³n, comparaciÃ³n y recuperaciÃ³n de objetos. Las salidas completas se encuentran en `evidencia/salidas/`.

## 4. LÃ­nea de tiempo forense

Los eventos relevantes reconstruidos a partir del historial y del reflog son los siguientes. Los autores de los commits investigados figuran como `dev-jperez <jperez@phantomcorp.example>`.

| Fecha y hora (-0300) | Hash | Autor / evento | DescripciÃ³n |
|---|---|---|---|
| 05/08/2026 16:30 | `0abdf95` | dev-jperez | Crea el commit `wip: pasarela de pagos (falta todo)` en `feature/pasarela-pagos`. Contiene un secreto de pagos. |
| 05/08/2026 16:30 | `9333f2b` | Evento de reflog | El reflog registra la creaciÃ³n de `feature/pasarela-pagos` desde `HEAD~1`, apuntando a este commit. |
| 10/08/2026 09:12 | `de33a75` | dev-jperez | Commit inicial: `inicial: deploy-tool con token por variable de entorno`. |
| 10/08/2026 18:47 | `9333f2b` | dev-jperez | Commit `hotfix: deploy roto en produccion (config temporal)`. Introduce un token directamente en el cÃ³digo. |
| 11/08/2026 10:05 | `eafb81c` | dev-jperez | Commit `fix: sacar credenciales del codigo (ups)`. Elimina el token del estado actual del cÃ³digo. |
| 12/08/2026 14:22 | `bc9d0db` | dev-jperez | Commit `wip: notas del cluster nuevo (no mergear todavia)`. Agrega notas con una clave de staging. |
| 12/08/2026 14:22 | `eafb81c` | Evento de reflog | Se registra `reset: moving to HEAD~1`, que mueve `main` al commit anterior y deja `bc9d0db` sin una referencia de rama. |
| 20/08/2026 11:00 | `fa714bd` | dev-jperez | Commit `docs: estado del proyecto`. El README afirma que el proyecto estÃ¡ limpio y sin secretos. |

**ObservaciÃ³n sobre la cronologÃ­a:** el reflog registra la creaciÃ³n de `feature/pasarela-pagos` el 05/08 a las 16:30 y la asocia con `9333f2b`, pero el commit `9333f2b` tiene fecha 10/08 a las 18:47. Es una inconsistencia temporal presente en los datos del caso. No se dispone de evidencia suficiente para determinar su causa, por lo que no se modifica ni se intenta justificar.

### 4.1. Tiempo de exposiciÃ³n de los secretos

**R1 â€” Token de API**

El token `FLAG{git_log_no_olvida}` aparece en `9333f2b`, fechado el 10/08/2026 a las 18:47. El commit que lo elimina del estado actual, `eafb81c`, estÃ¡ fechado el 11/08/2026 a las 10:05.

Entre ambos commits transcurrieron **15 horas y 18 minutos**.

Este intervalo representa el tiempo hasta la incorporaciÃ³n de la correcciÃ³n al historial, no el tiempo total durante el cual el secreto estuvo accesible. El commit que contiene el token continÃºa formando parte del historial.

**R2 â€” Clave de staging**

La clave `FLAG{git_reflog_rescata}` aparece en `bc9d0db`, fechado el 12/08/2026 a las 14:22. El reflog registra el `reset` que lo deja fuera de la rama `main` en el mismo segundo.

No es posible determinar el intervalo exacto entre el commit y el reset. Sin embargo, la informaciÃ³n siguiÃ³ siendo recuperable mediante el reflog y la bÃºsqueda de objetos no alcanzables.

No se encontrÃ³ evidencia que permita afirmar que la clave haya sido revocada o que haya dejado de estar expuesta.

**R3 â€” Secreto de pagos**

La rama `feature/pasarela-pagos` contiene el secreto `FLAG{git_rama_abandonada}` en el commit `0abdf95`, fechado el 05/08/2026 a las 16:30.

La rama seguÃ­a apareciendo en `git branch -a` durante la investigaciÃ³n. No se encontrÃ³ un commit o evento que demuestre su eliminaciÃ³n ni la revocaciÃ³n del secreto. Por lo tanto, no puede establecerse una fecha de finalizaciÃ³n de la exposiciÃ³n.

## 5. InvestigaciÃ³n de los retos

### 5.1. R1 â€” El historial recuerda

**Objetivo:** identificar un secreto que habÃ­a sido eliminado del cÃ³digo actual, pero que seguÃ­a presente en commits anteriores.

**Comandos utilizados:**

```bash
git log --oneline --all --decorate
git log -p --all
```

El primer comando permitiÃ³ visualizar los commits y las ramas disponibles. El segundo mostrÃ³ las modificaciones completas de los commits, incluyendo lÃ­neas agregadas y eliminadas.

**Hallazgo:**

En el commit `9333f2b`, cuyo mensaje es `hotfix: deploy roto en produccion (config temporal)`, se encontrÃ³:

```text
PHANTOM_API_TOKEN = "FLAG{git_log_no_olvida}"
```

La credencial quedÃ³ expuesta porque fue incorporada directamente al archivo de configuraciÃ³n y confirmada en un commit. Aunque luego se eliminÃ³ del cÃ³digo, el historial conservÃ³ la versiÃ³n anterior.

El commit posterior `eafb81c`, con mensaje `fix: sacar credenciales del codigo (ups)`, elimina esa credencial del cÃ³digo.

**Resultado:** `FLAG{git_log_no_olvida}`.

**ConclusiÃ³n:** borrar un secreto en un commit posterior no elimina su contenido de los commits anteriores. Cualquier persona que pueda consultar el historial puede recuperar la versiÃ³n que contenÃ­a la credencial.

**Evidencia:** `evidencia/salidas/r1.txt`.

### 5.2. R2 â€” El objeto perdido

**Objetivo:** recuperar informaciÃ³n que habÃ­a quedado fuera de la rama principal despuÃ©s de un `reset`.

**Comandos utilizados:**

```bash
git reflog --all
git show --stat bc9d0db
git show bc9d0db
git fsck --full --no-reflogs --unreachable
```

**Hallazgo en el reflog:**

Se identificÃ³ el commit `bc9d0db`, con mensaje `wip: notas del cluster nuevo (no mergear todavia)`. Inmediatamente despuÃ©s, el reflog registra:

```text
reset: moving to HEAD~1
```

La operaciÃ³n moviÃ³ la referencia `main` al commit anterior. Sin embargo, el commit perdido todavÃ­a podÃ­a localizarse mediante su hash.

**Contenido recuperado:**

```text
staging_key: FLAG{git_reflog_rescata}
```

El comando `git fsck --full --no-reflogs --unreachable` tambiÃ©n informÃ³ objetos no alcanzables:

```text
unreachable commit bc9d0dbe6aca41d639a515395cc983e139979102
unreachable tree 65ec201614a35871a642cc06df812ec4082d7ba9
unreachable blob fc979fdad9fb6246fd683eb2087b2d7e94ef0563
```

**Resultado:** `FLAG{git_reflog_rescata}`.

**ConclusiÃ³n:** un `git reset` modifica las referencias y, segÃºn el modo utilizado, tambiÃ©n el Ã­ndice y el directorio de trabajo. Sin embargo, no elimina inmediatamente los objetos que ya fueron creados. El reflog conserva registros de movimientos de referencias y `git fsck` permite localizar objetos no alcanzables.

**Evidencias:**

- `evidencia/salidas/r2-reflog.txt`
- `evidencia/salidas/r2-show-stat.txt`
- `evidencia/salidas/r2-show.txt`
- `evidencia/salidas/r2-fsck.txt`

### 5.3. R3 â€” La rama olvidada

**Objetivo:** investigar ramas que no forman parte de la rama principal y que podrÃ­an contener informaciÃ³n sensible.

**Comandos utilizados:**

```bash
git branch -a
git log --oneline --all --decorate
git log -p feature/pasarela-pagos
git show --stat 0abdf95
git show 0abdf95
```

**Hallazgo:**

La salida de `git branch -a` mostrÃ³:

```text
feature/pasarela-pagos
* main
```

La rama `feature/pasarela-pagos` contenÃ­a el commit `0abdf95`, con mensaje `wip: pasarela de pagos (falta todo)`.

Al inspeccionar su contenido se encontrÃ³ en `.env.pasarela`:

```text
PAGOS_SECRET=FLAG{git_rama_abandonada}
PAGOS_ENDPOINT=https://pagos.phantomcorp.example
```

TambiÃ©n se identificÃ³ el archivo `pasarela.py`, que contenÃ­a trabajo incompleto relacionado con la integraciÃ³n de pagos.

**Resultado:** `FLAG{git_rama_abandonada}`.

**ConclusiÃ³n:** una rama que no se fusionÃ³ con `main` puede seguir formando parte del repositorio y conservar informaciÃ³n sensible. Que una funcionalidad estÃ© abandonada o incompleta no significa que sus archivos hayan desaparecido.

**Evidencias:**

- `evidencia/salidas/r3-log.txt`
- `evidencia/salidas/r3-show-stat.txt`
- `evidencia/salidas/r3-show.txt`

## 6. Preguntas de anÃ¡lisis

### P1. Â¿QuÃ© ocurriÃ³ con el token de API?

El token `FLAG{git_log_no_olvida}` fue incorporado al repositorio en el commit `9333f2b`, del 10/08/2026 a las 18:47. El 11/08/2026 a las 10:05 se incorporÃ³ el commit `eafb81c`, que lo eliminÃ³ del estado actual del cÃ³digo.

La exposiciÃ³n entre ambos eventos fue de 15 horas y 18 minutos. Sin embargo, el commit original no fue eliminado del historial.

Por lo tanto, la limpieza realizada no fue suficiente. El token debe considerarse comprometido y debe revocarse o rotarse, aunque ya no aparezca en los archivos actuales.

### P2. Â¿Por quÃ© el reset no eliminÃ³ las notas?

Git utiliza un modelo de objetos. Los commits, Ã¡rboles y blobs son objetos identificados mediante hashes.

Un commit referencia un Ã¡rbol, que a su vez referencia otros Ã¡rboles y blobs. Las ramas son referencias que apuntan a commits. Cuando se ejecuta un `git reset`, la referencia de la rama actual se mueve al commit indicado y, segÃºn el modo utilizado, se actualizan tambiÃ©n el Ã­ndice y el directorio de trabajo.

En este caso, se ejecutÃ³ un `git reset` que moviÃ³ la referencia `main` al commit anterior (`HEAD~1`). Esto hizo que `bc9d0db` dejara de estar referenciado por `main`, pero no eliminÃ³ inmediatamente el objeto del repositorio. El commit permaneciÃ³ registrado en el reflog y pudo recuperarse como objeto no alcanzable.

Dos comandos que permiten demostrarlo son:

```bash
git reflog --all
git fsck --full --no-reflogs --unreachable
```

El primero muestra los movimientos de las referencias y el segundo permite localizar objetos que ya no son alcanzables desde las referencias actuales.

### P3. Â¿QuÃ© riesgo representa una rama abandonada en un repositorio pÃºblico o privado?

**Repositorio pÃºblico:**

El riesgo es muy alto. Cualquier persona puede acceder al repositorio y explorar las ramas disponibles. AdemÃ¡s, bots automatizados pueden clonar repositorios pÃºblicos y analizar sus commits, ramas y archivos en busca de credenciales.

Una rama olvidada puede exponer contraseÃ±as, tokens, claves de servicios externos, configuraciones internas o cÃ³digo que no estaba destinado a publicarse.

**Repositorio privado con 30 colaboradores:**

El acceso estÃ¡ restringido a los usuarios autorizados, pero el riesgo no desaparece. Cada colaborador puede tener una copia local del repositorio. TambiÃ©n pueden existir forks, copias de seguridad, pipelines de CI/CD y otros sistemas que hayan descargado los datos.

Cuantas mÃ¡s personas y sistemas tengan acceso, mayor es la superficie de exposiciÃ³n. Una rama abandonada con secretos sigue siendo peligrosa incluso si el repositorio no es pÃºblico.

### P4. Â¿CÃ³mo deberÃ­a responder PhantomCorp ante la filtraciÃ³n?

La remediaciÃ³n debe priorizar la seguridad de las credenciales y no solamente la limpieza visual del historial.

**1. Revocar y rotar los secretos inmediatamente.**

Identificar y revocar los tres secretos encontrados: el token de API, la clave de staging y el secreto de pagos. Emitir credenciales nuevas, revisar sus permisos y aplicar el principio de mÃ­nimo privilegio.

TambiÃ©n se deben consultar los registros de actividad de los servicios asociados para detectar posibles usos no autorizados.

**2. Contener el incidente y revisar los accesos.**

Identificar quÃ© usuarios, aplicaciones y sistemas podÃ­an utilizar las credenciales comprometidas. Revocar sesiones, tokens y permisos que pudieran estar comprometidos. Revisar los registros de auditorÃ­a y limitar temporalmente los cambios al repositorio mientras se coordina la remediaciÃ³n.

**3. Reescribir el historial del repositorio.**

Una vez revocadas las credenciales, utilizar herramientas como `git-filter-repo` para eliminar los secretos de los commits afectados y reescribir las referencias necesarias.

La reescritura cambia los hashes de los commits afectados y requiere coordinaciÃ³n para evitar que colaboradores vuelvan a introducir el historial antiguo.

**4. Contactar a los propietarios de forks y clones.**

Identificar forks, copias locales y otros lugares donde pueda existir el historial anterior. Informar a los colaboradores que deben descartar o limpiar sus copias antiguas y sincronizarse con el historial corregido.

La reescritura del repositorio principal no elimina automÃ¡ticamente los secretos de las copias externas.

**5. Verificar la remediaciÃ³n y prevenir nuevos incidentes.**

Volver a escanear el repositorio, revisar los accesos y monitorear el uso de las credenciales nuevas. Incorporar controles de detecciÃ³n antes del commit y durante el push, ademÃ¡s de capacitaciÃ³n para los desarrolladores.

**Â¿Por quÃ© reescribir la historia es menos urgente que rotar las credenciales?**

Porque la reescritura no invalida una credencial que ya fue expuesta. Aunque el secreto desaparezca del historial visible, una persona que lo haya obtenido puede seguir utilizÃ¡ndolo mientras el servicio lo acepte. La revocaciÃ³n o rotaciÃ³n corta esa posibilidad de uso; la reescritura reduce la exposiciÃ³n futura, pero no reemplaza la rotaciÃ³n.

### P5. Â¿QuÃ© mecanismos pueden impedir que un secreto ingrese al historial?

Se proponen dos mecanismos complementarios:

**1. Control local antes del commit: pre-commit hook.**

Se puede configurar Gitleaks como hook local para analizar los archivos preparados antes de crear un commit. Si detecta un patrÃ³n que parece una credencial, puede bloquear la operaciÃ³n y solicitar que el desarrollador elimine el secreto.

Este mecanismo permite detectar errores temprano, pero depende de que el desarrollador tenga instalado y habilitado el hook. TambiÃ©n puede ser omitido, por lo que no debe ser el Ãºnico control.

**2. Escaneo del lado del servidor durante el push.**

Se puede utilizar GitHub Secret Scanning con Push Protection, o un control equivalente en el servidor, para analizar los cambios antes de aceptarlos. Si detecta una credencial compatible con sus patrones, puede bloquear el push y solicitar una correcciÃ³n.

Este control agrega una barrera independiente de la configuraciÃ³n local del desarrollador. Sin embargo, su cobertura depende de los tipos de secretos y patrones habilitados, y no reemplaza la revisiÃ³n ni la rotaciÃ³n de credenciales.

## 7. Â¿QuÃ© secreto encontrarÃ­a primero un bot en un repositorio pÃºblico?

El secreto de pagos de R3 es un candidato especialmente probable: se encuentra en una rama que sigue existiendo y dentro de un archivo `.env.pasarela`, cuyo nombre y contenido sugieren configuraciÃ³n sensible.

Sin embargo, no es posible afirmar cuÃ¡l serÃ­a detectado primero por un bot real sin conocer el orden de rastreo, los patrones de detecciÃ³n y la fecha de publicaciÃ³n del repositorio. Los tres secretos son recuperables mediante la inspecciÃ³n correspondiente.

En particular:

- R1 aparece en el historial de commits.
- R2 puede recuperarse mediante el reflog y la inspecciÃ³n de objetos no alcanzables.
- R3 permanece en una rama distinta de `main`.

La conclusiÃ³n es que revisar solamente la rama principal o el estado actual de los archivos no es suficiente para evaluar la seguridad de un repositorio Git.

## 8. Conclusiones

La investigaciÃ³n permitiÃ³ demostrar tres formas diferentes de exposiciÃ³n de informaciÃ³n sensible:

1. Un secreto eliminado en un commit posterior continÃºa presente en el historial.
2. Un commit que deja de estar referenciado despuÃ©s de un reset puede seguir siendo recuperable.
3. Una rama abandonada puede conservar credenciales y cÃ³digo que no aparecen en la rama principal.

Los tres casos muestran que Git conserva informaciÃ³n mÃ¡s allÃ¡ del estado actual del directorio de trabajo. Por eso, la seguridad de un repositorio debe evaluarse inspeccionando su historial, sus referencias y sus objetos.

La medida prioritaria ante una filtraciÃ³n es revocar o rotar las credenciales. Luego se debe limpiar el historial, coordinar la actualizaciÃ³n de todas las copias y establecer mecanismos preventivos.

## 9. Evidencias adjuntas

La carpeta `evidencia/` contiene:

- `comandos.txt`: listado de los comandos utilizados durante la investigaciÃ³n.
- `status.png`: captura del estado final del laboratorio.
- `salidas/r1.txt`: salida del anÃ¡lisis del historial.
- `salidas/r2-reflog.txt`: registro de movimientos de referencias.
- `salidas/r2-show-stat.txt`: resumen del commit recuperado.
- `salidas/r2-show.txt`: contenido del commit recuperado.
- `salidas/r2-fsck.txt`: objetos no alcanzables identificados.
- `salidas/r3-log.txt`: historial de la rama investigada.
- `salidas/r3-show-stat.txt`: resumen del commit de la rama abandonada.
- `salidas/r3-show.txt`: contenido del commit de la rama abandonada.

La captura `status.png` muestra la ejecuciÃ³n de `./ctf status extra2` con los tres retos completados.
