# Informe — Laboratorio 04 · Marcos normativos y gestión

**Grupo:** 03 · **Integrantes:** *(nombre — usuario GitHub)*

| Nombre y apellido | Legajo | Usuario de GitHub |
|---|---|---|
| Federico Sánchez | `13614` | @Fedesan14 |
| Elian Enria | `13245` | @elian-enria-id |
| Efraín Host | `18273` | @hostefrain |
| Lohana Rumis | `14646` | @Lohana-Rumis |

### Distribución del trabajo

En este laboratorio no se repartieron componentes: los cuatro integrantes
trabajaron juntos todas las partes (Parte A, Parte B, código y mini-research)
y las revisaron en conjunto. Cada commit lleva a los cuatro integrantes, como
autor o como coautores (`Co-authored-by`).

**Marco elegido:** NIST Cybersecurity Framework 2.0 · **Mini-research:** tema
**D** — análisis de riesgo cuantitativo vs cualitativo.

---

## 0. Declaración de uso de IA

**¿El grupo usó asistentes de IA en este trabajo?** **Sí.**

| Herramienta | Para qué se usó | Qué partes del entregable afectó | Cómo se verificó que lo devuelto era correcto |
|---|---|---|---|
| Claude Code (Anthropic, modelo Opus 5.5) | Borrador de las tres funciones de `riesgo.py`, del test, del mapeo a NIST CSF 2.0 y de la redacción del informe y del research | `src/riesgo.py`; `test_riesgo.py`; `riesgos.json`; `informe.md`; `research.md` | El código se corrió contra `src/verificar.py` de la cátedra (3/3 OK) y contra `test_riesgo.py`, cuyos valores esperados son los ejemplos del enunciado y cuentas hechas a mano, no salidas del propio código. Cada identificador de NIST CSF citado (p. ej. `PR.AA-03`, `PR.DS-11`, `ID.IM-04`) se buscó en el documento oficial NIST CSWP 29 para descartar controles inventados. Las cifras de SLE/ARO son supuestos del grupo y se revisaron una por una |

**Declaración.** El grupo declara que todo el contenido entregado fue revisado
y comprendido por los cuatro integrantes, y que la
herramienta de IA se usó como apoyo y no como reemplazo del trabajo propio.

---

## 1. Parte A — Marco aplicado (marco elegido; 5 debilidades→controles; respuesta al riesgo)

**Escenario.** PhantomCorp guarda datos de clientes (nombres, DNI, tarjetas),
tiene un servidor web público, empleados con acceso remoto y backups en un
disco en la oficina. No tiene MFA, ni política de contraseñas, ni plan de
respuesta a incidentes.

### A.1 — Qué marco elegimos y por qué

Elegimos el **NIST Cybersecurity Framework (CSF) 2.0** (NIST CSWP 29, febrero
de 2024) [1].

- **Es un marco de resultados, no de certificación.** ISO/IEC 27001 exige
  montar un SGSI completo (alcance, declaración de aplicabilidad, auditoría) [2].
  PhantomCorp hoy no tiene ni lo mínimo; lo que necesita primero es saber *qué
  le falta* y en qué orden. El CSF está pensado justamente para describir un
  perfil actual, un perfil objetivo y la brecha entre ambos.
- **Sus seis funciones ordenan el diagnóstico.** Las tres carencias que nombra
  el enunciado caen en funciones distintas: la falta de política es **Govern**,
  la falta de MFA es **Protect** y la falta de plan de incidentes es
  **Identify/Respond**. Eso hace visible que el problema no es sólo técnico.
- **Es gratuito y tiene referencias cruzadas** a otros catálogos (incluido
  ISO/IEC 27001), así que si más adelante PhantomCorp quisiera certificar, el
  trabajo hecho con el CSF no se pierde.

Usamos la versión **2.0** y no la 1.1 porque agrega la función **Govern
(GV)**, donde vive la política de contraseñas, y porque reorganiza las
categorías de Protect (por ejemplo `PR.AA`, que reemplaza a `PR.AC`).

### A.2 — Cinco debilidades mapeadas al marco

