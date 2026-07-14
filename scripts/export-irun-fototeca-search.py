#!/usr/bin/env python3
import argparse
import csv
import html
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote_plus, urljoin


BASE_URL = "https://www.irun.org"
SEARCH_PATH = "/archivo/fototeca_resultado.asp"
DEFAULT_TEXT = "alarde irun"


def fetch(url, retries=3, delay=0.5):
    last_error = None
    for attempt in range(retries):
        try:
            return fetch_with_curl(url)
        except Exception as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(delay * (attempt + 1))
    raise RuntimeError(f"No se pudo descargar {url}: {last_error}")


def fetch_with_curl(url):
    completed = subprocess.run(
        [
            "curl",
            "-L",
            "--silent",
            "--show-error",
            "--fail",
            "--retry",
            "3",
            "--max-time",
            "45",
            "--user-agent",
            "Mozilla/5.0 (compatible; webalarde-reference-export/1.0)",
            url,
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout.decode("iso-8859-1", errors="replace")


def search_url(text, offset=0):
    query = (
        f"tema=&texto={quote_plus(text)}&referencia=&ano=&buscar=BUSCAR"
        f"&offset={offset}"
    )
    return f"{BASE_URL}{SEARCH_PATH}?{query}"


def clean_text(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_total(page):
    match = re.search(r"<strong>\s*[\d.-]+\s*</strong>\s+de\s+<strong>\s*(\d+)\s*</strong>", page)
    if not match:
        raise RuntimeError("No se ha podido localizar el total de resultados.")
    return int(match.group(1))


def parse_results(page, text):
    results = []
    blocks = re.findall(r'<div class="foto_archivo">(.*?)</div>\s*</div>', page, flags=re.S)
    for block in blocks:
        ref_match = re.search(r"referencia=(\d+)", block)
        if not ref_match:
            continue

        ref = ref_match.group(1)
        img_match = re.search(r'<img\s+src="([^"]+)"', block, flags=re.S)
        year_match = re.search(r"<span>\s*A[^<]*o foto:\s*</span>\s*(.*?)</li>", block, flags=re.S | re.I)
        desc_match = re.search(r"<span>\s*Descripci[^<]*n:\s*</span>\s*(.*?)</li>", block, flags=re.S | re.I)

        ficha_path = f"/archivo/fototeca_ficha.asp?texto={quote_plus(text)}&ref=&ano=&offset=&referencia={ref}"
        results.append(
            {
                "referencia": ref,
                "ano_foto": clean_text(year_match.group(1) if year_match else ""),
                "descripcion": clean_text(desc_match.group(1) if desc_match else ""),
                "url_ficha": urljoin(BASE_URL, ficha_path),
                "url_imagen_resultado": urljoin(BASE_URL, html.unescape(img_match.group(1))) if img_match else "",
            }
        )
    return results


def write_outputs(rows, csv_path, txt_path, unique_txt_path, duplicates_csv_path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    unique_txt_path.parent.mkdir(parents=True, exist_ok=True)
    duplicates_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "referencia",
                "ano_foto",
                "descripcion",
                "url_ficha",
                "url_imagen_resultado",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    with txt_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(f"{row['referencia']}\n")

    seen = set()
    unique_rows = []
    duplicate_rows = []
    for row in rows:
        if row["referencia"] in seen:
            duplicate_rows.append(row)
        else:
            seen.add(row["referencia"])
            unique_rows.append(row)

    with unique_txt_path.open("w", encoding="utf-8") as handle:
        for row in unique_rows:
            handle.write(f"{row['referencia']}\n")

    with duplicates_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "referencia",
                "ano_foto",
                "descripcion",
                "url_ficha",
                "url_imagen_resultado",
            ],
        )
        writer.writeheader()
        writer.writerows(duplicate_rows)

    return len(unique_rows), len(duplicate_rows)


def main():
    parser = argparse.ArgumentParser(
        description="Exporta referencias de resultados de la Fototeca del Archivo Municipal de Irun."
    )
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Texto libre de búsqueda.")
    parser.add_argument("--sleep", type=float, default=0.2, help="Pausa entre páginas, en segundos.")
    parser.add_argument("--csv", default="data/irun-fototeca-alarde-irun-resultados.csv")
    parser.add_argument("--txt", default="data/irun-fototeca-alarde-irun-referencias-todas.txt")
    parser.add_argument("--unique-txt", default="data/irun-fototeca-alarde-irun-referencias-unicas.txt")
    parser.add_argument("--duplicates-csv", default="data/irun-fototeca-alarde-irun-referencias-duplicadas.csv")
    args = parser.parse_args()

    first_page = fetch(search_url(args.text, 0))
    total = parse_total(first_page)
    rows = []
    seen = set()

    for offset in range(0, total, 12):
        page = first_page if offset == 0 else fetch(search_url(args.text, offset))
        for row in parse_results(page, args.text):
            seen.add(row["referencia"])
            rows.append(row)
        print(
            f"{min(offset + 12, total)}/{total} resultados revisados; {len(rows)} filas; {len(seen)} referencias únicas",
            flush=True,
        )
        if offset + 12 < total:
            time.sleep(args.sleep)

    rows.sort(key=lambda item: int(item["referencia"]))
    unique_count, duplicate_count = write_outputs(
        rows,
        Path(args.csv),
        Path(args.txt),
        Path(args.unique_txt),
        Path(args.duplicates_csv),
    )

    if len(rows) != total:
        print(f"AVISO: la búsqueda indica {total} resultados, pero se han extraído {len(rows)} filas.")
    if unique_count != len(rows):
        print(f"AVISO: hay {duplicate_count} fila(s) duplicada(s); {unique_count} referencias únicas.")
    print(f"CSV: {args.csv}")
    print(f"TXT: {args.txt}")
    print(f"TXT único: {args.unique_txt}")
    print(f"Duplicadas: {args.duplicates_csv}")


if __name__ == "__main__":
    main()
