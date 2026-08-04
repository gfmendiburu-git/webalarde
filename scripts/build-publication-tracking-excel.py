#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


DEFAULT_ROOT = Path("/home/gaizka/Descargas/Alarde de San Marcial")
DEFAULT_OUTPUT = Path("/tmp/seguimiento_publicaciones_alarde.xlsx")
INCLUDE_EXTS = {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"}
EXCLUDE_PARTS = {"Fotos", "Mi web", "Extracciones"}


KNOWN_TITLES = [
    ("el alarde", "El Alarde"),
    ("foto kruz", "Foto Kruz"),
    ("la voz de guipuzcoa", "La Voz de Guipuzcoa - Diario Republicano"),
    ("el eco de irun", "El Eco de Irun"),
    ("el buen combate", "El buen combate"),
    ("novedades revista semanal ilustrada", "Novedades revista semanal ilustrada"),
    ("euskal herria revista bascongada", "Euskal Herria revista bascongada"),
    ("el correo de guipuzcoa", "El Correo de Guipuzcoa"),
    ("el correo del norte", "El Correo del Norte"),
    ("el correo espanol", "El Correo Espanol"),
    ("el pueblo vasco", "El Pueblo Vasco"),
    ("el guipuzcoano", "El Guipuzcoano"),
    ("la libertad", "La Libertad"),
    ("la union liberal", "La Union Liberal"),
    ("la patria", "La Patria"),
    ("el liberal", "El Liberal"),
    ("el dia", "El Dia"),
    ("el diario vasco", "El Diario Vasco"),
    ("la voz de espana", "La Voz de Espana"),
    ("unidad", "Unidad"),
    ("txingudi", "Txingudi"),
    ("egin", "EGIN"),
    ("el bidasoa mexicano", "El Bidasoa Mexicano"),
    ("el bidasoa", "El Bidasoa"),
    ("bidasoan", "Bidasoan"),
    ("irungo jaiak", "Bidasoan"),
    ("san martzial jaiak", "Bidasoan"),
    ("easo", "Easo"),
    ("ecos del jaizkibel", "Ecos del Jaizkibel"),
    ("el pais vasco", "El Pais Vasco"),
    ("la constancia", "La Constancia"),
    ("la informacion", "La Informacion - Diario independiente"),
    ("la informacion - diario independiente", "La Informacion - Diario independiente"),
    ("el irunes", "El Irunes"),
    ("uranzu", "Uranzu"),
    ("la frontera", "La Frontera"),
    ("la voz de irun", "La Voz de Irun"),
    ("txistulari", "Txistulari"),
    ("estampa", "Estampa"),
    ("el figaro", "El Figaro"),
    ("la tribuna", "La Tribuna"),
    ("el urumea", "El Urumea"),
    ("urumea", "El Urumea"),
]


def strip_accents(value: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", value)
        if unicodedata.category(char) != "Mn"
    )


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(value).lower()).strip()


def extract_years(text: str) -> set[int | str]:
    years = {int(y) for y in re.findall(r"(?<!\d)(18\d{2}|19\d{2}|20\d{2})(?!\d)", text)}
    return {year for year in years if 1800 <= year <= 2099}


def extract_date_label(text: str) -> str:
    match = re.search(r"(?<!\d)(18\d{2}|19\d{2}|20\d{2})-(\d{2})-(\d{2})(?!\d)", text)
    if match:
        return f"{match.group(2)}-{match.group(3)}"
    return "Sin fecha exacta"


def publication_from_name(name: str) -> str:
    cleaned = re.sub(r"\.[^.]+$", "", name)
    cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}\s+-\s+", "", cleaned)
    cleaned = re.sub(r"^\d{4}\s+-\s+", "", cleaned)
    lowered = norm(cleaned)
    for needle, title in KNOWN_TITLES:
        if lowered.startswith(needle) or needle in lowered:
            return title
    cleaned = re.sub(r"\s+-\s+Año\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+-\s+PH\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+-\s+AEHTE\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+-\s+Recortes\b.*$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+-\s+Especial\b.*$", "", cleaned, flags=re.I)
    return cleaned.strip()


