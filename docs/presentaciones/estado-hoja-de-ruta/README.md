# Generador del deck — Estado + hoja de ruta

Deck para mostrar en clase: dónde estamos, qué falta y el calendario con fechas.
Se genera por código (pptxgenjs), igual que el deck de la clase 05-06.

## Regenerar

```bash
cd docs/presentaciones/estado-hoja-de-ruta
npm install        # una vez (pptxgenjs 4.0.1; node_modules va gitignoreado)
npm run build      # regenera docs/estado-y-hoja-de-ruta.pptx
```

## Actualizar el cronograma

Las fechas y la asignación de labs a cada viernes están en el array `cal` de
`generar.js` (slide 5) y en el deadline de la slide 6. Editá ahí, reconstruí, y
verificá que cada fecha caiga **viernes** antes de darlo. Identidad visual =
`docs/presentacion.html`.
