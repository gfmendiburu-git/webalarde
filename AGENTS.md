# Normas del proyecto

## Diseño visual

- La paleta principal del sitio debe limitarse a rojo, blanco y negro.
- Se pueden usar variaciones de opacidad o grises neutros solo cuando sean necesarias para legibilidad, bordes, fondos secundarios o estados interactivos.
- No introducir nuevos colores principales sin actualizar antes este archivo.
- Las imágenes fotográficas o ilustrativas pueden conservar su color original si aportan contexto visual y no sustituyen a la paleta principal de la interfaz.
- Usar `assets/logo-san-marcial-dark.svg` en la web normal sobre fondos claros y `assets/logo-san-marcial-light.svg` sobre fondos oscuros o en la pantalla de mantenimiento.

## Buenas prácticas

- Mantener el sitio como HTML y CSS estático, fácil de publicar en GitHub Pages.
- Usar HTML semántico: `header`, `nav`, `main`, `section`, `article` y `footer` cuando corresponda.
- Separar el contenido por páginas cuando una sección tenga entidad propia.
- Reutilizar estilos compartidos en `styles.css` y evitar duplicación innecesaria.
- Mantener textos informativos, neutrales y fáciles de contrastar con fuentes oficiales.
- Redactar las páginas de contenido con estilo narrativo y lectura natural, integrando los datos dentro del relato en lugar de acumular bloques sueltos de información. Cuando haya que citar, usar llamadas numeradas y notas al pie al final de la página, evitando interrumpir cada párrafo con textos largos de fuente.
- El alcance editorial del sitio es el Alarde tradicional de San Marcial de Irun. No incorporar ni desarrollar contenidos del alarde público; cuando sea imprescindible contextualizar el conflicto contemporáneo, hacerlo de forma breve, factual y sin convertirlo en eje de la página.
- Comprobar el estado de Git antes de commitear y publicar cambios con mensajes de commit claros.
- No depender de symlinks para publicar archivos en GitHub Pages. Si las descargas viven fuera del repositorio, sincronizarlas antes con `scripts/sync-downloads.sh`.
- Para materiales de terceros, conservar fuente, licencia y atribución. No incorporar imágenes externas al sitio sin revisar permisos y metadatos.
- Antes de publicar recortes de imágenes procedentes de documentación descargada, revisar `docs/derechos-imagenes.md` y registrar fuente, página, autor/fondo si consta, estado de derechos y atribución propuesta.
- Mantener intactas las imágenes originales de archivo fuera del sitio publicado. Para GitHub Pages, publicar copias optimizadas y regenerables junto con sus metadatos.
- Cuando se incorpore información procedente de documentos históricos, archivos municipales, prensa antigua, libros digitalizados u OCR, citar la fuente concreta junto al dato añadido.
- Cuando una página acumule muchas fuentes consultadas, agrupar la bibliografía por publicación, archivo, normativa o sitio web para que la lista sea legible sin perder trazabilidad.
- Mantener la evolución general de la estructura del Alarde dentro de Historia. La página de Composición debe funcionar como consulta práctica de unidades, compañías y fichas, evitando duplicar allí el relato histórico general. Los uniformes deben explicarse en la ficha de cada unidad, porque dependen de su función concreta.
- En las páginas individuales de compañías y unidades, redactar la historia en estilo narrativo natural, no como una lista de datos sueltos. Integrar cronología, mandos, cantineras, cambios de nombre, anécdotas, uniforme y dudas documentales dentro del relato de cada unidad, manteniendo notas y fuentes concretas cuando el dato lo requiera.
- Al revisar fuentes históricas, buscar y conservar tambien curiosidades documentadas que enriquezcan el relato: debates terminologicos, grafias antiguas, nombres populares, cambios de costumbre, detalles internos de unidades, anecdotas organizativas y pequenas variaciones de uniforme, mando, musica o ritual. Integrarlas solo cuando esten apoyadas por fuente concreta y aporten contexto al Alarde.
- Al procesar programas de fiestas, no convertir cada programa en una crónica anual de horarios, recorridos o actos municipales. Extraer solo datos relevantes para el Alarde: mando, composición, unidades, cantineras, música propia, actos rituales, cambios organizativos o evolución documentada. Omitir recorridos repetidos, conciertos, toros, concursos, trenes, horarios y actos generales salvo que expliquen directamente el Alarde.
- En la página de música, incluir solo música propia del Alarde o usada directamente en sus actos: dianas, himnos, marchas, toques, retretas, tamborrada, banda, pífanos y tambores vinculados al ceremonial. No incorporar repertorio festivo local, conciertos, concursos musicales ni obras sobre San Marcial si no forman parte del Alarde.
- Cuando una fuente aporte capitanes o mandos de una compañía, registrar el dato en `data/capitanes-companias.json` con años, fuente concreta, notas y estado de revisión si procede. La información debe mostrarse dentro de la ficha de la compañía correspondiente, no en una página independiente de capitanes.
- Mantener actualizado `docs/fuentes-examinadas.md` cada vez que se revise una publicación, documento histórico, búsqueda fotográfica o fuente web. Registrar fuente, archivo local o URL, estado, páginas afectadas, criterio aplicado y commit cuando sea posible.
- Mantener actualizado `docs/indice-articulos-sanmarcialeros.md` cada vez que se revise documentación nueva o se detecte un artículo, crónica, entrevista, página gráfica o pasaje útil. Este índice debe indicar publicación, fecha o número, título o descripción del artículo, temas, uso en la web y localización o URL para poder volver rápidamente a la fuente sin releer todo el corpus. Usar `docs/indice-articulos-sanmarcialeros.csv` como índice amplio de pasajes localizados y `docs/rastreo-documentos-articulos.csv` como control de PDFs rastreados, texto extraído, pasajes detectados y documentos pendientes de OCR.
- Mantener actualizado `docs/catalogo-documental-sanmarcialero.csv` como catálogo maestro e índice real del corpus documental. Debe contener una fila por documento de `/home/gaizka/Alarde`, incluso cuando el OCR no haya localizado pasajes. Regenerarlo con `python3 scripts/build-document-catalog.py` siempre que cambien `docs/indice-articulos-sanmarcialeros.csv`, `docs/rastreo-documentos-articulos.csv` o el índice curado de `docs/indice-articulos-sanmarcialeros.md`.
- Para relecturas minuciosas del archivo documental completo, usar `docs/auditoria-documental.md` como matriz de control. No dar por agotada una fuente solo por haber hecho búsquedas OCR: revisar también pies de foto, tablas, notas sueltas, variantes de nombres, mandos, cantineras, compañías históricas y curiosidades documentadas.
- Al revisar nuevas fuentes con datos de cantineras, omitir datos que solo repitan una cantinera ya confirmada en `data/cantineras.json`. Integrar solo cantineras nuevas, correcciones claras, datos pendientes de confirmar o fuentes que resuelvan una duda existente. No modificar una cantinera ya confirmada si una fuente nueva no coincide con ella; en ese caso, avisar al usuario indicando la discrepancia, la fuente nueva y el dato actualmente confirmado.
- Siempre que se cambien datos de cantineras por revisión de documentos, OCR, Excel, fuentes web o correcciones manuales, regenerar `/home/gaizka/Descargas/CANTINERAS_actualizado.xlsx` desde `data/cantineras.json` para que el usuario trabaje sobre una exportación sincronizada.
