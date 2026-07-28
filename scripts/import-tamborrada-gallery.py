#!/usr/bin/env python3
import hashlib
import html
import json
import re
import time
import unicodedata
import urllib.request
from pathlib import Path
from urllib.parse import quote, unquote, urlparse, urlunparse

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
TMP_PAGES = Path("/tmp/tamborrada-pages.json")
ORIGINALS_DIR = Path("/home/gaizka/Descargas/Alarde de San Marcial/Tamborrada Alarde Irun/originales")
MANIFEST_PATH = ORIGINALS_DIR.parent / "_manifest_tamborrada_alarde_irun.json"
FULL_DIR = ROOT / "assets/alarde-imagenes/tamborrada/full"
THUMB_DIR = ROOT / "assets/alarde-imagenes/tamborrada/thumbs"
ALARD_IMAGES = ROOT / "data/alarde-imagenes.json"
CANTINERA_PHOTOS = ROOT / "data/cantinera-fotos.json"
FULL_CANTINERAS = ROOT / "data/cantineras.json"

SOURCE_NAME = "Tamborrada del Alarde de Irun"
SOURCE_SITE = "tamborradaalardeirun.com"
LICENSE = "Uso autorizado por la Tamborrada del Alarde de Irun para uso no comercial en esta web"
ATTRIBUTION = f"{SOURCE_NAME} · {SOURCE_SITE} · Uso autorizado"

PAGE_CONFIG = {
    "galerias": {
        "kind": "gallery",
        "title": "La Tamborrada en imágenes",
    },
    "compania": {
        "kind": "cantineras",
        "title": "Cantineras de la Tamborrada",
    },
}


