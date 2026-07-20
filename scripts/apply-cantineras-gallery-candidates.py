#!/usr/bin/env python3
import json
import unicodedata
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
CANDIDATES = SITE.parent / "data-internal" / "cantineras-gallery-candidates.json"
CANTINERAS = SITE / "data" / "cantineras.json"


def strip_accents(text):
    return "".join(
        ch for ch in unicodedata.normalize("NFD", text or "") if unicodedata.category(ch) != "Mn"
    )


def norm(text):
    return " ".join(
        "".join(ch.lower() if ch.isalnum() else " " for ch in strip_accents(text)).split()
    )


def score(record):
    name = record["name"]
    first_title = record["sources"][0].get("title", "")
    return (
        len(name.split()),
        len(name),
        len(record["sources"]),
        1 if first_title.lower().startswith("retrato de") else 0,
    )


def main():
    data = json.loads(CANTINERAS.read_text(encoding="utf-8"))
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    existing_exact = {
        (entry.get("year"), norm(entry.get("company")), norm(entry.get("name")))
        for entry in data["entries"]
    }
    existing_year_company = {
        (entry.get("year"), entry.get("company"))
        for entry in data["entries"]
    }

    grouped = {}
    for candidate in candidates:
        if candidate.get("exists"):
            continue
        key = (candidate.get("year"), norm(candidate.get("company")), norm(candidate.get("name")))
        if key in existing_exact:
            continue
        year_company = (candidate.get("year"), candidate.get("company"))
        if year_company in existing_year_company:
            continue
        grouped.setdefault(year_company, []).append(candidate)

    additions = []
    for records in grouped.values():
        chosen = sorted(records, key=score, reverse=True)[0]
        titles = []
        refs = []
        refs_seen = set()
        for source in chosen["sources"]:
            title = source.get("title") or ""
            if title and title not in titles:
                titles.append(title)
            ref_key = (source.get("object_id"), title, source.get("date"))
            if ref_key in refs_seen:
                continue
            refs_seen.add(ref_key)
            refs.append(
                {
                    "object_id": source.get("object_id"),
                    "title": title,
                    "date": source.get("date"),
                    "source": source.get("source"),
                    "archive": source.get("archive"),
                    "license": source.get("license"),
                }
            )

        additions.append(
            {
                "year": chosen["year"],
                "company": chosen["company"],
                "name": chosen["name"],
                "source_url": "",
                "source_title": f"Metadatos de la galería fotográfica interna: {titles[0]}",
                "mentions": len(refs),
                "needs_review": True,
                "alternatives": [record["name"] for record in records if record["name"] != chosen["name"]],
                "gallery_source_refs": refs,
            }
        )

    data["entries"].extend(additions)
    data["entries"].sort(key=lambda entry: (entry["year"], entry["company"], norm(entry["name"])))
    data["companies"] = sorted({entry["company"] for entry in data["entries"]}, key=norm)
    data["stats"]["entries"] = len(data["entries"])
    data["stats"]["needs_review"] = sum(1 for entry in data["entries"] if entry.get("needs_review"))
    data["stats"]["total_entries"] = len(data["entries"])
    data["stats"]["last_manual_update"] = "2026-07-20"
    data["stats"]["manual_update_note"] = (
        f"Incorporados {len(additions)} huecos de cantineras detectados en metadatos "
        "de la galería fotográfica interna, sin enlazar fotos ni fichas por revisión de permisos."
    )

    CANTINERAS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"additions={len(additions)}")
    for entry in additions:
        print(f"{entry['year']} | {entry['company']} | {entry['name']}")


if __name__ == "__main__":
    main()
