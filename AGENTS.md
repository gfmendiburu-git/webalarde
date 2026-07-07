# Normas del proyecto

## Diseño visual

- La paleta principal del sitio debe limitarse a rojo, blanco y negro.
- Se pueden usar variaciones de opacidad o grises neutros solo cuando sean necesarias para legibilidad, bordes, fondos secundarios o estados interactivos.
- No introducir nuevos colores principales sin actualizar antes este archivo.
- Las imágenes fotográficas o ilustrativas pueden conservar su color original si aportan contexto visual y no sustituyen a la paleta principal de la interfaz.

## Buenas prácticas

- Mantener el sitio como HTML y CSS estático, fácil de publicar en GitHub Pages.
- Usar HTML semántico: `header`, `nav`, `main`, `section`, `article` y `footer` cuando corresponda.
- Separar el contenido por páginas cuando una sección tenga entidad propia.
- Reutilizar estilos compartidos en `styles.css` y evitar duplicación innecesaria.
- Mantener textos informativos, neutrales y fáciles de contrastar con fuentes oficiales.
- Comprobar el estado de Git antes de commitear y publicar cambios con mensajes de commit claros.
- No depender de symlinks para publicar archivos en GitHub Pages. Si las descargas viven fuera del repositorio, sincronizarlas antes con `scripts/sync-downloads.sh`.
- Para materiales de terceros, conservar fuente, licencia y atribución. No incorporar imágenes externas al sitio sin revisar permisos y metadatos.
