# Auditoria de derechos para imagenes recortadas

Documento de trabajo para decidir si una imagen encontrada dentro de la documentacion local puede recortarse y publicarse en la web.

No sustituye a asesoramiento juridico. Su funcion es aplicar un criterio prudente, dejar trazabilidad y evitar publicar imagenes sin fuente, licencia o permiso suficiente.

## Criterio base

- La web es no comercial, pero eso no basta por si solo: hace falta dominio publico, licencia reutilizable o permiso.
- Mantener siempre fuente, fecha, publicacion, pagina y procedencia del archivo.
- Si la imagen procede de una fotografia identificable, registrar tambien autor o fondo cuando aparezca.
- Si la fuente tiene condiciones de uso propias, prevalece la condicion mas restrictiva.
- No recortar fotografias modernas de prensa, revistas o programas recientes sin permiso expreso.
- Si hay duda razonable sobre autor, titularidad o licencia, marcar como `pedir permiso` o `no publicar`.

## Marco practico

- Obras de autor: en Espana el plazo general es vida del autor y 70 anos tras su muerte; para autores fallecidos antes de 1987 hay reglas transitorias que pueden ampliar el plazo.
- Meras fotografias: la Ley de Propiedad Intelectual espanola reconoce un derecho especifico de 25 anos desde el 1 de enero siguiente a la realizacion de la fotografia.
- Ediciones y digitalizaciones: aunque el contenido antiguo pueda estar en dominio publico, una institucion o portal puede imponer condiciones de reutilizacion sobre copias, fondos privados, imagenes en alta resolucion o colecciones concretas.
- Prensa y revistas modernas: ademas del fotografo puede haber derechos del medio, agencia, editor o archivo. Evitar recortes graficos sin autorizacion.

Referencias legales de base:

- Ley de Propiedad Intelectual, art. 26: duracion general de los derechos de explotacion.
- Ley de Propiedad Intelectual, art. 41: uso de obras en dominio publico respetando autoria e integridad.
- Ley de Propiedad Intelectual, art. 128: proteccion de meras fotografias durante 25 anos.
- Ley de Propiedad Intelectual, arts. 129-130: determinadas producciones editoriales y plazo de 25 anos.

## Estados

- `usable`: se puede publicar con atribucion y condiciones indicadas.
- `usable-con-cautela`: probable dominio publico o licencia suficiente, pero conviene atribuir de forma completa y conservar captura/ficha de procedencia.
- `pedir-permiso`: interesante, pero no hay licencia clara o la fuente es moderna/protegida.
- `solo-consulta`: util para documentacion interna, no para publicar imagen.
- `descartar`: fuera de alcance, derechos incompatibles o falta grave de trazabilidad.

## Clasificacion inicial por carpeta

