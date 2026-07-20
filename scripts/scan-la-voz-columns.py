#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path


SOURCE = Path("/home/gaizka/Descargas/Alarde de San Marcial/La Voz de Guipuzcoa - Diario Republicano")
OUT = Path("/tmp/la-voz-guipuzcoa-columns")
SKIP = {"La Voz de Guipúzcoa diario republicano - 01-07-1900.pdf"}
TERMS = [
    "alarde",
    "san marcial",
    "irun",
    "irún",
    "cantiner",
    "hacher",
    "archer",
    "caballer",
    "artiller",
    "infanter",
    "tambor",
    "pif",
    "pedr",
    "general",
    "romer",
]


def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def image_size(path):
    result = run(["identify", "-format", "%w %h", str(path)], capture_output=True, text=True)
    width, height = result.stdout.split()
    return int(width), int(height)


def ocr_image(path, out_base, psm):
    txt = out_base.with_suffix(".txt")
    if not txt.exists():
        run(
            ["tesseract", str(path), str(out_base), "-l", "spa", "--psm", str(psm)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return txt.read_text(errors="replace")


def hit_snippets(text, width=180):
    lower = text.lower()
    hits = []
    for term in TERMS:
        pos = lower.find(term)
        if pos >= 0:
            a = max(0, pos - width)
            b = min(len(text), pos + len(term) + width)
            hits.append(normalize(text[a:b]))
    deduped = []
    seen = set()
    for hit in hits:
        key = hit[:120]
        if key not in seen:
            seen.add(key)
            deduped.append(hit)
    return deduped


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--dpi", type=int, default=170)
    parser.add_argument("--first-page", type=int, default=1)
    parser.add_argument("--last-page", type=int, default=2)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--psm", default="6")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(p for p in SOURCE.glob("*.pdf") if p.name not in SKIP)
    summary_lines = ["# La Voz de Guipuzcoa, escaneo por columnas", ""]

    for idx, pdf in enumerate(pdfs, 1):
        safe = pdf.stem.replace(" ", "_")
        pdf_dir = args.out / safe
        pages_dir = pdf_dir / "pages"
        crops_dir = pdf_dir / "crops"
        ocr_dir = pdf_dir / "ocr"
        full = pdf_dir / "full.txt"
        pages_dir.mkdir(parents=True, exist_ok=True)
        crops_dir.mkdir(exist_ok=True)
        ocr_dir.mkdir(exist_ok=True)

        if not full.exists():
            prefix = pages_dir / "page"
            run([
                "pdftoppm",
                "-r",
                str(args.dpi),
                "-png",
                "-f",
                str(args.first_page),
                "-l",
                str(args.last_page),
                str(pdf),
                str(prefix),
            ])
            chunks = []
            for page_img in sorted(pages_dir.glob("page-*.png")):
                page_num = int(page_img.stem.split("-")[-1])
                width, height = image_size(page_img)
                col_w = width // args.columns
                overlap = max(30, col_w // 10)
                for col in range(args.columns):
                    x = max(0, col * col_w - overlap)
                    right = width if col == args.columns - 1 else min(width, (col + 1) * col_w + overlap)
                    crop = crops_dir / f"p{page_num:02d}_c{col + 1:02d}.png"
                    if not crop.exists():
                        run([
                            "magick",
                            str(page_img),
                            "-crop",
                            f"{right - x}x{height}+{x}+0",
                            "+repage",
                            "-colorspace",
                            "Gray",
                            "-sharpen",
                            "0x0.7",
                            str(crop),
                        ])
                    text = ocr_image(crop, ocr_dir / crop.stem, args.psm)
                    chunks.append(f"\n===== PAGINA {page_num} COLUMNA {col + 1} =====\n{text}")
            full.write_text("".join(chunks), encoding="utf-8")

        text = full.read_text(errors="replace")
        hits = hit_snippets(text)
        summary_lines.append(f"## {pdf.name}")
        summary_lines.append("")
        summary_lines.append(f"- OCR: `{full}`")
        if hits:
            summary_lines.append("- Coincidencias:")
            for hit in hits[:10]:
                summary_lines.append(f"  - {hit}")
        else:
            summary_lines.append("- Coincidencias: ninguna")
        summary_lines.append("")
        print(f"[{idx}/{len(pdfs)}] {pdf.name}: {len(hits)}", flush=True)

    summary = args.out / "summary.md"
    summary.write_text("\n".join(summary_lines), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
