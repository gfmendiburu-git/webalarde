# Alarde de San Marcial de Irun

Web informativa estática sobre el Alarde de San Marcial de Irun.

## Ver la web en local

Abre `index.html` en el navegador o sirve la carpeta con cualquier servidor estático.

## Publicar en GitHub Pages

1. Crea un repositorio nuevo en GitHub.
2. Conecta este proyecto local con el remoto:

   ```bash
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git branch -M main
   git push -u origin main
   ```

3. En GitHub, entra en `Settings` > `Pages`.
4. En `Build and deployment`, selecciona `Deploy from a branch`.
5. Elige la rama `main` y la carpeta `/root`.

## Descargas

Sube fondos de pantalla u otros archivos descargables a la carpeta `downloads/` y enlázalos desde la sección `Descargas` de `index.html`.

Si los fondos viven en una carpeta externa, sincronízalos al repositorio antes de publicar:

```bash
./scripts/sync-downloads.sh
```

Por defecto el script copia desde `../downloads`, que puede ser un symlink local hacia tu carpeta real de fondos. También puedes indicar otro origen:

```bash
./scripts/sync-downloads.sh /ruta/a/mis/fondos
```

## Kutxateka

Para descargar resultados públicos de Kutxateka de forma conservadora:

```bash
./scripts/download-kutxateka.py --search "alarde de irun"
```

Por defecto guarda las imágenes fuera del sitio, en `../kutxateka-downloads/`, junto a un `metadata.csv` con fuente, licencia y atribución. Antes de usar cualquier imagen en la web, revisa la licencia y conserva la atribución indicada.

Opciones útiles:

```bash
./scripts/download-kutxateka.py --dry-run
./scripts/download-kutxateka.py --max-items 3
./scripts/download-kutxateka.py --output ../kutxateka-alarde
```

## Nota editorial

Los horarios, recorridos y avisos pueden cambiar cada año. La web debe enlazar siempre a fuentes oficiales para la información operativa actualizada.
