#!/usr/bin/env python3
"""Importa fotografias publicables de la Fototeca Municipal de Irun."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlparse


DEFAULT_INPUT = Path("data/irun-fototeca-alarde-irun-resultados-con-fondo.csv")
DEFAULT_GALLERY_DATA = Path("data/alarde-imagenes.json")
DEFAULT_CANTINERAS_DATA = Path("data/cantineras.json")
DEFAULT_CANTINERA_PHOTOS = Path("data/cantinera-fotos.json")
DEFAULT_OUTPUT = Path("assets/alarde-imagenes/irun")
DEFAULT_CACHE = Path(tempfile.gettempdir()) / "webalarde-irun-fototeca"

AUTHORIZED_FUNDS = {"Fondo Kruz", "Felipe Iguiñiz", "Matías Guilló", "Familia Aguirreche", "Familia Zaragüeta"}
ARCHIVE = "Archivo Municipal de Irun"
LICENSE = "Uso no comercial autorizado por el Archivo Municipal de Irun"

COMPANY_ALIASES = {
    "ama shantalen": "Ama Shantalen",
    "anaka": "Anaka",
    "artilleria": "Batería de Artillería",
    "bateria de artilleria": "Batería de Artillería",
    "banda": "Banda de Música",
    "banda de musica": "Banda de Música",
    "behobia": "Behobia",
    "belaskoenea": "Belaskoenea",
    "belasko-enea": "Belaskoenea",
    "bidasoa": "Bidasoa",
    "buenos amigos": "Buenos Amigos",
    "caballeria": "Escolta de Caballería",
    "escolta de caballeria": "Escolta de Caballería",
    "lapice": "Lapice",
    "lapize": "Lapice",
    "meaka": "Meaka",
    "olaberria": "Olaberria",
    "real union": "Real Unión",
    "san miguel": "San Miguel",
    "santiago": "Santiago",
    "tamborrada": "Tamborrada",
    "uranzu": "Uranzu",
    "ventas": "Ventas",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFD", value or "")
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_year(*values: str) -> str:
    for value in values:
        match = re.search(r"\b(1[89]\d{2}|20\d{2})\b", value or "")
        if match:
            return match.group(1)
    return "sin-fecha"


def is_authorized(row: dict[str, str]) -> bool:
    if row.get("fondo_o_procedencia") in AUTHORIZED_FUNDS:
        return True
    if row.get("fondo_o_procedencia") == "Postal antigua":
        year = extract_year(row.get("ano_foto", ""), row.get("descripcion", ""))
        return year != "sin-fecha" and int(year) < 1936
    return False


def large_image_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    folder = str(Path(parsed.path).parent)
    if name.startswith("g"):
        return f"{parsed.scheme}://{parsed.netloc}{quote(parsed.path)}"
    return f"{parsed.scheme}://{parsed.netloc}{quote(folder)}/g{quote(name)}"


def fetch(url: str, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return True
    command = [
        "curl",
        "-L",
        "--silent",
        "--show-error",
        "--fail",
        "--retry",
        "3",
        "--max-time",
        "25",
        "--user-agent",
        "Mozilla/5.0 (compatible; webalarde-irun-fototeca/1.0)",
        url,
        "--output",
        str(destination),
    ]
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        destination.unlink(missing_ok=True)
        return False


def run_magick(source: Path, destination: Path, args: list[str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_mtime >= source.stat().st_mtime:
        return
    subprocess.run(["magick", str(source), "-auto-orient", *args, str(destination)], check=True)


def build_assets(reference: str, source: Path, output_dir: Path) -> dict[str, str]:
    basename = f"irun-{reference}.webp"
    full_path = output_dir / "full" / basename
    thumb_path = output_dir / "thumbs" / basename

    run_magick(source, full_path, ["-strip", "-resize", "1600x1600>", "-quality", "78"])
    run_magick(
        source,
        thumb_path,
        ["-strip", "-thumbnail", "520x360^", "-gravity", "center", "-extent", "520x360", "-quality", "72"],
    )
    return {"full": full_path.as_posix(), "thumb": thumb_path.as_posix()}


def item_from_row(row: dict[str, str], paths: dict[str, str], image_url: str) -> dict[str, str]:
    reference = row["referencia"]
    fund = row.get("fondo_o_procedencia") or "procedencia no indicada"
    title = row.get("descripcion") or f"Fotografía del Alarde de San Marcial. Referencia {reference}"
    date = row.get("ano_foto") or ""
    return {
        "source": "archivo-irun",
        "object_id": reference,
        "title": title,
        "date": date,
        "year": extract_year(date, title),
        "photographer": "",
        "studio": fund,
        "archive": ARCHIVE,
        "license": LICENSE,
        "attribution": f"{ARCHIVE} · {fund} · Ref. {reference} · {LICENSE}",
        "detail_url": row.get("url_ficha", ""),
        "image_index": "1",
        "image_count": "1",
        "image_url": image_url,
        "full": paths["full"],
        "thumb": paths["thumb"],
    }


def company_from_description(description: str) -> str:
    normalized = normalize(description)
    for alias, company in sorted(COMPANY_ALIASES.items(), key=lambda pair: len(pair[0]), reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return company
    return ""


def cantinera_key(entry: dict[str, object]) -> str:
    return f"{entry['year']}|{entry['company']}|{normalize(str(entry['name']))}"


def match_cantinera(item: dict[str, str], entries: list[dict[str, object]]) -> dict[str, object] | None:
    description = item["title"]
    if "cantinera" not in normalize(description):
        return None

    year = item["year"]
    if year == "sin-fecha":
        return None

    company = company_from_description(description)
    if not company:
        return None

    normalized_description = normalize(description)
    candidates = [
        entry
        for entry in entries
        if str(entry.get("year")) == year and entry.get("company") == company
    ]
    for entry in candidates:
        normalized_name = normalize(str(entry.get("name", "")))
        if normalized_name and normalized_name in normalized_description:
            return entry

    for entry in candidates:
        tokens = [token for token in normalize(str(entry.get("name", ""))).split() if len(token) > 2]
        if len(tokens) >= 2 and all(token in normalized_description for token in tokens[:2]):
            return entry

    return None


def merge_gallery(existing_path: Path, new_items: list[dict[str, str]]) -> None:
    existing = json.loads(existing_path.read_text(encoding="utf-8")) if existing_path.exists() else []
    kept = [item for item in existing if item.get("source") != "archivo-irun"]
    merged = kept + new_items
    merged.sort(key=lambda item: (item.get("year") == "sin-fecha", item.get("year", ""), item.get("object_id", "")))
    existing_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_cantinera_photos(path: Path, matches: dict[str, dict[str, object]]) -> None:
    data = {"source": "Archivo Municipal de Irun", "entries": list(matches.values())}
    data["entries"].sort(key=lambda item: (item["year"], item["company"], item["name"]))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera galería web con fotos autorizadas de la Fototeca de Irun.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--gallery-data", type=Path, default=DEFAULT_GALLERY_DATA)
    parser.add_argument("--cantineras-data", type=Path, default=DEFAULT_CANTINERAS_DATA)
    parser.add_argument("--cantinera-photos", type=Path, default=DEFAULT_CANTINERA_PHOTOS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = [row for row in csv.DictReader(args.input.open(encoding="utf-8", newline="")) if is_authorized(row)]
    if args.limit:
        rows = rows[: args.limit]

    cantineras = json.loads(args.cantineras_data.read_text(encoding="utf-8"))["entries"]
    items: list[dict[str, str]] = []
    matches: dict[str, dict[str, object]] = {}

    for index, row in enumerate(rows, start=1):
        reference = row["referencia"]
        image_url = large_image_url(row["url_imagen_resultado"])
        cache_file = args.cache / f"{reference}.jpg"
        if not fetch(image_url, cache_file):
            image_url = row["url_imagen_resultado"]
            if not fetch(image_url, cache_file):
                print(f"Sin imagen descargable: {reference}")
                continue

        paths = build_assets(reference, cache_file, args.output)
        item = item_from_row(row, paths, image_url)
        items.append(item)

        cantinera = match_cantinera(item, cantineras)
        if cantinera:
            key = cantinera_key(cantinera)
            matched = matches.setdefault(
                key,
                {
                    "id": key,
                    "year": cantinera["year"],
                    "company": cantinera["company"],
                    "name": cantinera["name"],
                    "profile": item,
                    "photos": [],
                },
            )
            matched["photos"].append(item)

        if index % 100 == 0 or index == len(rows):
            print(f"{index}/{len(rows)} fotografias procesadas; {len(matches)} cantineras con fotos", flush=True)

    merge_gallery(args.gallery_data, items)
    write_cantinera_photos(args.cantinera_photos, matches)
    print(f"Galeria: {args.gallery_data} (+{len(items)} Archivo Irun)")
    print(f"Fotos de cantineras: {args.cantinera_photos} ({len(matches)} cantineras)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
