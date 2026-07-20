#!/usr/bin/env python3
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
GALLERY = SITE / "data" / "alarde-imagenes.json"
CANTINERAS = SITE / "data" / "cantineras.json"
OUT = SITE.parent / "data-internal" / "cantineras-gallery-candidates.json"

COMPANY_ALIASES = {
    "ama shantalen": "Ama Shantalen",
    "anaka": "Anaka",
    "artilleria": "Batería de Artillería",
    "azken portu": "Azken Portu",
    "banda": "Banda de Música",
    "banda de musica": "Banda de Música",
    "batería de artillería": "Batería de Artillería",
    "bateria de artilleria": "Batería de Artillería",
    "behobia": "Behobia",
    "belaskoenea": "Belaskoenea",
    "bidasoa": "Bidasoa",
    "buenos amigos": "Buenos Amigos",
    "caballeria": "Escolta de Caballería",
    "calle mayor": "Calle Mayor",
    "lapice": "Lapice",
    "larretxipi": "Larretxipi",
    "meaka": "Meaka",
    "olaberria": "Olaberria",
    "racing": "Racing Club",
    "racing club": "Racing Club",
    "real union": "Real Unión",
    "san miguel": "San Miguel",
    "santiago": "Santiago",
    "tamborrada": "Tamborrada",
    "uranzu": "Uranzu",
    "urdanibia": "Urdanibia",
    "ventas": "Ventas",
}

STOP_NAMES = {
    "cantinera",
    "joven",
    "niña",
    "retrato",
    "retrato de",
    "integrantes",
    "integrantes y",
    "compañía",
    "compania",
    "el comandante",
}

BAD_NAME_PREFIXES = (
    "compañía ",
    "compania ",
    "el comandante ",
    "integrantes ",
    "integrantes y ",
)


def strip_accents(text):
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn"
    )


def norm(text):
    text = strip_accents(text or "").lower()
    text = re.sub(r"[^a-z0-9ñ ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_case_name(text):
    particles = {"de", "del", "la", "las", "los", "y"}
    words = []
    for word in re.sub(r"\s+", " ", text.strip()).split(" "):
        lower = word.lower()
        words.append(lower if lower in particles else lower.capitalize())
    return " ".join(words)


def clean_name(raw):
    raw = raw.strip(" .,:;-\"'“”¿?()[]")
    raw = re.sub(r"^(retrato de|la cantinera|las cantineras)\s+", "", raw, flags=re.I)
    raw = re.sub(r",?\s+con\s+.*$", "", raw, flags=re.I)
    if norm(raw).startswith(BAD_NAME_PREFIXES):
        return ""
    raw = re.sub(r"\b(reci[eé]n elegida|elegida|saludando|sonriendo|recibiendo.*)$", "", raw, flags=re.I)
    raw = re.sub(r"\b(cantinera|del alarde|de alarde)\b", "", raw, flags=re.I)
    raw = re.sub(r"\s+", " ", raw).strip(" .,:;-\"'“”¿?()[]")
    nraw = norm(raw)
    if not raw or nraw in STOP_NAMES or nraw.startswith(BAD_NAME_PREFIXES):
        return ""
    if " y " in nraw:
        return ""
    if len(raw.split()) < 2:
        return ""
    return title_case_name(raw)


def extract_company(text):
    text = re.split(r"\b(en la|en el|en los|en las|a su paso|durante|accediendo|posando)\b", text, maxsplit=1, flags=re.I)[0]
    text = re.sub(r"\(.*?\)", "", text)
    ntext = norm(text)
    best = ""
    for alias, company in COMPANY_ALIASES.items():
        if alias in ntext and len(alias) > len(best):
            best = alias
            chosen = company
    return chosen if best else ""


def parse_title(title):
    title = title or ""
    candidates = []
    patterns = [
        r"^(?P<name>.+?)\s+reci[eé]n elegida cantinera de\s+(?P<company>.+?)(?:\s+del\b|,|\.|$)",
        r"^(?P<name>.+?)\s*,?\s*cantinera de\s+(?P<company>.+?)(?:\s+del\b|,|\.|$)",
        r"^(?P<name>.+?)\s+cantinera\s+(?P<company>.+?)(?:\s+20\d{2}|,|\.|$)",
        r"^(?P<name>.+?)\.\s*cantinera de\s+(?P<company>.+?)(?:\s+del\b|,|\.|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, flags=re.I)
        if not match:
            continue
        name = clean_name(match.group("name"))
        company = extract_company(match.group("company"))
        if name and company:
            candidates.append((name, company))
    return candidates


def year_from(value):
    text = str(value or "")
    match = re.search(r"(18|19|20)\d{2}", text)
    return int(match.group(0)) if match else None


def main():
    gallery = json.loads(GALLERY.read_text(encoding="utf-8"))
    cantineras = json.loads(CANTINERAS.read_text(encoding="utf-8"))
    existing = {
        (entry.get("year"), norm(entry.get("company")), norm(entry.get("name")))
        for entry in cantineras["entries"]
    }

    grouped = {}
    for item in gallery:
        title = item.get("title", "")
        parsed = parse_title(title)
        if not parsed:
            continue
        year = year_from(item.get("year") or item.get("date") or title)
        for name, company in parsed:
            key = (year, norm(company), norm(name))
            rec = grouped.setdefault(
                key,
                {
                    "year": year,
                    "company": company,
                    "name": name,
                    "exists": key in existing,
                    "sources": [],
                },
            )
            rec["sources"].append(
                {
                    "object_id": item.get("object_id"),
                    "title": title,
                    "date": item.get("date"),
                    "source": item.get("source"),
                    "archive": item.get("archive"),
                    "detail_url": item.get("detail_url"),
                    "license": item.get("license"),
                }
            )

    records = sorted(grouped.values(), key=lambda r: (r["exists"], r["year"] or 9999, r["company"], r["name"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    missing = [r for r in records if not r["exists"]]
    by_company = defaultdict(int)
    for rec in missing:
        by_company[rec["company"]] += 1
    print(f"Candidates: {len(records)}")
    print(f"Missing: {len(missing)}")
    for company, count in sorted(by_company.items()):
        print(f"{company}: {count}")
    print(OUT)


if __name__ == "__main__":
    main()
