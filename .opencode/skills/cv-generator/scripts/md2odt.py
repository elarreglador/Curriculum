#!/usr/bin/env python3
"""Convierte un Markdown (CV o carta) en ODT y PDF.

El camino es Markdown -> HTML -> LibreOffice, y no al reves: el filtro
Markdown de LibreOffice no esta disponible en esta maquina y deja los `#` y
`**` literales en el ODT. Al reves funciona porque el importador HTML de
LibreOffice resuelve la tabla de cabecera con sus anchos absolutos en
pixeles, que es justo lo que hace falta para que el nombre no se parta en
tres lineas.

Dos detalles que costaron sangre:

- El importador HTML **ignora el bloque `<style>`**, asi que el tamano de
  letra y los margenes se inyectan como estilos en linea sobre cada elemento.
- Las imagenes locales (pin.png, los iconos) se copian junto al HTML: LibreOffice
  no resuelve data URI en HTML, y sin ellas el ODT se abre sin foto.

Los margenes de pagina se parchelan despues en el ODT, porque el importador
tampoco respeta `@page`.

    python3 md2odt.py output/20261022-conectio/curriculum-CONECTIO.md
    python3 md2odt.py carta.md --no-pdf
"""

import argparse
import mimetypes
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import markdown
from bs4 import BeautifulSoup

# Tamano de letra y separaciones. Todo en puntos: el ODT los guarda como
# fo:font-size y fo:margin-*, y son los que deciden si el CV cabe en una
# pagina.
ESTILOS = {
    "h1": "font-size:15pt;margin-top:0pt;margin-bottom:1pt;",
    "h2": "font-size:10.5pt;margin-top:6pt;margin-bottom:2pt;",
    "h3": "font-size:9.5pt;margin-top:4pt;margin-bottom:1pt;",
    "p": "font-size:9pt;margin-top:0pt;margin-bottom:3pt;",
    "li": "font-size:9pt;margin-top:0pt;margin-bottom:0.5pt;",
    "ul": "font-size:9pt;margin-top:0pt;margin-bottom:3pt;",
    "ol": "font-size:9pt;margin-top:0pt;margin-bottom:3pt;",
    "td": "font-size:9pt;",
}

MARGENES_PAGINA = {"top": "1cm", "bottom": "1cm", "left": "1.2cm", "right": "1.2cm"}

IMG_RE = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.IGNORECASE)
PAGE_RE = re.compile(rb"/Type\s*/Page[^s]")


def md_to_html(md_text: str) -> str:
    """Markdown -> HTML, con la cabecera del CV en HTML intacta."""
    return markdown.markdown(
        md_text,
        extensions=["tables", "md_in_html", "sane_lists", "attr_list"],
    )


def inyectar_estilos(html_text: str) -> str:
    """Anade los estilos en linea que el importador HTML de LibreOffice si lee."""
    sopa = BeautifulSoup(html_text, "html.parser")
    for etiqueta, estilo in ESTILOS.items():
        for elemento in sopa.find_all(etiqueta):
            actual = elemento.get("style", "")
            elemento["style"] = f"{actual};{estilo}" if actual else estilo
    return str(sopa)


def copiar_imagenes(html_text: str, base_dir: pathlib.Path, destino: pathlib.Path) -> str:
    """Copia las imagenes locales al directorio de trabajo y reapunta los src."""

    def sustituir(match: re.Match) -> str:
        prefijo, src, sufijo = match.groups()
        if src.startswith(("http://", "https://", "data:", "mailto:")):
            return match.group(0)
        ruta = (base_dir / src).resolve()
        if not ruta.is_file():
            return match.group(0)
        shutil.copy2(ruta, destino / ruta.name)
        return f"{prefijo}{ruta.name}{sufijo}"

    return IMG_RE.sub(sustituir, html_text)


