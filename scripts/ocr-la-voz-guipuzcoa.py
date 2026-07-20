#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
from pathlib import Path


DEFAULT_SOURCE = Path(
    "/home/gaizka/Descargas/Alarde de San Marcial/La Voz de Guipuzcoa - Diario Republicano"
)
DEFAULT_OUT = Path("/tmp/la-voz-guipuzcoa-ocr")
SKIP = {"La Voz de Guipúzcoa diario republicano - 01-07-1900.pdf"}

PATTERNS = [
    "alarde",
    "san marcial",
    "san-marcial",
    "irun",
    "irún",
    "cantiner",
    "hacher",
    "archer",
    "caballeria",
    "caballería",
    "artiller",
    "infanter",
    "tambor",
    "pifano",
    "pífano",
    "pedros",
    "pedrós",
    "general",
    "romeria",
    "romería",
]


def run(cmd):
    subprocess.run(cmd, check=True)


def pdf_pages(pdf):
    result = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"No page count found for {pdf}")


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def snippets(text, terms, width=180):
    lower = text.lower()
    found = []
    for term in terms:
        start = 0
        term_lower = term.lower()
        while True:
            idx = lower.find(term_lower, start)
            if idx < 0:
                break
            a = max(0, idx - width)
            b = min(len(text), idx + len(term) + width)
            found.append((idx, normalize(text[a:b])))
            start = idx + len(term)
    found.sort(key=lambda item: item[0])
    deduped = []
    seen = set()
    for _, snippet in found:
        key = snippet[:140]
        if key not in seen:
            seen.add(key)
            deduped.append(snippet)
    return deduped[:12]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dpi", type=int, default=210)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--psm", default="6")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    summary = args.out / "summary.md"
    pdfs = sorted(p for p in args.source.glob("*.pdf") if p.name not in SKIP)
    if args.limit:
        pdfs = pdfs[: args.limit]

    lines = ["# OCR La Voz de Guipuzcoa", ""]
    for idx, pdf in enumerate(pdfs, 1):
        safe_name = pdf.stem.replace(" ", "_").replace("/", "_")
        pdf_dir = args.out / safe_name
        pages_dir = pdf_dir / "pages"
        ocr_dir = pdf_dir / "ocr"
        text_file = pdf_dir / "full.txt"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pages_dir.mkdir(exist_ok=True)
        ocr_dir.mkdir(exist_ok=True)

        pages = pdf_pages(pdf)
        if not text_file.exists():
            prefix = pages_dir / "page"
            convert_cmd = ["pdftoppm", "-r", str(args.dpi), "-png"]
            if args.max_pages:
                convert_cmd.extend(["-f", "1", "-l", str(args.max_pages)])
            convert_cmd.extend([str(pdf), str(prefix)])
            run(convert_cmd)
            page_texts = []
            for page_img in sorted(pages_dir.glob("page-*.png")):
                page_num = int(page_img.stem.split("-")[-1])
                if args.max_pages and page_num > args.max_pages:
                    continue
                base = ocr_dir / page_img.stem
                if not base.with_suffix(".txt").exists():
                    subprocess.run(
                        ["tesseract", str(page_img), str(base), "-l", "spa", "--psm", args.psm],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                page_texts.append(f"\n===== PAGINA {page_num} =====\n")
                page_texts.append(base.with_suffix(".txt").read_text(errors="replace"))
            text_file.write_text("".join(page_texts), encoding="utf-8")

        text = text_file.read_text(errors="replace")
        hits = snippets(text, PATTERNS)
        lines.append(f"## {pdf.name}")
        lines.append("")
        lines.append(f"- Paginas: {pages}")
        lines.append(f"- OCR: `{text_file}`")
        if hits:
            lines.append("- Coincidencias:")
            for hit in hits:
                lines.append(f"  - {hit}")
        else:
            lines.append("- Coincidencias: ninguna")
        lines.append("")
        print(f"[{idx}/{len(pdfs)}] {pdf.name}: {len(hits)} snippets")

    summary.write_text("\n".join(lines), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