def clean_text(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return " ".join(html.unescape(value).split())


def slugify(value):
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "imagen"


def normalize_name(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = ascii_text.replace("maria", "ma").replace("mª", "ma")
    ascii_text = re.sub(r"[^a-z0-9]+", " ", ascii_text)
    return " ".join(ascii_text.split())


def canonical_url(url):
    url = html.unescape(url)
    return re.sub(r"-\d+x\d+(?=\.(?:jpe?g|png|gif|webp)$)", "", url, flags=re.I)


def request_url(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(path=quote(unquote(parsed.path))))


def output_stem(url, used):
    path = unquote(urlparse(url).path)
    stem = slugify(Path(path).stem)
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    candidate = f"tamborrada-{stem}"
    if candidate in used:
        candidate = f"{candidate}-{digest}"
    used.add(candidate)
    return candidate


def entry_id(year, company, name):
    return f"{year}|{slugify(company)}|{slugify(name)}"


def extract_figures(content, page):
    pieces = re.split(r"(<p[^>]*>\s*(?:&nbsp;|\s)*<strong>.*?</strong>.*?</p>|<figure[\s\S]*?</figure>)", content, flags=re.I)
    current_years = []
    records = []

    for piece in pieces:
        if not piece:
            continue
        if re.match(r"<p", piece, flags=re.I):
            text = clean_text(piece)
            years = re.findall(r"(?:18|19|20)\d{2}", text)
            if years:
                current_years = years
            continue
        if not re.match(r"<figure", piece, flags=re.I):
            continue

        href_match = re.search(r"<a[^>]+href=[\"']([^\"']+\.(?:jpe?g|png|gif|webp))[\"']", piece, flags=re.I)
        if not href_match:
            continue
        url = canonical_url(href_match.group(1))
        caption_match = re.search(r"<figcaption[^>]*>([\s\S]*?)</figcaption>", piece, flags=re.I)
        alt_match = re.search(r"<img[^>]+alt=[\"']([^\"']*)[\"']", piece, flags=re.I)
        caption = clean_text(caption_match.group(1) if caption_match else "")
        alt = html.unescape(alt_match.group(1)).strip() if alt_match else ""
        title = caption or alt or Path(unquote(urlparse(url).path)).stem.replace("-", " ")

        years = current_years[:] if page["kind"] == "cantineras" else []
        if not years:
            text_for_year = f"{title} {url}"
            years = re.findall(r"(?:18|19|20)\d{2}", text_for_year)
        year = years[0] if years else ""

        records.append({
            "url": url,
            "title": title,
            "year": year,
            "years": years or ([year] if year else []),
            "page_title": page["title"],
            "page_url": page["link"],
            "kind": page["kind"],
        })

    return records


def load_pages():
    if not TMP_PAGES.exists():
        raise SystemExit("No existe /tmp/tamborrada-pages.json; descarga primero la API de paginas.")
    pages = json.loads(TMP_PAGES.read_text())
    selected = []
    for item in pages:
        slug = item.get("slug")
        if slug in PAGE_CONFIG:
            config = PAGE_CONFIG[slug]
            selected.append({
                "slug": slug,
                "kind": config["kind"],
                "title": config["title"],
                "link": item.get("link") or f"http://tamborradaalardeirun.com/{slug}/",
                "content": item.get("content", {}).get("rendered", ""),
            })
    return selected


def download(url, dest):
    if dest.exists() and dest.stat().st_size:
        return
    request = urllib.request.Request(request_url(url), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    dest.write_bytes(data)
    time.sleep(0.04)


def optimize(original, full, thumb):
    with Image.open(original) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        full_img = img.copy()
        full_img.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        full_img.save(full, "WEBP", quality=82, method=6)

        thumb_img = img.copy()
        thumb_img.thumbnail((520, 520), Image.Resampling.LANCZOS)
        thumb_img.save(thumb, "WEBP", quality=76, method=6)


def build_photo(record, stem, original_path, full_path, thumb_path):
    title = record["title"]
    return {
        "source": "tamborrada-alarde-irun",
        "object_id": stem,
        "title": title,
        "date": record["year"],
        "year": record["year"] or "sin-fecha",
        "photographer": "",
        "studio": "Tamborrada del Alarde de Irun",
        "archive": SOURCE_NAME,
        "license": LICENSE,
        "attribution": ATTRIBUTION,
        "detail_url": record["page_url"],
        "image_url": record["url"],
        "original": str(original_path),
        "full": str(full_path.relative_to(ROOT)),
        "thumb": str(thumb_path.relative_to(ROOT)),
    }


def existing_gallery_by_url(items):
    return {
        item.get("image_url"): item
        for item in items
        if item.get("source") == "tamborrada-alarde-irun" and item.get("image_url")
    }


def build_full_cantineras_by_year(items):
    if isinstance(items, dict):
        items = items.get("entries", [])
    by_year = {}
    for item in items:
        if item.get("company") != "Tamborrada":
            continue
        by_year.setdefault(str(item.get("year")), []).append(item)
    return by_year


def target_years(record):
    url = record["url"].lower()
    if "1920-21-cantinera" in url:
        return ["1920", "1921"]
    if "197-28-30-cantinera" in url:
        return ["1927", "1928", "1930"]
    return [str(year) for year in record["years"] if year]


def photo_entry_from_full(item):
    name = item.get("name") or "Sin datos"
    year = str(item.get("year") or "")
    company = item.get("company") or "Tamborrada"
    return {
        "id": entry_id(year, company, name),
        "year": year,
        "company": company,
        "name": name,
        "confirmed": bool(item.get("confirmed")),
        "pending_confirmation": bool(item.get("pending_confirmation")),
        "profile": {},
        "photos": [],
    }


def attach_to_cantineras(cantinera_data, full_cantineras_by_year, photo, record):
    attached = []
    if record["kind"] != "cantineras":
        return attached

    photo_name = normalize_name(record["title"])
    entries = cantinera_data.setdefault("entries", [])
    existing_by_key = {
        (str(entry.get("year")), entry.get("company"), normalize_name(entry.get("name", ""))): entry
        for entry in entries
    }

    for year in target_years(record):
        candidates = []
        for entry in entries:
            if str(entry.get("year")) != str(year):
                continue
            if entry.get("company") != "Tamborrada":
                continue
            entry_name = normalize_name(entry.get("name", ""))
            if entry_name and entry_name == photo_name:
                candidates.append(entry)

        if not candidates:
            full_candidates = full_cantineras_by_year.get(str(year), [])
            if len(full_candidates) == 1:
                full_item = full_candidates[0]
                key = (str(year), "Tamborrada", normalize_name(full_item.get("name", "")))
                entry = existing_by_key.get(key)
                if not entry:
                    entry = photo_entry_from_full(full_item)
                    entries.append(entry)
                    existing_by_key[key] = entry
                candidates.append(entry)

        for entry in candidates:
            photos = entry.setdefault("photos", [])
            if not any(p.get("object_id") == photo["object_id"] for p in photos):
                photos.append(photo)
            if not entry.get("profile") or entry.get("profile", {}).get("source") == "generic":
                entry["profile"] = photo
            if entry.get("id") not in attached:
                attached.append(entry.get("id"))

    return attached


def main():
    ORIGINALS_DIR.mkdir(parents=True, exist_ok=True)
    FULL_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    pages = load_pages()
    records_by_url = {}
    for page in pages:
        for record in extract_figures(page["content"], page):
            records_by_url.setdefault(record["url"], record)

    alarde_items = json.loads(ALARD_IMAGES.read_text())
    cantinera_data = json.loads(CANTINERA_PHOTOS.read_text())
    full_cantineras = json.loads(FULL_CANTINERAS.read_text())
    full_cantineras_by_year = build_full_cantineras_by_year(full_cantineras)
    existing_by_url = existing_gallery_by_url(alarde_items)
    used_stems = {
        Path(item.get("full", "")).stem
        for item in alarde_items
        if item.get("source") == "tamborrada-alarde-irun"
    }

    manifest_items = []
    added_gallery = 0
    attached_count = 0

    for url, record in sorted(records_by_url.items(), key=lambda item: (item[1].get("year") or "9999", item[0])):
        if url in existing_by_url:
            photo = existing_by_url[url]
            original_path = Path(photo.get("original") or "")
        else:
            stem = output_stem(url, used_stems)
            ext = Path(unquote(urlparse(url).path)).suffix.lower() or ".jpg"
            original_path = ORIGINALS_DIR / f"{stem}{ext}"
            full_path = FULL_DIR / f"{stem}.webp"
            thumb_path = THUMB_DIR / f"{stem}.webp"

            download(url, original_path)
            if not full_path.exists() or not thumb_path.exists():
                optimize(original_path, full_path, thumb_path)

            photo = build_photo(record, stem, original_path, full_path, thumb_path)
            alarde_items.append(photo)
            existing_by_url[url] = photo
            added_gallery += 1

        attached = attach_to_cantineras(cantinera_data, full_cantineras_by_year, photo, record)
        attached_count += len(attached)

        manifest_items.append({
            "url": url,
            "file": original_path.name,
            "title": record["title"],
            "year": record["year"],
            "page": record["page_title"],
            "page_url": record["page_url"],
            "attached_cantineras": attached,
        })

    alarde_items.sort(key=lambda item: (
        str(item.get("year") or "sin-fecha"),
        str(item.get("source") or ""),
        str(item.get("object_id") or ""),
    ))
    ALARD_IMAGES.write_text(json.dumps(alarde_items, ensure_ascii=False, indent=2) + "\n")
    CANTINERA_PHOTOS.write_text(json.dumps(cantinera_data, ensure_ascii=False, indent=2) + "\n")

    MANIFEST_PATH.write_text(json.dumps({
        "source": SOURCE_NAME,
        "site": SOURCE_SITE,
        "permission": LICENSE,
        "downloaded": "2026-07-28",
        "pages": [{"title": page["title"], "url": page["link"], "kind": page["kind"]} for page in pages],
        "items": manifest_items,
    }, ensure_ascii=False, indent=2) + "\n")

    print(f"paginas: {len(pages)}")
    print(f"imagenes originales: {len(records_by_url)}")
    print(f"nuevas en galeria: {added_gallery}")
    print(f"adjuntos a cantineras: {attached_count}")
    print(f"manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
