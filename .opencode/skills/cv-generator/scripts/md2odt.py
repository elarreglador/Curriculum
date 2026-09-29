#!/usr/bin/env python3
"""Convierte un Markdown de CV/carta en ODT de una pagina.

Flujo: Markdown -> HTML (con CSS de impresion A4) -> ODT (LibreOffice).

Motivo: el filtro de importacion Markdown de LibreOffice 24.2 no esta disponible
en esta maquina y degrada el fichero a texto preformateado. La importacion HTML
si es funcional y respeta @page, tipografia y espaciados.
"""

import argparse
import pathlib
import subprocess
import sys
import tempfile

import markdown

CSS = """
@page {{
  size: A4 portrait;
  margin: {margin}cm;
}}

body {{
  font-family: "{font}";
  font-size: {base}pt;
  line-height: {line};
  color: #1a1a1a;
  margin: 0;
  padding: 0;
}}

h1 {{
  font-size: {h1}pt;
  margin: 0 0 2pt 0;
  line-height: 1.1;
}}

h1 + p {{
  margin-top: 0;
}}

h2 {{
  font-size: {h2}pt;
  margin: {h2mt}pt 0 2pt 0;
  border-bottom: 0.5pt solid #999999;
  padding-bottom: 1pt;
}}

h3 {{
  font-size: {h3}pt;
  margin: {h3mt}pt 0 1pt 0;
}}

p {{
  margin: 0 0 {pmt}pt 0;
}}

ul, ol {{
  margin: 0 0 {pmt}pt 0;
  padding-left: 14pt;
}}

li {{
  margin: 0 0 1pt 0;
}}

hr {{
  border: none;
  border-top: 0.5pt solid #bbbbbb;
  margin: {hrmt}pt 0;
}}

a {{ color: #1a1a1a; text-decoration: none; }}
strong {{ font-weight: bold; }}
"""

DEFAULTS = {
    "margin": 1.2,
    "font": "Liberation Sans",
    "base": 8.5,
    "line": 1.10,
    "h1": 15.0,
    "h2": 10.5,
    "h3": 9.5,
    "h2mt": 4.0,
    "h3mt": 3.0,
    "pmt": 1.8,
    "hrmt": 2.0,
}


def md_to_html(text: str, css: str, title: str) -> str:
    body = markdown.markdown(
        text,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html",
    )
    return (
        "<!DOCTYPE html>\n"
        '<html lang="es"><head><meta charset="utf-8">'
        f"<title>{title}</title><style>{css}</style></head>"
        f"<body>{body}</body></html>\n"
    )


def to_odt(html_path: pathlib.Path, outdir: pathlib.Path) -> pathlib.Path:
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "odt:writer8",
            "--outdir",
            str(outdir),
            str(html_path),
        ],
        check=True,
        capture_output=True,
        timeout=180,
    )
    return outdir / (html_path.stem + ".odt")


def to_pdf(odt: pathlib.Path, outdir: pathlib.Path) -> pathlib.Path:
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(odt),
        ],
        check=True,
        capture_output=True,
        timeout=180,
    )
    return outdir / (odt.stem + ".pdf")


def page_count(pdf: pathlib.Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(pdf)],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    for line in result.stdout.splitlines():
        if line.lower().startswith("pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"No se pudo determinar el numero de paginas de {pdf}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> ODT + PDF de una pagina")
    ap.add_argument("source", type=pathlib.Path)
    ap.add_argument("--outdir", type=pathlib.Path, default=None)
    ap.add_argument("--base-size", type=float, default=DEFAULTS["base"])
    ap.add_argument("--margin", type=float, default=DEFAULTS["margin"])
    ap.add_argument("--no-pdf", action="store_true", help="No generar el PDF")
    args = ap.parse_args()

    src: pathlib.Path = args.source
    outdir: pathlib.Path = args.outdir or src.parent
    outdir.mkdir(parents=True, exist_ok=True)

    config = dict(DEFAULTS, base=args.base_size, margin=args.margin)
    html = md_to_html(src.read_text(encoding="utf-8"), CSS.format(**config), src.stem)

    with tempfile.TemporaryDirectory() as tmp:
        html_path = pathlib.Path(tmp) / f"{src.stem}.html"
        html_path.write_text(html, encoding="utf-8")
        odt = to_odt(html_path, outdir)
        pdf = None if args.no_pdf else to_pdf(odt, outdir)
        pages = page_count(pdf if pdf else odt)

    print(f"{odt}  ({pages} pagina{'s' if pages != 1 else ''})")
    if pdf:
        print(f"{pdf}")
    return 0 if pages == 1 else 2


if __name__ == "__main__":
    sys.exit(main())