| # | Debilidad del escenario | Función | Categoría / subcategoría CSF 2.0 | Qué pide el resultado |
|---|---|---|---|---|
| 1 | Servidor web **público** sin gestión declarada de parches ni monitoreo | Protect / Detect | `PR.PS-02` (el software se mantiene, reemplaza o elimina según el riesgo), `PR.IR-01` (redes y entornos protegidos de acceso lógico no autorizado), `DE.CM-01` (se monitorean las redes y servicios de red) | Parchear, separar el servidor web de donde están los datos, y enterarse si alguien lo ataca |
| 2 | Se **almacenan** tarjetas y DNI de clientes | Identify / Protect | `ID.AM-07` (se mantienen inventarios de datos y de tipos de datos designados), `PR.DS-01` (se protege la confidencialidad, integridad y disponibilidad de los datos en reposo) | Saber qué datos sensibles hay y dónde; protegerlos en reposo |
| 3 | Acceso remoto **sin MFA** y **sin política de contraseñas** | Govern / Protect | `GV.PO-01` (se establece una política de gestión del riesgo de ciberseguridad), `PR.AA-01` (se gestionan identidades y credenciales de usuarios autorizados), `PR.AA-03` (se autentican usuarios, servicios y hardware) | Una política escrita y aprobada, y autenticación fuerte para entrar desde afuera |
| 4 | Backups en **un disco en la oficina** | Protect / Recover | `PR.DS-11` (se crean, protegen, mantienen y prueban backups de los datos), `PR.IR-02` (los activos se protegen de amenazas ambientales), `RC.RP-03` (se verifica la integridad de backups antes de restaurar) | Copias fuera del alcance de un incendio, un robo o un ransomware, y restauraciones probadas |
| 5 | **No hay plan** de respuesta a incidentes | Identify / Respond / Recover | `ID.IM-04` (se establecen, comunican, mantienen y mejoran planes de respuesta a incidentes), `RS.MA-01` (el plan se ejecuta en coordinación con terceros una vez declarado el incidente), `RC.RP-01` (se ejecuta la parte de recuperación del plan) | Un plan escrito, con roles y contactos, que se pueda ejecutar el día del incidente |

Observación sobre el mapeo: la debilidad 5 aparece en **Identify** y no sólo en
Respond. En el CSF 2.0 el plan se *crea y mejora* en `ID.IM` (mejora continua),
y se *ejecuta* en `RS.MA`; sin lo primero, lo segundo no tiene nada que
ejecutar.

### A.3 — Respuesta al riesgo para cada debilidad

| # | Debilidad | Respuesta | Justificación |
|---|---|---|---|
| 1 | Servidor web público | **Mitigar** (y **transferir** el residual) | No se puede *evitar*: el sitio es el canal con los clientes. Parches, segmentación y monitoreo bajan la probabilidad a un costo razonable (ver B.2). Lo que quede —un 0-day o un error propio— es poco probable pero muy caro, y ese residual se transfiere con un ciberseguro |
| 2 | Tarjetas y DNI almacenados | **Evitar** (tarjetas) · **Mitigar** (DNI) | Para cobrar no hace falta guardar el número de tarjeta: un procesador de pagos certificado PCI DSS [3] devuelve un *token* y la tarjeta nunca toca los servidores de PhantomCorp. Se elimina la actividad que genera el riesgo, que es la definición de evitar. El DNI sí puede hacer falta (facturación, identificación), así que ahí se mitiga: minimizar qué se guarda y cifrarlo en reposo, como exige además la Ley 25.326, art. 9 [4] |
| 3 | Acceso remoto sin MFA ni política | **Mitigar** | Es la debilidad con mejor relación costo/beneficio del escenario: MFA en la VPN o el acceso remoto cuesta poco y neutraliza el robo de contraseñas, el vector más común contra accesos remotos. *Aceptar* no es defendible (ALE de $30k/año, ver B.1) y *evitar* sería prohibir el trabajo remoto, que es parte de la operación. La política sigue NIST SP 800-63B [5]: largo mínimo, lista de contraseñas prohibidas y sin rotación forzada periódica |
| 4 | Backup en un solo disco en la oficina | **Mitigar** | Un único disco en el mismo lugar que los servidores comparte el destino de lo que respalda: el incendio, el robo o el ransomware que tira abajo el servidor se lleva también el backup. La regla 3-2-1 con una copia offline o inmutable fuera de la oficina [6] es barata frente a lo que protege, y además reduce el SLE del riesgo de ransomware |
| 5 | Sin plan de respuesta a incidentes | **Mitigar** (y **transferir** parte) | Escribir el plan es casi sólo horas de trabajo. Lo que PhantomCorp no tiene es capacidad forense propia: eso se **transfiere** contratando un servicio de respuesta a incidentes (o un seguro que lo incluya), de modo que el plan diga a quién llamar |

Las respuestas no son "mitigar todo": la 2 es **evitar**, y la 1 y la 5
**transfieren** una parte. El ejemplo de **aceptar** está en B.3.

---

## 2. Parte B — Riesgo cuantitativo (ranking por ALE; ROI del control #1; un riesgo a aceptar/transferir)

### Implementación

Las tres funciones de [`src/riesgo.py`](src/riesgo.py) son una línea de
cálculo cada una:

- `ale(sle, aro)` → `sle * aro`.
- `roi_control(antes, despues, costo)` → `(antes - despues - costo) / costo`.
  Rechaza `costo <= 0` con `ValueError`, porque el valor viene de la línea de
  comandos y de otro modo terminaría en una división por cero sin mensaje.
