#!/usr/bin/env python3
"""Build the master documentary catalog for the Alarde corpus.

The catalog is intentionally different from the OCR trace:

- one row per PDF/document;
- all documents remain present, even when OCR gives no useful text;
- human-curated index entries are preferred over automatic passages;
- automatic text/OCR matches are kept as finding aids, not as proof.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = SITE_ROOT / "docs" / "catalogo-documental-sanmarcialero.csv"
TRACKING_CSV = SITE_ROOT / "docs" / "rastreo-documentos-articulos.csv"
PASSAGES_CSV = SITE_ROOT / "docs" / "indice-articulos-sanmarcialeros.csv"
CURATED_MD = SITE_ROOT / "docs" / "indice-articulos-sanmarcialeros.md"
CORPUS_ROOT = Path("/home/gaizka/Alarde")


FIELDS = [
    "ID",
    "Año",
    "Fecha",
    "Publicacion",
    "Fecha o numero fuente",
    "Tipo documental",
    "Ruta",
    "Estado del indice real",
    "Calidad de lectura",
    "Entradas curadas",
    "Pasajes automaticos",
    "Pasajes OCR",
    "Paginas detectadas",
    "Temas",
    "Uso en la web",
    "Resumen para indice",
    "Observaciones",
]


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def date_from_path(path: str, fallback: str) -> tuple[str, str]:
    for value in (Path(path).name, fallback, path):
        match = re.search(r"(?P<year>18\d{2}|19\d{2}|20\d{2})(?:[-_/ ](?P<month>\d{2})(?:[-_/ ](?P<day>\d{2}))?)?", value)
        if match:
            year = match.group("year")
            month = match.group("month")
            day = match.group("day")
            if month and day:
                return year, f"{year}-{month}-{day}"
            return year, year
    return "", fallback


def stable_id(path: str) -> str:
    try:
        rel = str(Path(path).relative_to(CORPUS_ROOT))
    except ValueError:
        rel = path
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]


def document_type(path: str, publication: str) -> str:
    lower = f"{path} {publication}".lower()
    if "programas de fiestas" in lower:
        return "Programa de fiestas"
    if "ordenanza" in lower or "ordenanzas" in lower:
        return "Ordenanza"
    if "cuentas municipales" in lower:
        return "Documento municipal"
    if "serapio" in lower or "sagrario arrizabalaga" in lower or "album gráfico" in lower or "album grafico" in lower:
        return "Libro o recorte de libro"
    if "fototeca" in lower or "foto" in lower:
        return "Fuente fotografica"
    if "revistas y periodicos" in lower:
        return "Prensa o revista"
    if "el irunes" in lower or "bidasoan" in lower or "diario" in lower or "bidasoa" in lower:
        return "Prensa o revista"
    return "Documento"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
            }
        )
    return rows


def normalize_location(location: str) -> str:
    return compact(location).split("#page=", 1)[0].strip("`")


def matches_document(location: str, document: str) -> bool:
    loc = normalize_location(location)
    if not loc or loc.startswith("http"):
        return False
    doc = str(Path(document))
    # Curated rows sometimes point to a folder instead of a concrete PDF.
    return doc == loc or doc.startswith(loc.rstrip("/") + "/")


def aggregate_passages(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    by_doc: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "automatic": 0,
            "ocr": 0,
            "themes": set(),
            "uses": set(),
            "pages": set(),
            "summaries": [],
        }
    )
    for row in rows:
        loc = normalize_location(row["Localizacion / fuente"])
        data = by_doc[loc]
        data["automatic"] += 1
        if "OCR visual" in row["Uso"]:
            data["ocr"] += 1
        for theme in re.split(r",\s*", row.get("Temas", "")):
            if theme:
                data["themes"].add(theme)
        if row.get("Uso"):
            data["uses"].add(row["Uso"])
        page_match = re.search(r"#page=(\d+)", row.get("Localizacion / fuente", ""))
        if page_match:
            data["pages"].add(page_match.group(1))
        title = compact(row.get("Articulo o pasaje", ""))
        if title and len(data["summaries"]) < 5:
            data["summaries"].append(title)
    return by_doc


def aggregate_curated(rows: list[dict[str, str]], documents: list[str]) -> dict[str, dict[str, object]]:
    by_doc: dict[str, dict[str, object]] = defaultdict(
        lambda: {"count": 0, "themes": set(), "uses": set(), "summaries": []}
    )
    for row in rows:
        matched = [doc for doc in documents if matches_document(row["Localizacion / fuente"], doc)]
        for doc in matched:
            data = by_doc[doc]
            data["count"] += 1
            for theme in re.split(r",\s*", row.get("Temas", "")):
                if theme:
                    data["themes"].add(theme)
            if row.get("Uso"):
                data["uses"].add(row["Uso"])
            title = compact(row.get("Articulo o pasaje", ""))
            if title and len(data["summaries"]) < 6:
                data["summaries"].append(title)
    return by_doc


def quality_from_tracking(state: str, chars: int) -> str:
    if state == "texto extraido":
        return "Alta: texto extraido del PDF"
    if state == "OCR visual procesado con pasajes":
        return "Media/baja: OCR visual con pasajes detectados"
    if state == "OCR visual procesado sin pasajes":
        return "Media/baja: OCR visual sin pasajes detectados"
    if "timeout" in state:
        return "Baja: OCR visual con timeout; requiere lectura manual"
    if chars > 0:
        return "Baja: OCR visual con texto insuficiente"
    return "Sin texto util; requiere lectura manual"


def status_for(curated_count: int, automatic_count: int, state: str) -> str:
    if curated_count:
        return "Indice real iniciado con entrada curada"
    if automatic_count:
        return "Catalogado con pistas automaticas pendientes de verificacion"
    if "timeout" in state:
        return "Catalogado; requiere OCR mejorado o lectura manual"
    return "Catalogado; pendiente de indice humano"


def build_catalog(output: Path) -> None:
    tracking = read_csv(TRACKING_CSV)
    passages = read_csv(PASSAGES_CSV)
    curated = parse_curated_markdown(CURATED_MD)
    documents = [row["Documento"] for row in tracking]
    passage_by_doc = aggregate_passages(passages)
    curated_by_doc = aggregate_curated(curated, documents)

    catalog_rows: list[dict[str, str]] = []
    for row in tracking:
        doc = row["Documento"]
        year, date = date_from_path(doc, row["Fecha / numero"])
        chars = int(row.get("Caracteres extraidos") or 0)
        auto = passage_by_doc.get(doc, {})
        # If rows were indexed by page-stripped concrete path, this direct key works.
        auto_count = int(auto.get("automatic", 0))
        ocr_count = int(auto.get("ocr", 0))
        curated_data = curated_by_doc.get(doc, {})
        curated_count = int(curated_data.get("count", 0))
        themes = sorted(set(auto.get("themes", set())) | set(curated_data.get("themes", set())))
        uses = sorted(set(auto.get("uses", set())) | set(curated_data.get("uses", set())))
        summaries = list(curated_data.get("summaries", [])) or list(auto.get("summaries", []))
        pages = sorted(auto.get("pages", set()), key=lambda value: int(value))
        state = row["Estado de texto"]
        catalog_rows.append(
            {
                "ID": stable_id(doc),
                "Año": year,
                "Fecha": date,
                "Publicacion": row["Publicacion"],
                "Fecha o numero fuente": row["Fecha / numero"],
                "Tipo documental": document_type(doc, row["Publicacion"]),
                "Ruta": doc,
                "Estado del indice real": status_for(curated_count, auto_count, state),
                "Calidad de lectura": quality_from_tracking(state, chars),
                "Entradas curadas": str(curated_count),
                "Pasajes automaticos": row["Pasajes localizados"],
                "Pasajes OCR": str(ocr_count),
                "Paginas detectadas": ", ".join(pages[:25]) + (" ..." if len(pages) > 25 else ""),
                "Temas": ", ".join(themes),
                "Uso en la web": " | ".join(uses),
                "Resumen para indice": " | ".join(summaries),
                "Observaciones": "Todos los documentos del catalogo forman parte del corpus sanmarcialero local; las pistas automaticas deben contrastarse con la fuente original.",
            }
        )

    catalog_rows.sort(key=lambda item: (item["Año"] or "9999", item["Fecha"], item["Publicacion"], item["Ruta"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(catalog_rows)

    print(f"Catalogo generado: {output}")
    print(f"Documentos: {len(catalog_rows)}")
    print(f"Con entrada curada: {sum(1 for row in catalog_rows if int(row['Entradas curadas']) > 0)}")
    print(f"Con pistas automaticas: {sum(1 for row in catalog_rows if int(row['Pasajes automaticos']) > 0)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_catalog(args.output)


if __name__ == "__main__":
    main()
