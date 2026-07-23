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
| `Bidasoan` | 101 PDF | `pedir-permiso` | Revistas modernas con fotografias, articulos firmados y posibles derechos editoriales. Usar como fuente textual citada; no recortar imagenes sin permiso. |
| `Easo` | 2 PDF | `usable-con-cautela` | Prensa antigua de 1932. Puede usarse para recortes documentales si se cita medio, fecha, pagina y procedencia. Revisar fotografia concreta si aparece autor o agencia. |
| `Ecos del Jaizkibel` | 5 PDF conservados | `usable-con-cautela` | Publicacion antigua. Revisar pagina concreta y procedencia de descarga; citar Euskariana o archivo correspondiente si procede. |
| `El Alarde` | 4 PDF | `usable-con-cautela` | Periodico de 1919 procedente del Archivo Municipal de Irun. Util para facsimiles o recortes historicos con cita completa; revisar cada fotografia/ilustracion si aparece autor. |
| `El Bidasoa` | 99 PDF | `usable-con-cautela` para numeros antiguos; `pedir-permiso` si son imagenes modernas o de autor claro | Publicacion local historica. Para recortes de pagina o cabeceras antiguas, riesgo bajo con cita completa. Para fotografias identificadas, anotar autor/fondo antes de decidir. |
| `El Bidasoa Mexicano` | 12 PDF | `pedir-permiso` | Publicacion de 1951-1961 y estudio moderno. Usar como fuente textual; imagenes solo con permiso o si se demuestra dominio publico/licencia. |
| `El Dia` | 13 PDF | `usable-con-cautela` | Prensa de 1930-1936. Puede usarse para recortes documentales con cita completa; fotografias con autor/agencia requieren revision individual. |
| `El Diario Vasco` | 8 PDF | `pedir-permiso` por defecto | Aunque haya ejemplares antiguos de 1935, 1937 o 1943, el medio sigue existiendo y puede haber derechos editoriales/fotograficos. Usar como fuente textual; para fotos o recortes graficos, pedir permiso salvo que se documente una razon clara de dominio publico/licencia. Recortes modernos de 1997/2008: no publicar sin autorizacion. |
| `El Irunes` | 75 PDF | `pedir-permiso` | Revista moderna/local con fotografias probablemente protegidas. Usar como fuente textual; imagenes solo con permiso o licencia clara. |
| `El buen combate semanario catolico` | 1 PDF | `revisar-caso-a-caso` | Comprobar fecha, procedencia y tipo de imagen. Si es prensa antigua sin fotografia de autor visible, podria ser `usable-con-cautela`; si contiene ilustracion/foto identificada, pedir permiso o descartar. |
| `El eco de Irun` | 28 PDF | `usable-con-cautela` | Prensa local antigua de 1909-1910. Recortes de pagina, cabeceras o textos graficos son candidatos razonables con cita completa. Revisar fotografias si aparece estudio o autor. |
| `La Libertad` | 2 PDF | `usable-con-cautela` | Prensa antigua de 1889-1890. Recortes documentales o cabeceras con cita completa son candidatos razonables. |
| `La Voz de Guipuzcoa - Diario Republicano` | 76 PDF | `usable-con-cautela` | Prensa antigua, mayoritariamente anterior a 1936. Para recortes de pagina, anuncios o cabeceras, riesgo bajo con cita completa. Fotografias con autor o estudio visible requieren registro individual. |
| `La frontera semanario republicano` | 2 PDF | `usable-con-cautela` | Prensa local de 1926. Candidata para recortes documentales con cita completa; revisar fotos/ilustraciones si constan autores. |
| `La informacion - Diario independiente` | 3 PDF | `usable-con-cautela` | Prensa de 1918-1920. Puede usarse para facsimiles o recortes pequenos con cita completa. Revisar fotografia concreta si aparece autor. |
| `Novedades revista semanal ilustrada` | 6 PDF | `revisar-caso-a-caso` | Revista ilustrada: puede contener fotografias de agencia, estudio o autor. Aunque sea antigua, revisar cada imagen antes de publicarla. |
| `Ordenanzas` | 1 PDF | `solo-consulta` para imagenes; `usable` para cita textual institucional breve | Documento normativo. Normalmente no aporta imagenes publicables; usar como fuente textual y citar la ordenanza. |
| `Programas de fiestas` | 265 PDF | `usable-con-cautela` para material antiguo; `pedir-permiso` desde posguerra reciente | Los programas municipales antiguos pueden aportar imagenes utiles, pero muchos incluyen fotografias, anuncios, dibujos o portadas con autor desconocido. Antes de publicar cada recorte hay que registrar ano, pagina y tipo de imagen. En programas modernos, pedir permiso salvo licencia clara. |
| `Recortes del periodico Egin` | 8 TIFF conservados | `pedir-permiso` | Recortes de 1980-1982. No publicar imagenes ni recortes graficos sin permiso. |
| `Txistulari` | 1 PDF | `pedir-permiso` | Publicacion especializada con autores y posible material grafico protegido. Usar como fuente textual; no recortar imagenes sin licencia o permiso. |
| `Unidad` | 1 PDF | `pedir-permiso` salvo recorte muy justificado | Prensa de 1937. Usar preferentemente como fuente textual. Para imagenes, pedir permiso o publicar solo si se justifica dominio publico/licencia y se cita con precision. |
| `Uranzu` | 13 PDF | `usable-con-cautela` para numeros antiguos; `pedir-permiso` para 1978 | Los numeros de 1925-1926 son prensa antigua y pueden servir para recortes documentales con cita completa. El especial de 1978 debe tratarse como moderno: pedir permiso para imagenes. |
| `Urumea` | 1 PDF | `usable-con-cautela` | Prensa antigua de 1880. Candidata razonable para recortes documentales con cita completa. |

## Procedimiento para cada candidato

1. Guardar ruta exacta del documento y pagina.
2. Exportar una miniatura de trabajo en `/tmp` para revisar el recorte.
3. Identificar si es fotografia, dibujo, anuncio, portada, mapa, partitura o facsimil de texto.
4. Buscar en la propia pagina pie de foto, autor, estudio, agencia, fondo o archivo.
5. Clasificar con uno de los estados anteriores.
6. Si se publica, crear copia optimizada en `assets/` y registrar atribucion visible o cercana.
7. Mantener el original intacto en `Descargas`; no modificarlo ni moverlo.

## Herramientas del proyecto

- Extraccion automatica de imagenes embebidas en PDFs o archivos graficos ya separados:
  `python3 scripts/extract-document-image-candidates.py --folder "Nombre de carpeta"`.
- Recorte manual de una pagina o lamina cuando la foto esta dentro de una pagina escaneada:
  `python3 scripts/crop-document-image.py documento.pdf --page 1 --crop x,y,w,h --title "Titulo" --year 1919 --rights-status usable-con-cautela --attribution "Fuente completa"`.
- Publicacion de candidatos ya revisados:
  `python3 scripts/publish-document-image-candidates.py`.

La publicacion exige que el candidato tenga `review_status: "aprobado-publicar"` y `publishable_by_policy: true`. Si el recorte identifica una cantinera con nombre, ano y compania, el campo `cantinera_matches` permite enlazarlo tambien desde la pagina de Cantineras.

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