- `priorizar(riesgos)` → `sorted(...)` por ALE descendente sobre **copias** de
  los dicts, para no mutar el JSON de quien llama. `sorted` es estable: dos
  riesgos con igual ALE conservan el orden del archivo.

Verificación:

```
$ python3 src/verificar.py
  ✓ ale()
  ✓ roi_control()
  ✓ priorizar() ordena por ALE
3 OK · 0 a revisar · 0 sin implementar

$ python3 test_riesgo.py
OK: ale, roi_control, priorizar y riesgos.json verificados
```

`test_riesgo.py` contrasta contra los ejemplos que publica el enunciado
(`20000.00`, `0.875`) y contra cuentas hechas a mano con las cifras de
`riesgos.json`; además corre la CLI como proceso aparte para comprobar la
salida exacta.

### Supuestos de las cifras

Las cifras son **estimaciones del grupo** en dólares, para una PyME con algunos
miles de clientes. No son datos medidos; justamente por eso se explicitan:

| Riesgo | SLE | Cómo se estimó el SLE | ARO | Por qué ese ARO |
|---|---:|---|---:|---|
| Fuga de tarjetas y DNI vía servidor web | 120 000 | Forense, notificación a clientes, reemisión de tarjetas, sanciones de las marcas de tarjeta, pérdida de clientes | 0,3 | Servidor expuesto a Internet, sin gestión de parches declarada: un incidente cada ~3 años |
| Intrusión por acceso remoto sin MFA | 60 000 | Forense, contención, horas de trabajo perdidas, eventual acceso a datos internos | 0,5 | Credenciales filtradas o *phishing* son frecuentes; sin MFA una sola contraseña alcanza |
| Ransomware sobre servidores y backup | 80 000 | Días sin operar, reconstrucción, datos perdidos (el backup está en la misma red) | 0,25 | Uno cada ~4 años |
| Pérdida del disco de backup (robo/incendio) | 30 000 | Reconstruir lo que no estaba en otro lado | 0,05 | Evento físico raro: uno cada ~20 años |
| Caída del sitio por DDoS | 2 500 | Un día sin ventas web y horas de soporte | 0,5 | Ataques oportunistas; uno cada ~2 años |

### B.1 — Ranking por ALE

```
$ python3 src/riesgo.py priorizar --archivo riesgos.json
      36000.00  Fuga de tarjetas y DNI por explotacion del servidor web publico
      30000.00  Intrusion por acceso remoto sin MFA (credenciales robadas)
      20000.00  Ransomware que cifra los servidores y el disco de backup
       1500.00  Perdida del disco de backup por robo o incendio en la oficina
       1250.00  Caida del sitio web por DDoS
```

**¿Coincide con la intuición?** En lo grueso, sí: los dos primeros son los que
cualquiera señalaría mirando el escenario (tarjetas guardadas detrás de un
servidor público, y acceso remoto con sólo una contraseña). Los dos últimos
quedan muy abajo, como era de esperar.

**Dónde no coincide:**

1. **Ransomware queda tercero.** La intuición lo pone primero porque es el
   incidente "de moda" y el más visible. El número dice que, con estos
   supuestos, una fuga de tarjetas cuesta más por año aunque no paralice la
   empresa. Lo que el ranking no muestra es que el ransomware **suele entrar por
   el riesgo #2** (acceso remoto sin MFA): mitigar el #2 baja también el ARO del
   #3. ALE trata los riesgos como independientes y no lo son.
2. **La pérdida del backup queda casi última (ALE $1 500), y eso engaña.**
   Aislado, perder el disco es barato. Pero ese disco es lo que hace que el
   ransomware cueste $80k y no menos: si el backup estuviera fuera de la
   oficina, el SLE del #3 bajaría mucho. El riesgo "barato" es el que agrava a
   otro "caro". Por eso en A.3 lo mitigamos igual.
3. **ALE promedia y esconde la cola.** Un riesgo de SLE $120 000 con ARO 0,3 y
   otro de SLE $36 000 con ARO 1 tienen el mismo ALE, pero el primero puede
   fundir a una PyME en un solo evento. El ranking dice qué cuesta más **en
   promedio**, no qué puede matar a la empresa.

### B.2 — Control para el riesgo #1 y su ROI

**Riesgo #1:** fuga de tarjetas y DNI por explotación del servidor web.
ALE antes = **$36 000/año**.

**Control propuesto: tokenización de pagos** — cobrar a través de un
procesador certificado PCI DSS y dejar de almacenar números de tarjeta [3].

- **Costo anual estimado:** $6 000 (comisiones adicionales del procesador e
  integración amortizada).