| Carpeta | Volumen aprox. | Estado por defecto | Criterio |
| --- | ---: | --- | --- |
| `Alarde de San Marcial en Irún: origen y detalles - Serapio Múgica - 1901` | 36 imagenes | `usable-con-cautela` | Libro de 1901. El texto esta fuera de plazo con alta probabilidad. Las imagenes son escaneos de paginas; publicar recortes pequenos o paginas como fuente historica parece razonable con cita completa al Archivo Municipal de Irun. |
| `Album gráfico descriptivo del País Vascongado años de 1914-1915 tomo de Guipúzcoa - Creative Commons CC BY-SA 4.0` | 1 PDF | `usable` | La propia carpeta indica CC BY-SA 4.0. Los recortes derivados deben acreditar autor/fuente si constan y mantener la misma licencia para la adaptacion. |
| `Programas de fiestas` | 265 PDF | `usable-con-cautela` para material antiguo; `pedir-permiso` desde posguerra reciente | Los programas municipales antiguos pueden aportar imagenes utiles, pero muchos incluyen fotografias, anuncios, dibujos o portadas con autor desconocido. Antes de publicar cada recorte hay que registrar ano, pagina y tipo de imagen. En programas modernos, pedir permiso salvo licencia clara. |
| `El Alarde` | 4 PDF | `usable-con-cautela` | Periodico de 1919 procedente del Archivo Municipal de Irun. Util para facsimiles o recortes historicos con cita completa; revisar cada fotografia/ilustracion si aparece autor. |
| Prensa antigua anterior a 1936: `La Voz de Guipuzcoa`, `La Libertad`, `La informacion`, `El eco de Irun`, `El Bidasoa`, `La frontera`, `Uranzu`, `Easo`, `El Dia`, `Urumea` | 237 PDF aprox. | `usable-con-cautela` | Para recortes de pagina, cabeceras, anuncios o fotografias periodisticas antiguas, el riesgo suele ser bajo si se cita medio, fecha, pagina y archivo. Aun asi, si aparece fotografia de autor o estudio conocido, registrar ese dato. |
| `Unidad` y `El Diario Vasco` de 1937-1943 | 9 PDF aprox. | `pedir-permiso` salvo recorte muy justificado | Son prensa historica, pero ya dentro de un periodo mas delicado por autores/fotografos y derechos editoriales. Usar preferentemente como fuente textual; para imagenes, pedir permiso o usar solo miniaturas documentales muy justificadas. |
| `El Diario Vasco` moderno y recortes de 1997/2008 | varios | `pedir-permiso` | No publicar fotografias ni recortes graficos sin permiso del medio o titular correspondiente. |
| `Bidasoan` | 101 PDF | `pedir-permiso` | Revistas modernas con fotografias y articulos de autores identificables. Se pueden usar como fuente textual citada, pero no recortar imagenes para publicar sin permiso. |
| `El Irunes` | 75 PDF | `pedir-permiso` | Revista moderna/local con fotografias probablemente protegidas. Usar como fuente textual; imagenes solo con permiso o licencia clara. |
| `Ecos del Jaizkibel` | 5 PDF conservados | `usable-con-cautela` | Publicacion antigua. Revisar pagina concreta y procedencia de descarga; citar Euskariana o archivo correspondiente si procede. |
| `El Bidasoa Mexicano` | 12 PDF | `pedir-permiso` | Publicacion de 1951-1961 y estudio moderno. Usar como fuente textual; imagenes solo con permiso o si se demuestra dominio publico/licencia. |
| `Recortes del periodico Egin` | 8 TIFF conservados | `pedir-permiso` | Recortes de 1980-1982. No publicar imagenes ni recortes graficos sin permiso. |
| `Novedades revista semanal ilustrada` | 6 PDF | `revisar-caso-a-caso` | Revista ilustrada: puede contener fotografias de agencia o autor. Si son numeros muy antiguos, valorar fecha, autor y procedencia antes de usar. |
| `Txistulari`, `Ordenanzas`, `El buen combate semanario catolico` | pocos archivos | `revisar-caso-a-caso` | Depende de fecha, autor, procedencia y tipo de imagen. |

## Procedimiento para cada candidato

1. Guardar ruta exacta del documento y pagina.
2. Exportar una miniatura de trabajo en `/tmp` para revisar el recorte.
3. Identificar si es fotografia, dibujo, anuncio, portada, mapa, partitura o facsimil de texto.
4. Buscar en la propia pagina pie de foto, autor, estudio, agencia, fondo o archivo.
5. Clasificar con uno de los estados anteriores.
6. Si se publica, crear copia optimizada en `assets/` y registrar atribucion visible o cercana.
7. Mantener el original intacto en `Descargas`; no modificarlo ni moverlo.

## Plantilla de registro

| ID | Documento | Pagina | Imagen | Fecha | Autor/fondo | Procedencia | Estado | Atribucion propuesta | Notas |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| pendiente | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente | pendiente |

## Formatos de atribucion sugeridos

- Archivo Municipal de Irun: `Archivo Municipal de Irun · [publicacion/documento] · [fecha] · p. [pagina]`.
- Euskariana: `Euskariana / [institucion si consta] · [publicacion] · [fecha] · p. [pagina]`.
- CC BY-SA 4.0: `[titulo/autor si consta] · [fuente] · CC BY-SA 4.0`.
- Prensa antigua sin autor visible: `[medio] · [fecha] · p. [pagina] · procedencia: [archivo/portal]`.

## Pendientes

- Crear una tabla de candidatos concretos cuando se localicen imagenes interesantes.
- Revisar condiciones especificas del Archivo Municipal de Irun para recortes procedentes de programas municipales y hemeroteca.
- Revisar condiciones especificas de Euskariana para cada publicacion descargada desde ese portal.
- Confirmar por correo cualquier imagen moderna procedente de revistas, prensa reciente o publicaciones con autores identificados.
