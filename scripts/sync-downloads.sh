#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${1:-"$ROOT_DIR/../downloads"}"
TARGET_DIR="$ROOT_DIR/downloads"

if [ ! -e "$SOURCE_DIR" ]; then
  echo "No existe la carpeta de origen: $SOURCE_DIR" >&2
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "El origen no es una carpeta: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
find "$TARGET_DIR" -mindepth 1 ! -name ".gitkeep" -exec rm -rf {} +
cp -a "$SOURCE_DIR"/. "$TARGET_DIR"/

find "$TARGET_DIR" -type f | sort
