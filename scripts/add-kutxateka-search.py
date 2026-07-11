#!/usr/bin/env python3
"""Append missing Kutxateka results from a supplemental search or URL list."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import HTTPCookieProcessor, build_opener


DEFAULT_ARCHIVE = Path("../kutxateka-downloads")


def load_downloader():
    script_path = Path(__file__).with_name("download-kutxateka.py")
    spec = importlib.util.spec_from_file_location("download_kutxateka", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se puede cargar {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append missing Kutxateka objects from another search.")
    parser.add_argument("--search", help="Search text to add.")
    parser.add_argument("--start-url", help="Full Kutxateka search URL to add.")
    parser.add_argument("--detail-urls-file", type=Path, help="Text file with one detail URL per line.")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE, help="Existing Kutxateka archive folder.")
    parser.add_argument("--delay", type=float, default=10.0, help="Seconds between requests.")
    parser.add_argument("--max-pages", type=int, help="Limit result pages.")
    parser.add_argument("--dry-run", action="store_true", help="Only list missing detail URLs.")
    return parser.parse_args()


def existing_fieldnames(metadata_path: Path) -> list[str]:
    with metadata_path.open(encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise RuntimeError(f"CSV sin cabecera: {metadata_path}")
        return reader.fieldnames


def build_rows(mod, opener, detail_url: str, images_dir: Path, delay: float) -> list[dict[str, str]]:
    page_html = mod.fetch_text(opener, detail_url)
    object_id = mod.extract_object_id(detail_url)
    title = mod.extract_title(page_html)
    image_records = mod.extract_image_records(page_html, detail_url)
    photographer = mod.extract_field(page_html, ["ARGAZKILARIA", "Argazkilaria", "AUTOR", "Autor"])
    studio = mod.extract_field(page_html, ["ESTUDIOA", "Estudioa", "ESTUDIO", "Estudio"])
    archive = mod.extract_field(page_html, ["Artxiboa", "ARCHIVO", "Archivo"])
    date = mod.extract_date(page_html)
    rows: list[dict[str, str]] = []

    if not image_records:
        row = {
            "object_id": object_id,
            "title": title,
            "date": date,
            "photographer": photographer,
            "studio": studio,
            "archive": archive,
            "license": mod.LICENSE,
            "detail_url": detail_url,
            "image_index": "",
            "image_count": "0",
            "image_url": "",
            "file": "",
        }
        row["attribution"] = mod.build_attribution(row)
        return [row]

    if len(image_records) > 1:
        print(f"  {len(image_records)} imagenes en la ficha.", file=sys.stderr)

    for image_index, image_record in enumerate(image_records, start=1):
        image_url = image_record["image_url"]
        filename = mod.filename_for_image(object_id, title, image_url, image_index, len(image_records))
        destination = images_dir / filename

        if not destination.exists():
            time.sleep(delay)
            mod.download_file(opener, image_url, destination)

        row = {
            "object_id": object_id,
            "title": title,
            "date": date,
            "photographer": photographer,
            "studio": studio,
            "archive": archive,
            "license": mod.LICENSE,
            "detail_url": image_record["detail_url"],
            "image_index": str(image_index),
            "image_count": str(len(image_records)),
            "image_url": image_url,
            "file": f"images/{filename}",
        }
        row["object_id"] = image_record["object_id"]
        row["attribution"] = mod.build_attribution(row)
        rows.append(row)

    return rows


def main() -> int:
    args = parse_args()
    if not args.search and not args.start_url and not args.detail_urls_file:
        print("Indica --search, --start-url o --detail-urls-file.", file=sys.stderr)
        return 2

    mod = load_downloader()
    opener = build_opener(HTTPCookieProcessor())
    start_url = args.start_url or (
        f"{mod.BASE_URL}/index.php/Search/objects/search/?search={quote_plus(args.search)}"
        if args.search
        else ""
    )
    detail_urls_path = args.archive / "detail_urls.txt"
    metadata_path = args.archive / "metadata.csv"
    images_dir = args.archive / "images"

    existing_urls = {
        line.strip()
        for line in detail_urls_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    fieldnames = existing_fieldnames(metadata_path)

    if args.detail_urls_file:
        found_urls = [
            line.strip()
            for line in args.detail_urls_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        try:
            found_urls = mod.collect_detail_urls(opener, start_url, args.delay, args.max_pages)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"Error leyendo resultados: {exc}", file=sys.stderr)
            return 1

    missing_urls = [url for url in found_urls if url not in existing_urls]
    print(f"Fichas encontradas: {len(found_urls)}", file=sys.stderr)
    print(f"Fichas nuevas: {len(missing_urls)}", file=sys.stderr)

    if args.dry_run:
        for detail_url in missing_urls:
            print(detail_url)
        return 0

    images_dir.mkdir(parents=True, exist_ok=True)
    with metadata_path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        for index, detail_url in enumerate(missing_urls, start=1):
            print(f"[{index}/{len(missing_urls)}] {detail_url}", file=sys.stderr)
            try:
                rows = build_rows(mod, opener, detail_url, images_dir, args.delay)
            except (HTTPError, URLError, TimeoutError) as exc:
                print(f"  Error leyendo ficha: {exc}", file=sys.stderr)
                continue

            writer.writerows(rows)
            csv_file.flush()
            with detail_urls_path.open("a", encoding="utf-8") as detail_file:
                detail_file.write(detail_url + "\n")

            if index < len(missing_urls):
                time.sleep(args.delay)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
