#!/usr/bin/env python3
"""Download public Kutxateka search results with metadata.

The script is intentionally conservative: it follows result/detail pages,
uses the normal public media URL exposed in each detail page and waits between
requests. It does not call Kutxateka's internal Download endpoints.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, unquote, urljoin, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener


BASE_URL = "https://kutxateka.eus"
DEFAULT_SEARCH = "alarde de irun"
DEFAULT_OUTPUT = Path("../kutxateka-downloads")
LICENSE = "CC BY-NC 4.0"
USER_AGENT = "webalarde-local-archive-script/1.0 (+personal research; respectful delay)"


def fetch_text(opener, url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=60) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def download_file(opener, url: str, destination: Path) -> None:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with opener.open(request, timeout=120) as response:
        destination.write_bytes(response.read())


def strip_tags(value: str) -> str:
    value = re.sub(r"(?i)<br\s*/?>", "\n", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"[ \t]+", " ", value).strip()


def safe_filename(value: str, max_length: int = 90) -> str:
    value = html.unescape(value)
    value = re.sub(r"[^\w\s.-]", "", value, flags=re.UNICODE)
    value = re.sub(r"\s+", "-", value.strip())
    return (value[:max_length].strip(".-") or "kutxateka")


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def extract_detail_urls(page_html: str) -> list[str]:
    paths = re.findall(r"href=['\"](/index\.php/Detail/objects/\d+)(?:/s/\d+)?['\"]", page_html)
    return [urljoin(BASE_URL, path) for path in unique(paths)]


def extract_next_url(page_html: str) -> str | None:
    for match in re.finditer(r"(?is)<a\b([^>]*\bjscroll-next\b[^>]*)>", page_html):
        href = re.search(r"href=['\"]([^'\"]+)", match.group(1))
        if href:
            return urljoin(BASE_URL, html.unescape(href.group(1)))
    return None


def extract_title(page_html: str) -> str:
    match = re.search(r"(?is)<title>(.*?)</title>", page_html)
    if not match:
        return "Kutxateka object"
    title = strip_tags(match.group(1))
    title = re.sub(r"^Kutxateka\s*:\s*[^:]+:\s*", "", title)
    title = re.sub(r"\s*\[[^\]]+\]\s*$", "", title)
    return title.strip() or "Kutxateka object"


def extract_object_id(detail_url: str) -> str:
    match = re.search(r"/objects/(\d+)", detail_url)
    return match.group(1) if match else "unknown"


def extract_field(page_html: str, labels: Iterable[str]) -> str:
    for label in labels:
        pattern = rf"(?is)<h6>\s*{re.escape(label)}\s*</h6>(.*?)(?:<hr\b|</div>)"
        match = re.search(pattern, page_html)
        if match:
            return " | ".join(part for part in strip_tags(match.group(1)).splitlines() if part)
    return ""


def extract_date(page_html: str) -> str:
    match = re.search(r"(?is)<h6>\s*Data:\s*</h6>\s*<span>(.*?)</span>", page_html)
    return strip_tags(match.group(1)) if match else ""


def extract_image_url(page_html: str) -> str:
    urls = re.findall(
        r"https://kutxateka\.eus/media/images/[^'\"\s<>]+?_original\.(?:jpg|jpeg|png)",
        page_html,
        flags=re.IGNORECASE,
    )
    return html.unescape(unique(urls)[0]) if urls else ""


def extension_from_url(url: str) -> str:
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png"} else ".jpg"


def extract_variant_urls(page_html: str) -> list[str]:
    urls = [BASE_URL + "/index.php/Search/objects/search/?search=" + quote_plus(DEFAULT_SEARCH)]
    for href in re.findall(r"href=['\"]([^'\"]*/index\.php/Search/objects/[^'\"]*(?:sort|direction)[^'\"]*)", page_html):
        urls.append(urljoin(BASE_URL, html.unescape(href)))
    return unique(urls)


def collect_detail_urls(opener, start_url: str, delay: float, max_pages: int | None) -> list[str]:
    urls: list[str] = []
    current_url: str | None = start_url
    page_count = 0

    while current_url:
        page_count += 1
        print(f"Resultados {page_count}: {current_url}", file=sys.stderr)
        page_html = fetch_text(opener, current_url)
        urls.extend(extract_detail_urls(page_html))
        current_url = extract_next_url(page_html)

        if max_pages and page_count >= max_pages:
            break
        if current_url:
            time.sleep(delay)

    return unique(urls)


def collect_detail_urls_from_variants(opener, start_url: str, delay: float, max_pages: int | None) -> list[str]:
    print(f"Preparando variantes desde: {start_url}", file=sys.stderr)
    first_page = fetch_text(opener, start_url)
    variant_urls = extract_variant_urls(first_page)
    all_urls: list[str] = []

    first_page_urls = extract_detail_urls(first_page)
    all_urls.extend(first_page_urls)
    next_url = extract_next_url(first_page)
    if next_url and (not max_pages or max_pages > 1):
        all_urls.extend(collect_detail_urls(opener, next_url, delay, None if max_pages is None else max_pages - 1))

    for variant_url in variant_urls[1:]:
        time.sleep(delay)
        all_urls.extend(collect_detail_urls(opener, variant_url, delay, max_pages))

    return unique(all_urls)


def build_attribution(row: dict[str, str]) -> str:
    archive = row.get("archive") or "Kutxa Fundazioa Fototeka"
    photographer = row.get("photographer") or "autor no indicado"
    studio = row.get("studio")
    fund = studio or archive
    return f"{LICENSE} / KUTXA FUNDAZIOA FOTOTEKA / {fund} / {photographer}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download Kutxateka images from a public search.")
    parser.add_argument("--search", default=DEFAULT_SEARCH, help="Search text. Default: %(default)s")
    parser.add_argument("--start-url", help="Use a full Kutxateka search URL instead of --search.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output folder.")
    parser.add_argument("--delay", type=float, default=10.0, help="Seconds between requests.")
    parser.add_argument("--max-pages", type=int, help="Limit result pages.")
    parser.add_argument("--max-items", type=int, help="Limit detail items.")
    parser.add_argument("--dry-run", action="store_true", help="List what would be downloaded.")
    parser.add_argument("--refresh-list", action="store_true", help="Ignore cached detail_urls.txt.")
    parser.add_argument("--variants", action="store_true", help="Collect multiple sort/direction variants and deduplicate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    opener = build_opener(HTTPCookieProcessor())

    start_url = args.start_url or f"{BASE_URL}/index.php/Search/objects/search/?search={quote_plus(args.search)}"
    output_dir = args.output
    images_dir = output_dir / "images"
    metadata_path = output_dir / "metadata.csv"
    detail_urls_path = output_dir / "detail_urls.txt"

    if args.delay < 10:
        print("Aviso: robots.txt indica Crawl-delay: 10 para bots genéricos.", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)

    if detail_urls_path.exists() and not args.refresh_list and not args.max_pages:
        detail_urls = [line.strip() for line in detail_urls_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(f"Usando lista cacheada: {detail_urls_path}", file=sys.stderr)
    else:
        try:
            if args.variants:
                detail_urls = collect_detail_urls_from_variants(opener, start_url, args.delay, args.max_pages)
            else:
                detail_urls = collect_detail_urls(opener, start_url, args.delay, args.max_pages)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"Error leyendo resultados: {exc}", file=sys.stderr)
            return 1
        detail_urls_path.write_text("\n".join(detail_urls) + "\n", encoding="utf-8")

    if args.max_items:
        detail_urls = detail_urls[: args.max_items]

    print(f"Fichas encontradas: {len(detail_urls)}", file=sys.stderr)
    if args.dry_run:
        for detail_url in detail_urls:
            print(detail_url)
        return 0

    images_dir.mkdir(parents=True, exist_ok=True)

    with metadata_path.open("w", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "object_id",
            "title",
            "date",
            "photographer",
            "studio",
            "archive",
            "license",
            "attribution",
            "detail_url",
            "image_url",
            "file",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for index, detail_url in enumerate(detail_urls, start=1):
            print(f"[{index}/{len(detail_urls)}] {detail_url}", file=sys.stderr)
            try:
                page_html = fetch_text(opener, detail_url)
            except (HTTPError, URLError, TimeoutError) as exc:
                print(f"  Error leyendo ficha: {exc}", file=sys.stderr)
                continue

            object_id = extract_object_id(detail_url)
            title = extract_title(page_html)
            image_url = extract_image_url(page_html)
            photographer = extract_field(page_html, ["ARGAZKILARIA", "Argazkilaria", "AUTOR", "Autor"])
            studio = extract_field(page_html, ["ESTUDIOA", "Estudioa", "ESTUDIO", "Estudio"])
            archive = extract_field(page_html, ["Artxiboa", "ARCHIVO", "Archivo"])
            date = extract_date(page_html)

            filename = ""
            if image_url:
                filename = f"{object_id}-{safe_filename(title)}{extension_from_url(image_url)}"
                destination = images_dir / filename
                if not destination.exists():
                    try:
                        time.sleep(args.delay)
                        download_file(opener, image_url, destination)
                    except (HTTPError, URLError, TimeoutError) as exc:
                        print(f"  Error descargando imagen: {exc}", file=sys.stderr)
                        filename = ""
            else:
                print("  Sin URL de imagen original.", file=sys.stderr)

            row = {
                "object_id": object_id,
                "title": title,
                "date": date,
                "photographer": photographer,
                "studio": studio,
                "archive": archive,
                "license": LICENSE,
                "detail_url": detail_url,
                "image_url": image_url,
                "file": f"images/{filename}" if filename else "",
            }
            row["attribution"] = build_attribution(row)
            writer.writerow(row)
            csv_file.flush()

            if index < len(detail_urls):
                time.sleep(args.delay)

    print(f"Metadatos: {metadata_path}", file=sys.stderr)
    print(f"Imagenes: {images_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
