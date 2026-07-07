#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${1:-"$ROOT_DIR/../downloads"}"
TARGET_DIR="$ROOT_DIR/downloads"
PREVIEW_DIR="$ROOT_DIR/assets/download-previews"

if [ ! -e "$SOURCE_DIR" ]; then
  echo "No existe la carpeta de origen: $SOURCE_DIR" >&2
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "El origen no es una carpeta: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
mkdir -p "$PREVIEW_DIR"
find "$TARGET_DIR" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
find "$PREVIEW_DIR" -mindepth 1 -type f -exec rm -f {} +
cp -a "$SOURCE_DIR"/. "$TARGET_DIR"/

if command -v magick >/dev/null 2>&1; then
  find "$TARGET_DIR" -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) -print0 |
    while IFS= read -r -d "" file; do
      base="$(basename "$file")"
      name="${base%.*}"
      preview_name="${name// /-}.webp"
      magick "$file" -auto-orient -resize 520x360^ -gravity center -extent 520x360 -quality 78 -strip "$PREVIEW_DIR/$preview_name"
    done
else
  echo "Aviso: ImageMagick no esta instalado; no se han generado previews." >&2
fi

find "$TARGET_DIR" -type f | sort
