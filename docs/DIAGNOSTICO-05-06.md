# Diagnóstico — cruce a ofensiva (clase 05-06)

> No es una nota. Es un **espejo de 5 minutos**: te dice qué te quedó de los
> fundamentos (labs 01-04) y si tu entorno está listo para empezar a atacar.
> Nadie te mira el resultado para bocharte — te lo mirás **vos** para saber
> dónde estás parado antes de que arranque lo bueno.

## Por qué, justo ahora

Venís del **bloque 1** (código: CIA, hashing, cripto, auth, riesgo). Hoy
empieza el **bloque 2**: dejás de escribir código y empezás a **atacar**
PhantomCorp con herramientas reales. Ese salto tiene un requisito que no se
negocia: **si no entendiste los fundamentos, lo ofensivo se te hace humo.** Un
puerto abierto no te dice nada si no sabés qué es un servicio; un `.git`
expuesto no te alarma si no entendés integridad.

Por eso, antes de tirar el primer `nmap`, 5 minutos de espejo.

## Cómo se corre

```bash
cp docs/diagnostico-respuestas.txt mi-diagnostico.txt   # tu copia
# editá mi-diagnostico.txt con tus respuestas
python3 bin/diagnostico.py mi-diagnostico.txt           # feedback instantáneo
```

Son **11 preguntas**:

- **Bloque A (8)** — conceptos de los labs 01-04. Respondés una letra. Si no te
  sale alguna, no adivines: andá a [`RESUMEN-TEORICO.md`](RESUMEN-TEORICO.md) y
  repasá ESE tema.
- **Bloque B (3)** — se contestan **operando el lab 05**. Levantás el entorno,
  tirás un par de comandos, y leés la salida. Si no podés levantarlo, dejalas
  vacías: **eso también es el diagnóstico** (tenés un problema de setup que hay
  que resolver antes de seguir).

```bash
./ctf lab 05        # levanta el entorno del lab 05
make shell          # entrás a la consola del atacante (todas las tools adentro)
```

## Qué te va a decir

Al final te tira un veredicto y una línea `RESULTADO`:

| Estado | Qué significa | Qué hacés |
|---|---|---|
| **LISTO** | Fundamentos sólidos + entorno operativo | A romper PhantomCorp, sin red. |
| **CASI** | 1-2 huecos de concepto | Repasás el tema puntual que marcaste ✗ y seguís. |
| **REPASAR** | Menos de la mitad de fundamentos | Prioridad: labs 01-04 antes de avanzar. |
| **ENTORNO** | No pudiste con el Bloque B | Resolvés Docker/setup PRIMERO. Todo el bloque corre sobre eso. |

**Pegá la línea `RESULTADO` en tu entrega.** Con eso el docente ve de un vistazo
cómo llega el curso y ajusta la clase. No es delación: es que nadie quede atrás
sin que se note.

## Las respuestas van hasheadas

Igual que las flags: el script sabe si acertaste, pero la respuesta correcta **no
está en claro** en ningún archivo que vos tengas. Nada de espiar el `.py`. El
único que gana si te hacés trampa en un espejo sos... nadie. Es para vos.
