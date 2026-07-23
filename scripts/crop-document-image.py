#!/usr/bin/env python3
"""Create one reviewed crop from a document page or image."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path

from PIL import Image


SITE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path("/home/gaizka/Descargas/Alarde de San Marcial")
DEFAULT_ORIGINALS = SOURCE_ROOT / "Recortes web" / "originales"
DEFAULT_ASSETS = SITE_ROOT / "assets" / "document-recortes"
DEFAULT_MANIFEST = SITE_ROOT / "data" / "document-recortes-candidatos.json"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower() or "sin-nombre"


def norm_key(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(SITE_ROOT))
    except ValueError:
        return str(path)


def top_folder(path: Path) -> str:
    return path.relative_to(SOURCE_ROOT).parts[0]


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_pdf_page(pdf: Path, page: int, dpi: int, outdir: Path) -> Path:
    prefix = outdir / "page"
    subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-f", str(page), "-singlefile", "-png", str(pdf), str(prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return prefix.with_suffix(".png")


def make_web_versions(src: Path, full_dest: Path, thumb_dest: Path) -> None:
    full_dest.parent.mkdir(parents=True, exist_ok=True)
    thumb_dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        image = image.convert("RGB")
        full = image.copy()
        full.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        full.save(full_dest, "WEBP", quality=86, method=6)
        thumb = image.copy()
        thumb.thumbnail((560, 420), Image.Resampling.LANCZOS)
        thumb.save(thumb_dest, "WEBP", quality=78, method=6)


def cantinera_match(year: str, company: str, name: str) -> list[dict]:
    if not (year and company and name):
        return []
    return [{
        "year": int(year),
        "company": company,
        "name": name,
        "key": f"{year}|{company}|{norm_key(name)}",
    }]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--page", type=int, help="1-based PDF page number.")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--crop", required=True, help="Crop rectangle as x,y,w,h in rendered/source pixels.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--year", required=True)
    parser.add_argument("--rights-status", required=True)
    parser.add_argument("--attribution", required=True)
    parser.add_argument("--review-status", default="pendiente-revision-visual")
    parser.add_argument("--cantinera-name")
    parser.add_argument("--cantinera-company")
    parser.add_argument("--originals-dir", type=Path, default=DEFAULT_ORIGINALS)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    source = args.source
    x, y, w, h = [int(part.strip()) for part in args.crop.split(",")]

    with tempfile.TemporaryDirectory(prefix="alarde-crop-") as tmp:
        tmpdir = Path(tmp)
        page_label = f"p.{args.page}" if args.page else "imagen"
        if source.suffix.lower() == ".pdf":
            if not args.page:
                raise SystemExit("--page is required for PDFs")
            base = render_pdf_page(source, args.page, args.dpi, tmpdir)
        else:
            base = source

        with Image.open(base) as image:
            crop = image.crop((x, y, x + w, y + h)).convert("RGB")
            source_folder = top_folder(source)
            candidate_id = f"doc-{slugify(source_folder)}-{slugify(source.stem)}-{page_label.replace('.', '')}-{slugify(args.title)}"
            original_dest = args.originals_dir / source_folder / f"{candidate_id}.jpg"
            original_dest.parent.mkdir(parents=True, exist_ok=True)
            crop.save(original_dest, "JPEG", quality=96, subsampling=0)

    digest = sha256_file(original_dest)
    candidate_id = f"{candidate_id}-{digest[:10]}"
    final_original = original_dest.with_name(f"{candidate_id}.jpg")
    original_dest.rename(final_original)

    full_dest = args.assets_dir / "full" / f"{candidate_id}.webp"
    thumb_dest = args.assets_dir / "thumbs" / f"{candidate_id}.webp"
    make_web_versions(final_original, full_dest, thumb_dest)

    entry = {
        "id": candidate_id,
        "source_file": str(source),
        "source_folder": top_folder(source),
        "source_page": page_label,
        "title": args.title,
        "year": args.year,
        "rights_status": args.rights_status,
        "publishable_by_policy": args.rights_status in {"usable", "usable-con-cautela"},
        "original": str(final_original),
        "full": display_path(full_dest),
        "thumb": display_path(thumb_dest),
        "width": w,
        "height": h,
        "sha256": digest,
        "attribution": args.attribution,
        "review_status": args.review_status,
        "cantinera_matches": cantinera_match(args.year, args.cantinera_company or "", args.cantinera_name or ""),
    }

    manifest = load_json(args.manifest, {
        "source_root": str(SOURCE_ROOT),
        "originals_dir": str(args.originals_dir),
        "assets_dir": display_path(args.assets_dir),
        "entries": [],
        "stats": {},
        "failed_files": [],
    })
    entries = [item for item in manifest.get("entries", []) if item.get("sha256") != digest]
    entries.append(entry)
    manifest["entries"] = sorted(entries, key=lambda item: (item["source_folder"], item["source_file"], item["id"]))
    manifest["stats"] = {
        **manifest.get("stats", {}),
        "total_candidates": len(entries),
    }
    save_json(args.manifest, manifest)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
