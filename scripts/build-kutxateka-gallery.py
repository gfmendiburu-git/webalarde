#!/usr/bin/env python3
"""Build web-ready Kutxateka gallery assets from the local archive."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path


DEFAULT_ARCHIVE = Path("../kutxateka-downloads")
DEFAULT_OUTPUT = Path("assets/alarde-imagenes")
DEFAULT_DATA = Path("data/alarde-imagenes.json")


def extract_year(value: str) -> str:
    match = re.search(r"\b(1[6-9]\d{2}|20\d{2})\b", value or "")
    return match.group(1) if match else "sin-fecha"


def run_magick(source: Path, destination: Path, args: list[str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_mtime >= source.stat().st_mtime:
        return

    command = ["magick", str(source), "-auto-orient", *args, str(destination)]
    subprocess.run(command, check=True)


def build_assets(row: dict[str, str], source: Path, output_dir: Path) -> dict[str, str]:
    object_id = row["object_id"]
    image_index = int(row.get("image_index") or 1)
    basename = f"{object_id}-{image_index:03d}.webp"
    full_path = output_dir / "full" / basename
    thumb_path = output_dir / "thumbs" / basename

    run_magick(
        source,
        full_path,
        ["-strip", "-resize", "1600x1600>", "-quality", "78"],
    )
    run_magick(
        source,
        thumb_path,
        [
            "-strip",
            "-thumbnail",
            "520x360^",
            "-gravity",
            "center",
            "-extent",
            "520x360",
            "-quality",
            "72",
        ],
    )

    return {
        "full": full_path.as_posix(),
        "thumb": thumb_path.as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate optimized gallery images for GitHub Pages.")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="Local Kutxateka archive folder.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output folder for optimized images.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="Output JSON data file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata_path = args.archive / "metadata.csv"
    rows = list(csv.DictReader(metadata_path.open(encoding="utf-8")))
    items: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        source = args.archive / row["file"]
        if not source.exists():
            print(f"Sin archivo local: {source}")
            continue

        paths = build_assets(row, source, args.output)
        item = {
            "object_id": row["object_id"],
            "title": row["title"],
            "date": row["date"],
            "year": extract_year(row["date"]),
            "photographer": row["photographer"],
            "studio": row["studio"],
            "archive": row["archive"],
            "license": row["license"],
            "attribution": row["attribution"],
            "detail_url": row["detail_url"],
            "image_index": row["image_index"],
            "image_count": row["image_count"],
            "full": paths["full"],
            "thumb": paths["thumb"],
        }
        items.append(item)

        if index % 50 == 0 or index == len(rows):
            print(f"{index}/{len(rows)} imagenes procesadas")

    args.data.parent.mkdir(parents=True, exist_ok=True)
    args.data.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"JSON: {args.data}")
    print(f"Imagenes optimizadas: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
