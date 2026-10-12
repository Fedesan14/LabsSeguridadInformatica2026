# Generador del deck — Clase 05-06 (cruce a ofensiva)

Este deck (`docs/clase-05-06-cruce-ofensiva.pptx`) se genera por código con
[pptxgenjs](https://gitbrent.github.io/PptxGenJS/). Así se regenera sin partir
de cero: cambiás un dato, un color o una slide en `generar.js` y reconstruís.

## Regenerar

```bash
cd docs/presentaciones/clase-05-06
npm install        # una vez (baja pptxgenjs 4.0.1; node_modules va gitignoreado)
npm run build      # regenera docs/clase-05-06-cruce-ofensiva.pptx
```

Requiere **Node.js**. La salida se escribe en `docs/` (dos niveles arriba).

## Identidad visual

Paleta y tipografía replican la presentación HTML del práctico
(`docs/presentacion.html`): fondo `#0a0e12`, verde `#39d98a` (acento), cyan
`#4cc9f0`, ámbar `#f0b429` (flags), violeta `#b19cf0`. En el `.pptx` se usan
`Courier New` (mono) y `Calibri` (texto) por compatibilidad de render en
PowerPoint; si tenés IBM Plex instalado, cambialas en `generar.js`.

## Verificar antes de dar la clase

Abrilo y revisá que ninguna slide desborde. Si tenés las tools del skill de
oficina a mano, `validate.py` sobre el `.pptx` tiene que dar *All validations
PASSED*.