def classify(path: Path, root: Path) -> tuple[str, set[int | str], Path] | None:
    rel = path.relative_to(root)
    parts = rel.parts
    if any(part in EXCLUDE_PARTS for part in parts):
        return None
    if path.suffix.lower() not in INCLUDE_EXTS:
        return None
    if parts[0] == "Alarde de San Marcial en Irún: origen y detalles - Serapio Múgica - 1901":
        return ("Serapio Mugica, Alarde de San Marcial en Irun: origen y detalles", {1901}, rel)
    if parts[0] == "Album gráfico descriptivo del País Vascongado años de 1914-1915 tomo de Guipúzcoa - Creative Commons CC BY-SA 4.0":
        return ("Album grafico descriptivo del Pais Vascongado", {1914, 1915}, rel)
    if parts[0] == "Alarde de San Marcial origen y evolucion - Sagrario Arrizabalaga Marin - Recortes":
        years = extract_years(str(rel)) or {"Sin año"}
        return ("Sagrario Arrizabalaga Marin, Alarde de San Marcial: origen y evolucion", years, rel)
    if parts[0] == "Programas de fiestas":
        return ("Programas de fiestas", extract_years(path.name) or {"Sin año"}, rel)
    if parts[0] == "Ordenanzas":
        return ("Ordenanzas", extract_years(path.name) or {"Sin año"}, rel)
    if parts[0] == "Cuentas municipales":
        return ("Cuentas municipales", extract_years(path.name) or {"Sin año"}, rel)
    if parts[0] == "Facebook Buenos Amigos":
        return ("Facebook Buenos Amigos", extract_years(str(rel)) or {"Sin año"}, rel)
    publication = publication_from_name(path.name)
    return (publication, extract_years(str(rel)) or {"Sin año"}, rel)


def collect(root: Path):
    matrix: dict[str, set[int | str]] = defaultdict(set)
    details = []
    seen_book_pages = set()

    for path in sorted(root.rglob("*")):
        info = classify(path, root)
        if not info:
            continue
        publication, years, rel = info
        key = (publication, tuple(sorted(str(year) for year in years)))
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"} and publication.startswith(("Serapio", "Album")):
            if key in seen_book_pages:
                continue
            seen_book_pages.add(key)
        for year in years:
            matrix[publication].add(year)
        details.append(
            {
                "publication": publication,
                "years": ", ".join(str(year) for year in sorted(years, key=str)),
                "year_values": years,
                "date": extract_date_label(str(rel)),
                "path": str(rel),
                "status": "Pendiente" if "Pdte revisar" in rel.parts else "Archivado",
            }
        )

    return matrix, details