def _soffice(args: list[str], profile: pathlib.Path) -> None:
    cmd = [
        "soffice",
        "--headless",
        "--norestore",
        f"-env:UserInstallation=file://{profile}",
        *args,
    ]
    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if resultado.returncode != 0:
        raise RuntimeError(
            f"LibreOffice fallo ({resultado.returncode}): {resultado.stderr.strip()}"
        )


def to_odt(html_path: pathlib.Path, outdir: pathlib.Path, profile: pathlib.Path) -> pathlib.Path:
    _soffice(
        ["--convert-to", "odt:writer8", "--outdir", str(outdir), str(html_path)],
        profile,
    )
    odt = outdir / f"{html_path.stem}.odt"
    if not odt.is_file():
        raise RuntimeError(f"no se genero el ODT en {odt}")
    return odt


def parchear_margenes(odt_path: pathlib.Path) -> None:
    """Ajusta los margenes de pagina del ODT generado (el HTML no los lleva)."""
    with zipfile.ZipFile(odt_path) as origen:
        contenido = {nombre: origen.read(nombre) for nombre in origen.namelist()}

    estilos = contenido["styles.xml"].decode("utf-8")

    def ajustar(matched: re.Match) -> str:
        bloque = matched.group(0)
        for lado, valor in MARGENES_PAGINA.items():
            bloque = re.sub(
                rf'fo:margin-{lado}="[^"]*"', f'fo:margin-{lado}="{valor}"', bloque
            )
        return bloque

    estilos = re.sub(r"<style:page-layout-properties[^>]*/>", ajustar, estilos)
    contenido["styles.xml"] = estilos.encode("utf-8")

    with zipfile.ZipFile(odt_path, "w", zipfile.ZIP_DEFLATED) as salida:
        # 'mimetype' debe ir primero y sin comprimir para que el ODT sea valido.
        salida.writestr("mimetype", contenido["mimetype"], zipfile.ZIP_STORED)
        for nombre, datos in contenido.items():
            if nombre != "mimetype":
                salida.writestr(nombre, datos)


def to_pdf(odt_path: pathlib.Path, outdir: pathlib.Path, profile: pathlib.Path) -> pathlib.Path:
    _soffice(
        ["--convert-to", "pdf:writer_pdf_Export", "--outdir", str(outdir), str(odt_path)],
        profile,
    )
    pdf = outdir / f"{odt_path.stem}.pdf"
    if not pdf.is_file():
        raise RuntimeError(f"no se genero el PDF en {pdf}")
    return pdf


def page_count(pdf_path: pathlib.Path) -> int:
    return len(PAGE_RE.findall(pdf_path.read_bytes()))


def main() -> int:
    ap = argparse.ArgumentParser(description="Markdown -> ODT + PDF (via HTML y LibreOffice)")
    ap.add_argument("source", type=pathlib.Path, help="fichero .md de entrada")
    ap.add_argument("--no-pdf", action="store_true", help="no generar el PDF")
    ap.add_argument(
        "--outdir", type=pathlib.Path, help="directorio de salida (por defecto, el del .md)"
    )
    args = ap.parse_args()

    origen = args.source.resolve()
    if not origen.is_file():
        raise SystemExit(f"error: no existe {origen}")

    destino = (args.outdir or origen.parent).resolve()
    destino.mkdir(parents=True, exist_ok=True)

    html = inyectar_estilos(md_to_html(origen.read_text(encoding="utf-8")))

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        html = copiar_imagenes(html, origen.parent, tmpdir)
        html_path = tmpdir / f"{origen.stem}.html"
        html_path.write_text(html, encoding="utf-8")
        profile = tmpdir / "lo-profile"

        odt = to_odt(html_path, tmpdir, profile)
        parchear_margenes(odt)
        shutil.copy2(odt, destino / f"{origen.stem}.odt")
        print(f"{destino / f'{origen.stem}.odt'}")

        if not args.no_pdf:
            pdf = to_pdf(odt, tmpdir, profile)
            shutil.copy2(pdf, destino / f"{origen.stem}.pdf")
            print(f"{destino / f'{origen.stem}.pdf'}  ({page_count(pdf)} paginas)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
