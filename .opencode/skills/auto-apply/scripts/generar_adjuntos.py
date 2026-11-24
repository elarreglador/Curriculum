#!/usr/bin/env python3
"""Convierte los Markdown de una candidatura en adjuntos PDF (y DOCX si se pide).

LibreOffice interpreta un .md como texto plano, así que el PDF se genera desde
un HTML temporal. Las imágenes relativas se reescriben como file:// absolutos.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[4]
DEFAULT_TMP = REPO / "SENSIBLE" / "tmp"

CSS = """
@page { size: A4; margin: 1.5cm; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 10.5pt; color: #111; }
h1 { font-size: 16pt; margin: 0 0 8pt 0; }
h2 { font-size: 12pt; margin: 12pt 0 6pt 0; border-bottom: 1px solid #ccc; }
p, li { line-height: 1.35; margin: 3pt 0; }
table { border-collapse: collapse; }
img { max-width: 100%; }
code { font-family: "DejaVu Sans Mono", monospace; background: #f4f4f4; }
"""

IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.IGNORECASE)
MARKDOWN_LEFTovers = re.compile(r"(^\s*#{1,6}\s|\*\*|^\s*---\s*$)", re.MULTILINE)


def absolute_images(html: str, source_dir: Path) -> str:
    """Replace relative image sources with absolute file URIs."""

    def replace(match: re.Match[str]) -> str:
        src = match.group(2)
        if src.startswith(("http://", "https://", "data:", "file://")):
            return match.group(0)
        resolved = (source_dir / src).resolve()
        return f"{match.group(1)}{resolved.as_uri()}{match.group(3)}"

    return IMG_SRC.sub(replace, html)


def build_html(source: Path, tmp_dir: Path) -> Path:
    """Render one Markdown file as a standalone HTML file."""

    text = source.read_text(encoding="utf-8")
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    body = absolute_images(body, source.parent)
    document = (
        "<!DOCTYPE html><html lang=\"es\"><head><meta charset=\"utf-8\">"
        f"<title>{source.stem}</title><style>{CSS}</style></head>"
        f"<body>{body}</body></html>"
    )
    target = tmp_dir / f"{source.stem}.html"
    target.write_text(document, encoding="utf-8")
    return target


def convert(html: Path, output_dir: Path, tmp_dir: Path, formats: list[str]) -> list[Path]:
    """Run LibreOffice headless once per requested format."""

    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    if not libreoffice:
        raise RuntimeError("LibreOffice no está instalado (se buscó libreoffice/soffice)")

    profile = tmp_dir / "libreoffice-profile"
    profile.mkdir(parents=True, exist_ok=True)
    filters = {"pdf": "pdf:writer_pdf_Export", "docx": "docx:MS Word 2007 XML"}
    generated: list[Path] = []

    for fmt in formats:
        target = output_dir / f"{html.stem}.{fmt}"
        if target.exists():
            target.unlink()
        command = [
            libreoffice,
            "--headless",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to",
            filters[fmt],
            "--outdir",
            str(output_dir),
            str(html),
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=180, check=False
        )
        if result.returncode != 0 or not target.exists():
            raise RuntimeError(
                f"Falló la conversión a {fmt}: {result.stdout.strip()} {result.stderr.strip()}"
            )
        generated.append(target)

    return generated


def verify_pdf(pdf: Path) -> str:
    """Check that the PDF does not contain raw Markdown syntax."""

    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return "omitido: pdftotext no disponible"
    result = subprocess.run(
        [pdftotext, str(pdf), "-"], capture_output=True, text=True, check=True
    )
    found = MARKDOWN_LEFTovers.search(result.stdout)
    if found:
        raise RuntimeError(f"El PDF contiene sintaxis Markdown: {found.group(0)!r}")
    return "correcto"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_files", nargs="+", type=Path)
    parser.add_argument("--docx", action="store_true", help="Generar también DOCX")
    parser.add_argument("--tmp-dir", type=Path, default=DEFAULT_TMP)
    parser.add_argument("--verificar", action="store_true")
    args = parser.parse_args()

    formats = ["pdf"] + (["docx"] if args.docx else [])
    tmp_dir = args.tmp_dir.resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)

    report: list[dict[str, object]] = []
    try:
        for source in args.markdown_files:
            source = source.resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            html = build_html(source, tmp_dir)
            files = convert(html, source.parent, tmp_dir, formats)
            entry: dict[str, object] = {
                "origen": str(source),
                "generados": [str(path) for path in files],
            }
            if args.verificar:
                entry["verificacion"] = verify_pdf(
                    next(path for path in files if path.suffix == ".pdf")
                )
            report.append(entry)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