def build_workbook(root: Path, output: Path) -> None:
    matrix, details = collect(root)
    years = sorted({year for values in matrix.values() for year in values}, key=lambda value: (value == "Sin año", str(value)))
    publications = sorted(matrix.keys(), key=norm)
    details_by_publication: dict[str, list[dict]] = defaultdict(list)
    for item in details:
        details_by_publication[item["publication"]].append(item)

    wb = Workbook()
    ws = wb.active
    ws.title = "Matriz publicaciones"
    ws.cell(1, 1, "Año")
    for col, publication in enumerate(publications, start=2):
        ws.cell(1, col, publication)
    for row, year in enumerate(years, start=2):
        ws.cell(row, 1, year)
        for col, publication in enumerate(publications, start=2):
            if year in matrix[publication]:
                ws.cell(row, col, "x")

    header_fill = PatternFill("solid", fgColor="B00020")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="bottom", textRotation=90, wrap_text=True)
        cell.border = border
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 170

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    ws.column_dimensions["A"].width = 10
    for col in range(2, len(publications) + 2):
        ws.column_dimensions[get_column_letter(col)].width = 5

    summary = wb.create_sheet("Resumen")
    summary.append(["Dato", "Valor"])
    summary.append(["Publicaciones", len(publications)])
    summary.append(["Años / filas", len(years)])
    summary.append(["Archivos considerados", len(details)])
    summary.append(["Pestañas por publicación", len(publications)])
    summary.append(["Carpeta base", str(root)])
    summary.append(["Criterio matriz", "x indica que existe al menos un archivo de esa publicacion asociado a ese año."])
    summary.append(["Criterio pestañas", "En cada publicacion, las filas son años y las columnas son fechas dia-mes detectadas en los nombres de archivo."])
    for cell in summary[1]:
        cell.fill = header_fill
        cell.font = header_font
    summary.column_dimensions["A"].width = 24
    summary.column_dimensions["B"].width = 120

    publication_sheet_names = []
    for publication in publications:
        sheet_name = create_publication_sheet(
            wb,
            publication,
            details_by_publication[publication],
            header_fill,
            header_font,
            border,
        )
        publication_sheet_names.append((publication, sheet_name))

    index_ws = wb.create_sheet("Indice publicaciones", 2)
    index_ws.append(["Publicacion", "Pestaña"])
    for publication, sheet_name in publication_sheet_names:
        index_ws.append([publication, sheet_name])
    for cell in index_ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    index_ws.freeze_panes = "A2"
    index_ws.auto_filter.ref = index_ws.dimensions
    index_ws.column_dimensions["A"].width = 64
    index_ws.column_dimensions["B"].width = 36

    detail_ws = wb.create_sheet("Detalle archivos")
    detail_ws.append(["Publicacion", "Años detectados", "Fecha columna", "Estado", "Ruta relativa"])
    for item in details:
        detail_ws.append([item["publication"], item["years"], item["date"], item["status"], item["path"]])
    for cell in detail_ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    detail_ws.freeze_panes = "A2"
    detail_ws.auto_filter.ref = detail_ws.dimensions
    detail_ws.column_dimensions["A"].width = 48
    detail_ws.column_dimensions["B"].width = 18
    detail_ws.column_dimensions["C"].width = 18
    detail_ws.column_dimensions["D"].width = 14
    detail_ws.column_dimensions["E"].width = 120
    table = Table(displayName="DetalleArchivos", ref=detail_ws.dimensions)
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    detail_ws.add_table(table)

    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    print(output)
    print(f"{len(publications)} publicaciones, {len(years)} filas de año, {len(details)} archivos considerados")


def safe_sheet_name(name: str, used: set[str]) -> str:
    cleaned = re.sub(r"[\[\]:*?/\\]", " ", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip() or "Publicacion"
    base = cleaned[:31]
    candidate = base
    index = 2
    while candidate in used:
        suffix = f" {index}"
        candidate = f"{base[:31 - len(suffix)]}{suffix}"
        index += 1
    used.add(candidate)
    return candidate


def date_sort_key(value: str):
    if value == "Sin fecha exacta":
        return (1, value)
    match = re.match(r"(\d{2})-(\d{2})$", value)
    if match:
        return (0, int(match.group(1)), int(match.group(2)))
    return (0, value)


def create_publication_sheet(
    wb: Workbook,
    publication: str,
    items: list[dict],
    header_fill: PatternFill,
    header_font: Font,
    border: Border,
) -> str:
    if not hasattr(wb, "_publication_sheet_names"):
        wb._publication_sheet_names = set(wb.sheetnames)
    ws = wb.create_sheet(safe_sheet_name(publication, wb._publication_sheet_names))
    years = sorted(
        {year for item in items for year in item["year_values"]},
        key=lambda value: (value == "Sin año", str(value)),
    )
    dates = sorted({item["date"] for item in items}, key=date_sort_key)
    paths_by_cell = defaultdict(list)
    for item in items:
        for year in item["year_values"]:
            paths_by_cell[(year, item["date"])].append(item["path"])

    ws.cell(1, 1, "Año")
    for col, date in enumerate(dates, start=2):
        ws.cell(1, col, date)
    for row, year in enumerate(years, start=2):
        ws.cell(row, 1, year)
        for col, date in enumerate(dates, start=2):
            paths = paths_by_cell.get((year, date), [])
            if paths:
                ws.cell(row, col, "x")
                ws.cell(row, col).comment = None

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="bottom", textRotation=90, wrap_text=True)
        cell.border = border
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 90
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = border
            cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    ws.column_dimensions["A"].width = 10
    for col in range(2, len(dates) + 2):
        ws.column_dimensions[get_column_letter(col)].width = 5
    return ws.title


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera el Excel de seguimiento de publicaciones por año.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_workbook(args.root, args.output)


if __name__ == "__main__":
    main()
