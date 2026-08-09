# Catalogo documental sanmarcialero

Este catalogo es el indice maestro del corpus documental local conservado en `/home/gaizka/Alarde`.

A diferencia del rastreo OCR, aqui debe aparecer cada documento del corpus aunque el texto no se haya podido leer bien de forma automatica. Por tanto, una fila sin pasajes detectados no significa que el documento no trate sobre San Marcial; significa solo que aun no tiene una entrada humana completa o que el OCR no ha recuperado texto fiable.

## Archivo principal

- `docs/catalogo-documental-sanmarcialero.csv`: catalogo maestro, una fila por documento.
- `docs/indice-revision-manual-sanmarcialero.md`: version en formato documento para revision manual, ordenada por fecha y con un bloque por archivo.
- `docs/indice-articulos-sanmarcialeros.csv`: indice amplio de pasajes localizados por lectura automatica u OCR.
- `docs/rastreo-documentos-articulos.csv`: control tecnico de extraccion de texto, OCR visual y pasajes detectados.

## Campos del catalogo

- `ID`: identificador estable generado desde la ruta del documento.
- `Año` y `Fecha`: fecha normalizada cuando se puede deducir del archivo o del registro.
- `Publicacion`: nombre de la publicacion o fondo documental.
- `Tipo documental`: prensa, revista, programa de fiestas, ordenanza, documento municipal, libro o fuente fotografica.
- `Estado del indice real`: situacion editorial del documento dentro del indice.
- `Calidad de lectura`: calidad tecnica de la extraccion de texto.
- `Entradas curadas`: entradas procedentes del indice humano en Markdown.
- `Pasajes automaticos`: pasajes detectados por texto/OCR y pendientes de verificacion fina.
- `Pasajes OCR`: subconjunto de pasajes automaticos procedente de OCR visual.
- `Paginas detectadas`: paginas en las que el rastreo automatico localizo algo.
- `Temas`: temas detectados o curados.
- `Uso en la web`: si ya se ha integrado, si queda como referencia o si requiere revision.
- `Resumen para indice`: descripcion breve del contenido util conocido.
- `Observaciones`: criterio de lectura y cautelas.

## Estados

- `Indice real iniciado con entrada curada`: el documento ya tiene al menos una entrada revisada manualmente en el indice humano.
- `Catalogado con pistas automaticas pendientes de verificacion`: el documento contiene pasajes detectados por texto u OCR, pero esos pasajes deben comprobarse contra la fuente original antes de usarse como cita.
- `Catalogado; pendiente de indice humano`: el documento forma parte del corpus, pero aun no tiene entrada de contenido fiable.
- `Catalogado; requiere OCR mejorado o lectura manual`: el documento existe en el corpus, pero el OCR visual no pudo recuperar texto suficiente.

## Criterio de uso

El catalogo debe funcionar como indice real de trabajo: sirve para saber que existe, donde esta, que se ha localizado y que queda pendiente. El indice amplio de pasajes es una ayuda para buscar, no una prueba definitiva. Cuando se extraiga informacion para la web, hay que contrastar siempre el pasaje con el PDF, imagen o fuente original.

Para regenerarlo:

```bash
python3 scripts/build-document-catalog.py
```

Para regenerar la version manual en Markdown:

```bash
python3 scripts/build-manual-document-index.py
```

Para regenerar la version en Word:

```bash
python3 scripts/build-manual-document-word.py
```
