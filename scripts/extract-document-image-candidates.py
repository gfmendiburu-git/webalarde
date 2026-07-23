#!/usr/bin/env python3
"""Extract candidate image crops from local Alarde documentation.

The script is intentionally conservative:
- It does not alter source files.
- It keeps high quality extracted candidates outside the published site.
- It writes optimized WebP copies under assets for candidates that may later be
  published.
- It records rights status and cantinera matching hints, but does not decide
  legal publication for ambiguous material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image


SITE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path("/home/gaizka/Descargas/Alarde de San Marcial")
DEFAULT_ORIGINALS = SOURCE_ROOT / "Recortes web" / "originales"
DEFAULT_MANIFEST = SITE_ROOT / "data" / "document-recortes-candidatos.json"
DEFAULT_ASSETS = SITE_ROOT / "assets" / "document-recortes"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
PDF_EXTS = {".pdf"}


FOLDER_POLICIES = {
    "Alarde de San Marcial en Irún: origen y detalles - Serapio Múgica - 1901": ("usable-con-cautela", False),
    "Album gráfico descriptivo del País Vascongado años de 1914-1915 tomo de Guipúzcoa - Creative Commons CC BY-SA 4.0": ("usable", False),
    "Bidasoan": ("pedir-permiso", True),
    "Easo": ("usable-con-cautela", True),
    "Ecos del Jaizkibel": ("usable-con-cautela", True),
    "El Alarde": ("usable-con-cautela", True),
    "El Bidasoa": ("usable-con-cautela", True),
    "El Bidasoa Mexicano": ("pedir-permiso", True),
    "El Dia": ("usable-con-cautela", True),
    "El Diario Vasco": ("pedir-permiso", True),
    "El Irunes": ("pedir-permiso", True),
    "El buen combate semanario catolico": ("revisar-caso-a-caso", True),
    "El eco de Irun": ("usable-con-cautela", True),
    "La Libertad": ("usable-con-cautela", True),
    "La Voz de Guipuzcoa - Diario Republicano": ("usable-con-cautela", True),
    "La frontera semanario republicano": ("usable-con-cautela", True),
    "La informacion - Diario independiente": ("usable-con-cautela", True),
    "Novedades revista semanal ilustrada": ("revisar-caso-a-caso", True),
    "Ordenanzas": ("solo-consulta", False),
    "Programas de fiestas": ("usable-con-cautela", True),
    "Recortes del periodico Egin": ("pedir-permiso", True),
    "Txistulari": ("pedir-permiso", True),
    "Unidad": ("pedir-permiso", True),
    "Uranzu": ("usable-con-cautela", True),
    "Urumea": ("usable-con-cautela", True),
}

APPROVED_STATES = {"usable", "usable-con-cautela"}
ALARD_KEYWORDS = (
    "alarde",
    "san marcial",
    "san martzial",
    "cantinera",
    "hacher",
    "archer",
    "tamborr",
    "banda",
    "caballeria",
    "artilleria",
    "compania",
    "compañia",
    "irun",
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug or "sin-nombre"


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


def top_folder(path: Path) -> str:
    rel = path.relative_to(SOURCE_ROOT)
    return rel.parts[0]


def policy_for(path: Path) -> tuple[str, bool]:
    return FOLDER_POLICIES.get(top_folder(path), ("revisar-caso-a-caso", True))


def discover_files(limit: int | None = None, folders: set[str] | None = None) -> list[Path]:
    files: list[Path] = []
    for path in SOURCE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.parts[-2:] and "Recortes web" in path.parts:
            continue
        if path.suffix.lower() not in IMAGE_EXTS | PDF_EXTS:
            continue
        if folders and top_folder(path) not in folders:
            continue
        files.append(path)
        if limit and len(files) >= limit:
            break
    return sorted(files)


def run_pdfimages(pdf: Path, output_prefix: Path, timeout: int) -> list[Path]:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    before = set(output_prefix.parent.glob(output_prefix.name + "-*"))
    subprocess.run(
        ["pdfimages", "-png", str(pdf), str(output_prefix)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    after = set(output_prefix.parent.glob(output_prefix.name + "-*"))
    return sorted(after - before)


def image_info(path: Path) -> tuple[int, int, str]:
    with Image.open(path) as image:
        return image.width, image.height, image.mode


def likely_full_page(width: int, height: int) -> bool:
    if width < 1200 or height < 1600:
        return False
    ratio = min(width, height) / max(width, height)
    return 0.62 <= ratio <= 0.78


def is_candidate(width: int, height: int, *, from_pdf: bool) -> tuple[bool, str]:
    if width < 260 or height < 220:
        return False, "demasiado-pequena"
    if from_pdf and likely_full_page(width, height):
        return False, "probable-pagina-completa"
    if width * height < 120_000:
        return False, "baja-resolucion"
    return True, "candidato"


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


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(SITE_ROOT))
    except ValueError:
        return str(path)


def title_from_file(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip()


def infer_year(path: Path) -> str:
    match = re.search(r"(18|19|20)\d{2}", path.name)
    if match:
        return match.group(0)
    for part in reversed(path.parts):
        match = re.search(r"(18|19|20)\d{2}", part)
        if match:
            return match.group(0)
    return ""


def load_cantineras() -> list[dict]:
    path = SITE_ROOT / "data" / "cantineras.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("entries", [])


def cantinera_matches(text: str, year: str, entries: list[dict]) -> list[dict]:
    haystack = norm_key(text)
    matches = []
    for entry in entries:
        if year and str(entry.get("year")) != str(year):
            continue
        name = norm_key(entry.get("name", ""))
        if name and name in haystack:
            matches.append({
                "year": entry.get("year"),
                "company": entry.get("company"),
                "name": entry.get("name"),
                "key": f"{entry.get('year')}|{entry.get('company')}|{name}",
            })
    return matches


@dataclass
class Candidate:
    id: str
    source_file: str
    source_folder: str
    source_page: str
    title: str
    year: str
    rights_status: str
    publishable_by_policy: bool
    original: str
    full: str
    thumb: str
    width: int
    height: int
    sha256: str
    attribution: str
    review_status: str
    cantinera_matches: list[dict]

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def attribution_for(path: Path, year: str) -> str:
    folder = top_folder(path)
    page = "pagina/imagen pendiente"
    date = year or "fecha no indicada"
    if folder == "Album gráfico descriptivo del País Vascongado años de 1914-1915 tomo de Guipúzcoa - Creative Commons CC BY-SA 4.0":
        return f"{folder} · {date} · CC BY-SA 4.0"
    if folder in {"Programas de fiestas", "El Alarde", "Alarde de San Marcial en Irún: origen y detalles - Serapio Múgica - 1901"}:
        return f"Archivo Municipal de Irun · {folder} · {date} · {page}"
    if folder in {"Ecos del Jaizkibel"}:
        return f"Euskariana · {folder} · {date} · {page}"
    return f"{folder} · {date} · {page}"


def process_image(
    src: Path,
    *,
    source_file: Path,
    source_page: str,
    seq: int,
    originals_dir: Path,
    assets_dir: Path,
    cantineras: list[dict],
    from_pdf: bool,
) -> Candidate | None:
    width, height, _ = image_info(src)
    ok, reason = is_candidate(width, height, from_pdf=from_pdf)
    if not ok:
        return None

    rights_status, extract_allowed = policy_for(source_file)
    year = infer_year(source_file)
    title = title_from_file(source_file)
    source_folder = top_folder(source_file)
    digest = sha256_file(src)
    candidate_id = f"doc-{slugify(source_folder)}-{slugify(source_file.stem)}-{seq:03d}-{digest[:10]}"

    ext = ".png" if src.suffix.lower() in {".png", ".tif", ".tiff"} else ".jpg"
    original_dest = originals_dir / source_folder / f"{candidate_id}{ext}"
    original_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, original_dest)

    full_dest = assets_dir / "full" / f"{candidate_id}.webp"
    thumb_dest = assets_dir / "thumbs" / f"{candidate_id}.webp"
    make_web_versions(original_dest, full_dest, thumb_dest)

    combined_text = f"{source_file.name} {title} {source_folder}"
    matches = cantinera_matches(combined_text, year, cantineras)

    publishable = rights_status in APPROVED_STATES and extract_allowed
    return Candidate(
        id=candidate_id,
        source_file=str(source_file),
        source_folder=source_folder,
        source_page=source_page,
        title=title,
        year=year,
        rights_status=rights_status,
        publishable_by_policy=publishable,
        original=str(original_dest),
        full=display_path(full_dest),
        thumb=display_path(thumb_dest),
        width=width,
        height=height,
        sha256=digest,
        attribution=attribution_for(source_file, year),
        review_status="pendiente-revision-visual" if publishable else "pendiente-permiso-o-revision",
        cantinera_matches=matches,
    )


def load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["sha256"]: item for item in data.get("entries", [])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--folder", action="append", help="Limit to a top-level source folder. Can be repeated.")
    parser.add_argument("--include-pending", action="store_true", help="Also extract folders whose default rights status is not publishable.")
    parser.add_argument("--pdf-timeout", type=int, default=20, help="Maximum seconds allowed for pdfimages per PDF.")
    parser.add_argument("--originals-dir", type=Path, default=DEFAULT_ORIGINALS)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--rebuild", action="store_true", help="Ignore existing manifest entries and rebuild selected candidates.")
    args = parser.parse_args()

    folders = set(args.folder or [])
    files = discover_files(limit=args.limit, folders=folders or None)
    cantineras = load_cantineras()
    existing = {} if args.rebuild else load_existing(args.manifest)
    entries = dict(existing)

    extracted = 0
    skipped_policy = 0
    skipped_existing = 0
    failed_files: list[str] = []
    scanned = 0

    with tempfile.TemporaryDirectory(prefix="alarde-doc-images-") as tmp:
        tmpdir = Path(tmp)
        for source in files:
            rights_status, extract_allowed = policy_for(source)
            if not extract_allowed:
                skipped_policy += 1
                continue
            if rights_status not in APPROVED_STATES and not args.include_pending:
                skipped_policy += 1
                continue
            scanned += 1
            temp_images: list[tuple[Path, str, bool]] = []
            try:
                if source.suffix.lower() in PDF_EXTS:
                    prefix = tmpdir / slugify(source.stem) / "img"
                    temp_images = [(p, "extraida", True) for p in run_pdfimages(source, prefix, args.pdf_timeout)]
                else:
                    temp_images = [(source, "imagen", False)]
            except subprocess.CalledProcessError:
                failed_files.append(str(source))
                continue
            except subprocess.TimeoutExpired:
                failed_files.append(str(source))
                continue
            except Exception:
                failed_files.append(str(source))
                continue

            seq = 0
            for image, source_page, from_pdf in temp_images:
                digest = sha256_file(image)
                if digest in entries:
                    skipped_existing += 1
                    continue
                seq += 1
                candidate = process_image(
                    image,
                    source_file=source,
                    source_page=source_page,
                    seq=seq,
                    originals_dir=args.originals_dir,
                    assets_dir=args.assets_dir,
                    cantineras=cantineras,
                    from_pdf=from_pdf,
                )
                if not candidate:
                    continue
                entries[candidate.sha256] = candidate.as_dict()
                extracted += 1

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source_root": str(SOURCE_ROOT),
        "originals_dir": str(args.originals_dir),
        "assets_dir": display_path(args.assets_dir),
        "entries": sorted(entries.values(), key=lambda item: (item["source_folder"], item["source_file"], item["id"])),
        "stats": {
            "files_seen": len(files),
            "files_scanned": scanned,
            "new_candidates": extracted,
            "skipped_policy": skipped_policy,
            "skipped_existing": skipped_existing,
            "total_candidates": len(entries),
            "failed_files": len(failed_files),
        },
        "failed_files": failed_files,
    }
    args.manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["stats"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
