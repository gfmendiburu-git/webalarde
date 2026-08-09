#!/usr/bin/env python3
"""Build a human-readable document-by-document index for manual review."""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SITE_ROOT / "docs" / "indice-revision-manual-sanmarcialero.md"
CATALOG_CSV = SITE_ROOT / "docs" / "catalogo-documental-sanmarcialero.csv"
PASSAGES_CSV = SITE_ROOT / "docs" / "indice-articulos-sanmarcialeros.csv"
CURATED_MD = SITE_ROOT / "docs" / "indice-articulos-sanmarcialeros.md"


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_location(location: str) -> tuple[str, str]:
    clean = compact(location).strip("`")
    if "#page=" in clean:
        path, page = clean.split("#page=", 1)
        return path, page
    return clean, ""


def parse_curated_markdown(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("| Publicacion | Fecha / numero |"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        parts = [compact(part.strip().strip("`")) for part in line.strip("|").split("|")]
        if len(parts) < 6:
            continue
        rows.append(
            {
                "Publicacion": parts[0].strip("*"),
                "Fecha / numero": parts[1],
                "Articulo o pasaje": parts[2],
                "Temas": parts[3],
                "Uso": parts[4],
                "Localizacion / fuente": parts[5],
                "Origen": "Entrada curada",
                "Extracto": "",
            }
        )
    return rows


def matches_document(location: str, document: str) -> bool:
    loc, _page = normalize_location(location)
    if not loc or loc.startswith("http"):
        return False
    doc = str(Path(document))
    return doc == loc or doc.startswith(loc.rstrip("/") + "/")


def group_entries(catalog: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    documents = [row["Ruta"] for row in catalog]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in parse_curated_markdown(CURATED_MD):
        for document in documents:
            if matches_document(row["Localizacion / fuente"], document):
                grouped[document].append(row)

    for row in read_csv(PASSAGES_CSV):
        location, page = normalize_location(row["Localizacion / fuente"])
        if location not in documents:
            continue
        origin = "Pista OCR" if "OCR visual" in row["Uso"] else "Pista automatica"
        grouped[location].append(
            {
                "Publicacion": row["Publicacion"],
                "Fecha / numero": row["Fecha / numero"],
                "Articulo o pasaje": row["Articulo o pasaje"],
                "Temas": row["Temas"],
                "Uso": row["Uso"],
                "Localizacion / fuente": row["Localizacion / fuente"],
                "Origen": origin,
                "Extracto": row.get("Extracto", ""),
                "Pagina": page,
            }
        )

    for entries in grouped.values():
        entries.sort(
            key=lambda item: (
                0 if item["Origen"] == "Entrada curada" else 1,
                int(item.get("Pagina") or 0),
                item["Articulo o pasaje"],
            )
        )
    return grouped


def trim(text: str, limit: int = 360) -> str:
    text = compact(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def render_entry(entry: dict[str, str]) -> list[str]:
    title = entry["Articulo o pasaje"] or "Pasaje pendiente de titular"
    bits = [f"  - {title}"]
    meta = []
    if entry.get("Pagina"):
        meta.append(f"pagina {entry['Pagina']}")
    if entry.get("Temas"):
        meta.append(f"temas: {entry['Temas']}")
    if entry.get("Uso"):
        meta.append(f"uso: {entry['Uso']}")
    if meta:
        bits.append(f"    - {'; '.join(meta)}.")
    return bits


def sort_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    year = row["Año"] or "9999"
    date = row["Fecha"] or row["Fecha o numero fuente"] or "9999"
    return year, date, row["Publicacion"], row["Ruta"]


def build_document(output: Path) -> None:
    catalog = read_csv(CATALOG_CSV)
    entries_by_doc = group_entries(catalog)
    lines = [
        "# Indice manual del corpus sanmarcialero",
        "",
        "Documento de trabajo para revisar manualmente el corpus conservado en `/home/gaizka/Alarde`.",
        "",
        "Cada bloque corresponde a un documento. Las viñetas interiores recogen articulos, cronicas, entrevistas, paginas graficas o pasajes que ya conocemos por el indice curado o por rastreo automatico. Las pistas automaticas y OCR deben verificarse contra el archivo original antes de usarse como fuente.",
        "",
        "## Resumen",
        "",
        f"- Documentos catalogados: {len(catalog)}.",
        f"- Documentos con entradas o pistas conocidas: {sum(1 for row in catalog if entries_by_doc.get(row['Ruta']))}.",
        f"- Documentos pendientes de completar manualmente: {sum(1 for row in catalog if not entries_by_doc.get(row['Ruta']))}.",
        "",
        "## Documentos",
        "",
    ]

    for row in sorted(catalog, key=sort_key):
        filename = Path(row["Ruta"]).name
        heading_date = row["Fecha"] or row["Fecha o numero fuente"] or "Fecha sin normalizar"
        entries = entries_by_doc.get(row["Ruta"], [])
        curated_entries = [entry for entry in entries if entry["Origen"] == "Entrada curada"]
        automatic_entries = [entry for entry in entries if entry["Origen"] != "Entrada curada"]

        lines.extend(
            [
                f"### {heading_date} · {row['Publicacion']}",
                "",
                f"- **Archivo**: `{filename}`",
                f"- **Ruta**: `{row['Ruta']}`",
                f"- **Nombre del documento**: {row['Publicacion']}",
                f"- **Fecha de publicacion**: {row['Fecha o numero fuente']}",
                f"- **Tipo documental**: {row['Tipo documental']}",
                f"- **Estado**: {row['Estado del indice real']}",
                f"- **Calidad de lectura**: {row['Calidad de lectura']}",
                "",
                "  **Entradas conocidas o verificadas**:",
            ]
        )

        if curated_entries:
            for entry in curated_entries:
                lines.extend(render_entry(entry))
        else:
            lines.append("  - Pendiente de completar manualmente.")

        lines.extend(["", "  **Pistas automaticas a revisar**:"])
        if automatic_entries:
            for entry in automatic_entries:
                lines.extend(render_entry(entry))
        else:
            lines.append("  - Sin pistas automaticas registradas.")

        lines.extend(["", "  **Notas de revision manual**:", "  - "])
        lines.append("")

    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Indice manual generado: {output}")
    print(f"Documentos: {len(catalog)}")
    print(f"Con entradas: {sum(1 for row in catalog if entries_by_doc.get(row['Ruta']))}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_document(args.output)


if __name__ == "__main__":
    main()
