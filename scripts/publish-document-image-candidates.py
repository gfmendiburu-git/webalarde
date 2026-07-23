#!/usr/bin/env python3
"""Publish reviewed document image candidates into the public gallery data."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SITE_ROOT / "data" / "document-recortes-candidatos.json"
ALARD_IMAGES = SITE_ROOT / "data" / "alarde-imagenes.json"
CANTINERA_PHOTOS = SITE_ROOT / "data" / "cantinera-fotos.json"


def norm_key(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).strip()


def load_json(path: Path, fallback):
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gallery_item(candidate: dict) -> dict:
    return {
        "source": "document-recorte",
        "object_id": candidate["id"],
        "title": candidate.get("title") or "Recorte documental del Alarde de San Marcial",
        "date": candidate.get("year") or "",
        "year": candidate.get("year") or "sin-fecha",
        "photographer": "",
        "studio": candidate.get("source_folder", ""),
        "archive": "Documentación histórica local",
        "license": candidate.get("rights_status", "revisar"),
        "attribution": candidate.get("attribution", ""),
        "detail_url": "",
        "source_file": candidate.get("source_file", ""),
        "source_page": candidate.get("source_page", ""),
        "full": candidate["full"],
        "thumb": candidate["thumb"],
    }


def merge_gallery(candidates: list[dict]) -> int:
    items = load_json(ALARD_IMAGES, [])
    existing = {item.get("object_id") for item in items if item.get("source") == "document-recorte"}
    added = 0
    for candidate in candidates:
        if candidate["id"] in existing:
            continue
        items.append(gallery_item(candidate))
        existing.add(candidate["id"])
        added += 1
    items.sort(key=lambda item: (item.get("year") or "9999", item.get("object_id") or ""))
    save_json(ALARD_IMAGES, items)
    return added


def merge_cantineras(candidates: list[dict]) -> int:
    data = load_json(CANTINERA_PHOTOS, {"source": "Fotografías identificadas", "entries": []})
    entries = {entry["id"]: entry for entry in data.get("entries", [])}
    added = 0

    for candidate in candidates:
        matches = candidate.get("cantinera_matches") or []
        if not matches:
            continue
        photo = gallery_item(candidate)
        for match in matches:
            key = f"{match.get('year')}|{match.get('company')}|{norm_key(match.get('name', ''))}"
            entry = entries.get(key)
            if not entry:
                entry = {
                    "id": key,
                    "year": match.get("year"),
                    "company": match.get("company"),
                    "name": match.get("name"),
                    "profile": photo,
                    "photos": [],
                }
                entries[key] = entry
            if not any(item.get("object_id") == candidate["id"] and item.get("source") == "document-recorte" for item in entry["photos"]):
                entry["photos"].append(photo)
                added += 1
            if not entry.get("profile"):
                entry["profile"] = photo

    data["entries"] = sorted(entries.values(), key=lambda item: (int(item.get("year") or 9999), item.get("company") or "", item.get("name") or ""))
    save_json(CANTINERA_PHOTOS, data)
    return added


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--status", default="aprobado-publicar", help="Only publish candidates with this review_status.")
    args = parser.parse_args()

    manifest = load_json(args.manifest, {"entries": []})
    candidates = [
        item for item in manifest.get("entries", [])
        if item.get("review_status") == args.status and item.get("publishable_by_policy")
    ]

    gallery_added = merge_gallery(candidates)
    cantineras_added = merge_cantineras(candidates)
    print(json.dumps({
        "approved_candidates": len(candidates),
        "gallery_added": gallery_added,
        "cantineras_photos_added": cantineras_added,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
