#!/usr/bin/env python3
"""Build a searchable cantineras dataset from public archive metadata."""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://veteranosescoltadecaballeria.com/wp-json/wp/v2/posts"
SOURCE_CATEGORY_ID = "9"
DEFAULT_CACHE = Path("../cache/veteranos-irun-cantineras.jsonl")
DEFAULT_OUTPUT = Path("data/cantineras.json")
USER_AGENT = "webalarde-research/1.0"

COMPANIES = [
    ("Escolta de Caballería", [r"Escolta de Caballer[ií]a", r"Escolta Caballer[ií]a", r"Caballer[ií]a"]),
    ("Batería de Artillería", [r"Bater[ií]a de Artiller[ií]a", r"Bateria Artilleria", r"Bater[ií]a Artiller[ií]a", r"Artiller[ií]a"]),
    ("Banda de Música", [r"Banda de M[uú]sica", r"Banda Musica", r"Banda M[uú]sica", r"Banda"]),
    ("Tamborrada", [r"Tamborrada"]),
    ("Ama Shantalen", [r"Ama Shantalen"]),
    ("Anaka", [r"Anaka"]),
    ("Azken Portu", [r"Azken Portu"]),
    ("Behobia", [r"Behobia", r"Bahobia"]),
    ("Belaskoenea", [r"Belaskoenea", r"Beleskoenea"]),
    ("Bidasoa", [r"Bidasoa"]),
    ("Buenos Amigos", [r"Buenos Amigos"]),
    ("Lapice", [r"Lapice", r"L[aá]pice"]),
    ("Meaka", [r"Meaka"]),
    ("Olaberria", [r"Olaberr[ií]a", r"Olaberria"]),
    ("Real Unión", [r"Real Uni[oó]n", r"Real Union"]),
    ("San Miguel", [r"San Miguel"]),
    ("Santiago", [r"Santiago"]),
    ("Uranzu", [r"Uranzu"]),
    ("Ventas", [r"Ventas"]),
    ("Renfe", [r"Renfe"]),
    ("Mendibil", [r"Mendibil"]),
]

EXCLUDED_COMPANY_HINTS = [
    "Pueblo",
    "Semisarga",
    "Olearso",
    "Mendelu",
    "Gora Ama",
    "Gora Ama Guadalupekoa",
    "Jaizubia",
    "Kosta",
    "Arkoll",
    "Akartegi",
    "Gora Gazteak",
]


def clean_text(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value))
    return re.sub(r"\s+", " ", value).strip()


