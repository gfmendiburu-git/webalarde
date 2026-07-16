#!/usr/bin/env python3
import argparse
import csv
import re
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_INPUT = "data/irun-fototeca-alarde-irun-resultados.csv"
DEFAULT_OUTPUT = "data/irun-fototeca-alarde-irun-resultados-con-fondo.csv"


EXPLICIT_RULES = [
    (
        "Felipe Iguiñiz",
        re.compile(r"Donaci[oó]n de Felipe(?: Igui[nñ]iz|\.\.\.)?", re.I),
        "Procedencia explícita en descripción web, a veces truncada en el listado",
        "publicable_con_atribucion",
    ),
    (
        "Matías Guilló",
        re.compile(r"Donaci[oó]n de Mat[ií]as(?: Guill[oó]|\.\.\.)?", re.I),
        "Procedencia explícita en descripción web, a veces truncada en el listado",
        "publicable_con_atribucion",
    ),
    (
        "Familia Aguirreche",
        re.compile(r"Donaci[oó]n de (?:la )?(?:familia )?Aguirreche|Familia Aguirreche", re.I),
        "Procedencia explícita en descripción web",
        "publicable_con_atribucion",
    ),
    (
        "Familia Zaragüeta",
        re.compile(r"Donaci[oó]n de (?:la )?(?:familia )?Zarag[uü]eta|Familia Zarag[uü]eta", re.I),
        "Procedencia explícita en descripción web",
        "publicable_con_atribucion",
    ),
]


TRUNCATED_PROVENANCE_RULES = [
    re.compile(r"Donaci[oó]n de\.\.\.", re.I),
    re.compile(r"Original propiedad(?: de)? la\.\.\.", re.I),
    re.compile(r"Original propiedad de la familia\.\.\.", re.I),
    re.compile(r"Imagen cedida por(?: la)?\.\.\.", re.I),
    re.compile(r"Imagen cedida por la familia\.\.\.", re.I),
    re.compile(r"Fotograf[ií]a cedida\.\.\.", re.I),
    re.compile(r"Original cedido\.\.\.", re.I),
]


def image_folder(url):
    parts = urlparse(url or "").path.strip("/").split("/")
    if len(parts) >= 2:
        return parts[-2]
    return ""


def classify(row):
    description = row.get("descripcion", "")
    folder = image_folder(row.get("url_imagen_resultado", ""))

    for fund, pattern, criterion, recommendation in EXPLICIT_RULES:
        if pattern.search(description):
            return fund, "explicito", criterion, recommendation

    for pattern in TRUNCATED_PROVENANCE_RULES:
        if pattern.search(description):
            return (
                "Procedencia truncada o sin identificar",
                "pendiente",
                "La descripción web indica donación, cesión u origen familiar, pero el listado no muestra la procedencia completa",
                "revisar_ficha_o_base_archivo",
            )

    if folder.lower().startswith("fcruz"):
        return (
            "Fondo Kruz",
            "inferido",
            f"Carpeta técnica de imagen: {folder}",
            "requiere_confirmacion_archivo",
        )

    if folder.lower().startswith("postal"):
        return (
            "Postal antigua",
            "inferido",
            f"Carpeta técnica de imagen: {folder}",
            "revisar_fecha_y_confirmar",
        )

    return "", "sin_clasificar", "Sin regla de clasificación", "no_publicar_sin_revision"


def main():
    parser = argparse.ArgumentParser(
        description="Añade clasificación de fondo/procedencia a resultados de la Fototeca de Irun."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    fieldnames = list(rows[0].keys()) + [
        "carpeta_imagen",
        "fondo_o_procedencia",
        "tipo_clasificacion",
        "criterio_clasificacion",
        "uso_recomendado",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            folder = image_folder(row.get("url_imagen_resultado", ""))
            fund, kind, criterion, recommendation = classify(row)
            enriched = dict(row)
            enriched.update(
                {
                    "carpeta_imagen": folder,
                    "fondo_o_procedencia": fund,
                    "tipo_clasificacion": kind,
                    "criterio_clasificacion": criterion,
                    "uso_recomendado": recommendation,
                }
            )
            writer.writerow(enriched)

    print(f"Escrito {output_path} con {len(rows)} filas")


if __name__ == "__main__":
    main()