- **Efecto:** no cambia la *probabilidad* de que vulneren el servidor (ARO
  sigue en 0,3), pero sí lo que se pierde si pasa. Sin tarjetas, el SLE baja de
  $120 000 a ~$40 000: quedan nombres y DNI, que siguen requiriendo forense y
  notificación.

```
$ python3 src/riesgo.py ale --sle 40000 --aro 0.3
12000.00
$ python3 src/riesgo.py roi --antes 36000 --despues 12000 --costo 6000
3.000
```

ROI = (36 000 − 12 000 − 6 000) / 6 000 = **3,0** → cada dólar invertido
evita tres de pérdida neta. **Conviene.**

**Comparación con la alternativa obvia.** Lo primero que se le ocurre a uno es
"poner un WAF". Lo calculamos con los mismos supuestos: WAF + gestión de
parches, $12 000/año, que bajaría el ARO de 0,3 a 0,08 (SLE sin cambios):

| Control | Costo/año | ALE después | Pérdida evitada | Beneficio neto | ROI |
|---|---:|---:|---:|---:|---:|
| Tokenización | 6 000 | 12 000 | 24 000 | **18 000** | **3,000** |
| WAF + parches | 12 000 | 9 600 | 26 400 | 14 400 | 1,200 |
| Ambos | 18 000 | 3 200 | 32 800 | 14 800 | 0,822 |

El WAF evita *más* pérdida, pero cuesta el doble. Y sumar el WAF **encima** de
la tokenización evita $8 800 más por $12 000 más: ese incremento tiene ROI
negativo. La decisión con estos números es **tokenizar primero**; el WAF se
justifica recién si el servidor tiene otro valor que proteger (por ejemplo, si
el riesgo de DDoS o de defacement crece). Esto también confirma que la
respuesta correcta para las tarjetas es **evitar** (A.3, #2), no mitigar.

### B.3 — Un riesgo para aceptar

**Riesgo:** caída del sitio web por DDoS. ALE = **$1 250/año**.

Un servicio dedicado de mitigación de DDoS costaría, estimado, $4 800/año y
dejaría un ALE residual de ~$250:

```
$ python3 src/riesgo.py roi --antes 1250 --despues 250 --costo 4800
-0.792
```

ROI = (1 250 − 250 − 4 800) / 4 800 = **−0,79**: el control cuesta casi
cuatro veces lo que evita. Además el impacto es acotado (un día sin ventas
web; ningún dato se pierde ni se filtra) y no agrava a otros riesgos. La
respuesta correcta es **aceptar**, dejándolo documentado y revisándolo si
cambian los supuestos (por ejemplo, si la web pasa a ser el canal principal de
ventas y el SLE sube).

**Y uno para transferir:** el residual del riesgo #1 después de tokenizar
(ALE $12 000, SLE $40 000) es raro pero caro para una PyME en un solo evento.
Ese residual —forense, notificación, defensa legal— es lo que cubre un
**ciberseguro**: se paga una prima conocida a cambio de no absorber un golpe
de $40k de una vez. No mitiga la fuga; traslada su costo.

### Referencias

[1] NIST, *The NIST Cybersecurity Framework (CSF) 2.0*, NIST CSWP 29, feb. 2024. https://doi.org/10.6028/NIST.CSWP.29
[2] ISO/IEC 27001:2022, *Information security, cybersecurity and privacy protection — Information security management systems — Requirements*.
[3] PCI Security Standards Council, *PCI DSS v4.0*, Requisito 3 (protección de datos de cuenta almacenados). https://www.pcisecuritystandards.org/
[4] Ley 25.326 de Protección de los Datos Personales (Argentina), art. 9 — Seguridad de los datos.
[5] NIST SP 800-63B, *Digital Identity Guidelines: Authentication and Lifecycle Management*. https://pages.nist.gov/800-63-3/sp800-63b.html
[6] CISA, *#StopRansomware Guide* (recomendación de backups offline, cifrados y probados). https://www.cisa.gov/stopransomware/ransomware-guide

---

## 3. Anexo — tu riesgos.json

Archivo: [`riesgos.json`](riesgos.json)

```json
[
  {"nombre": "Fuga de tarjetas y DNI por explotacion del servidor web publico", "sle": 120000, "aro": 0.3},
  {"nombre": "Intrusion por acceso remoto sin MFA (credenciales robadas)", "sle": 60000, "aro": 0.5},
  {"nombre": "Ransomware que cifra los servidores y el disco de backup", "sle": 80000, "aro": 0.25},
  {"nombre": "Perdida del disco de backup por robo o incendio en la oficina", "sle": 30000, "aro": 0.05},
  {"nombre": "Caida del sitio web por DDoS", "sle": 2500, "aro": 0.5}
]
```