def plain_key(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    normalized = normalized.lower()
    normalized = re.sub(r"\b(mª|ma|maria)\b", "maria", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def fetch_cache(cache_path: Path, delay: float) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text("", encoding="utf-8")
    page = 1
    total_pages = None

    while True:
        params = {
            "categories": SOURCE_CATEGORY_ID,
            "search": "cantinera",
            "per_page": "100",
            "page": str(page),
            "_fields": "id,date,link,title,excerpt,tags,categories",
        }
        request = Request(f"{API_URL}?{urlencode(params)}", headers={"User-Agent": USER_AGENT})
        with urlopen(request, timeout=60) as response:
            if total_pages is None:
                total_pages = int(response.headers.get("X-WP-TotalPages", "1"))
            data = json.loads(response.read().decode("utf-8"))

        with cache_path.open("a", encoding="utf-8") as output:
            for item in data:
                output.write(json.dumps(item, ensure_ascii=False) + "\n")

        if page >= total_pages:
            break
        page += 1
        time.sleep(delay)


def find_company(text: str) -> str:
    for hint in EXCLUDED_COMPANY_HINTS:
        if re.search(r"\b" + re.escape(hint) + r"\b", text, re.IGNORECASE):
            return ""

    for company, patterns in COMPANIES:
        for pattern in patterns:
            contexts = [
                rf"Cantinera\s+(?:de\s+la\s+|del\s+|de\s+)?(?:Compañ[ií]a\s+)?{pattern}\b",
                rf"Elegida\s+Cantinera\s+(?:de\s+la\s+|del\s+|de\s+)?(?:Compañ[ií]a\s+)?{pattern}\b",
                rf"elecci[oó]n\s+(?:de\s+)?Cantinera\s+(?:de\s+la\s+|del\s+|de\s+)?(?:Compañ[ií]a\s+)?{pattern}\b",
                rf"Compañ[ií]a\s+(?:de\s+|del\s+|la\s+)?{pattern}\b",
                rf"Cia\s+{pattern}\b",
            ]
            if any(re.search(context, text, re.IGNORECASE) for context in contexts):
                return company
    return ""


def find_year(text: str) -> int | None:
    match = re.search(r"\b(18\d{2}|19\d{2}|20\d{2})\b", text)
    return int(match.group(1)) if match else None


def extract_name(title: str, text: str, year: int | None) -> str:
    for separator in ("–", "-"):
        if separator in title and re.search(r"Cantinera|Compañ", title, re.IGNORECASE):
            name = clean_name(title.split(separator)[-1])
            if is_probable_name(name):
                return name

    patterns: list[str] = []
    if year:
        patterns.extend(
            [
                rf"Añ[o0]\s*{year}\.?\s*([^\.]+?)\.\s*(?:Fue |Ha sido |Elegida |En la |Cantinera)",
                rf"Añ[o0]\s*{year}\.?\s*([^\.]+?)\.\s*Cantinera",
            ]
        )
    patterns.extend(
        [
            r"^(.*?)\s+elegida\s+Cantinera",
            r"^(.*?)\s+elecci[oó]n\s+(?:de\s+)?Cantinera",
            r"^(.*?)\s+Cantinera\s+(?:de\s+|Compañ[ií]a|Bater[ií]a|Banda|Escolta|Tamborrada)",
            r"^(.*?)\s+Cantinera\b",
        ]
    )

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        name = clean_name(match.group(1))
        name = re.sub(r"^(Año\s*\d{4}\.?\s*)", "", name, flags=re.IGNORECASE).strip()
        if "–" in name:
            name = clean_name(name.split("–")[-1])
        if is_probable_name(name):
            return name
    return ""


def clean_name(value: str) -> str:
    value = value.strip(" .,-–—»«")
    value = re.sub(r"([a-záéíóúüñ])([A-ZÁÉÍÓÚÜÑ])", r"\1 \2", value)
    return re.sub(r"\s+", " ", value).strip()


def is_probable_name(value: str) -> bool:
    words = value.split()
    if not 1 <= len(words) <= 6:
        return False
    return not re.search(
        r"Compañ|Bater|Banda|Escolta|Alarde|Cantinera|Historia|Curiosidades|La figura|Año|Barril",
        value,
        re.IGNORECASE,
    )


def cluster_names(records: list[dict[str, str]]) -> list[list[dict[str, str]]]:
    clusters: list[list[dict[str, str]]] = []
    for record in records:
        key = plain_key(record["name"])
        placed = False
        for cluster in clusters:
            base = plain_key(cluster[0]["name"])
            ratio = SequenceMatcher(None, key, base).ratio()
            if ratio >= 0.86 or key in base or base in key:
                cluster.append(record)
                placed = True
                break
        if not placed:
            clusters.append([record])
    return clusters


def representative(cluster: list[dict[str, str]]) -> dict[str, str]:
    counts = Counter(plain_key(record["name"]) for record in cluster)
    best_key, _ = counts.most_common(1)[0]
    candidates = [record for record in cluster if plain_key(record["name"]) == best_key]
    return max(candidates, key=lambda record: len(record["name"]))


def build_dataset(cache_path: Path) -> dict[str, object]:
    grouped: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    rejected = Counter()

    for line in cache_path.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        title = clean_text(item["title"]["rendered"])
        text = clean_text(f"{item['title']['rendered']} {item['excerpt']['rendered']}")
        if "hondarribia" in plain_key(text):
            rejected["hondarribia"] += 1
            continue

        company = find_company(text)
        year = find_year(text)
        name = extract_name(title, text, year) if company and year else ""
        if not company:
            rejected["no_company"] += 1
            continue
        if not year:
            rejected["no_year"] += 1
            continue
        if not name:
            rejected["no_name"] += 1
            continue

        grouped[(year, company)].append(
            {
                "name": name,
                "source_url": item["link"],
                "source_title": title,
            }
        )

    entries: list[dict[str, object]] = []
    for (year, company), records in sorted(grouped.items()):
        clusters = sorted(cluster_names(records), key=len, reverse=True)
        names = [representative(cluster) for cluster in clusters]
        primary = names[0]
        entries.append(
            {
                "year": year,
                "company": company,
                "name": primary["name"],
                "source_url": primary["source_url"],
                "source_title": primary["source_title"],
                "mentions": len(records),
                "needs_review": len(names) > 1,
                "alternatives": [
                    {
                        "name": alt["name"],
                        "source_url": alt["source_url"],
                        "source_title": alt["source_title"],
                    }
                    for alt in names[1:]
                ],
            }
        )

    return {
        "source": "https://veteranosescoltadecaballeria.com/category/alarde-irun/",
        "scope": "Alarde tradicional de San Marcial de Irun; se excluyen registros ajenos a ese alcance.",
        "companies": [company for company, _ in COMPANIES],
        "entries": entries,
        "stats": {
            "entries": len(entries),
            "needs_review": sum(1 for entry in entries if entry["needs_review"]),
            "rejected": dict(rejected),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build cantineras dataset.")
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--delay", type=float, default=0.2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.refresh or not args.cache.exists():
        fetch_cache(args.cache, args.delay)
    data = build_dataset(args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{data['stats']['entries']} registros escritos en {args.output}")
    print(f"{data['stats']['needs_review']} registros marcados para revisar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
