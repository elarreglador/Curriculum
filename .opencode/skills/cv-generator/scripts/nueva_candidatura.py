#!/usr/bin/env python3
"""Crea el directorio de una candidatura: output/YYYYMMDD-nombreempresa.

Imprime la ruta del directorio creado. Si el directorio ya existe no falla:
lo reutiliza, de modo que reejecutar la skill tras revisar el .md no pierde
el trabajo previo.

    python3 nueva_candidatura.py "CityPrive"          # -> output/20260929-cityprive
    python3 nueva_candidatura.py "Banco Santander"    # -> output/20260929-bancosantander
    python3 nueva_candidatura.py "Wecity" --dry-run   # solo muestra la ruta
"""

import argparse
import datetime as dt
import pathlib
import sys
import unicodedata


def slug(empresa: str) -> str:
    """Normaliza un nombre comercial a un identificador de directorio.

    Minúsculas, sin acentos ni caracteres no alfanuméricos, para que la ruta
    sea estable entre sistemas y no dependa de la codificacion.
    """
    sin_acentos = unicodedata.normalize("NFKD", empresa)
    ascii_only = sin_acentos.encode("ascii", "ignore").decode("ascii")
    limpio = "".join(c if c.isalnum() else "-" for c in ascii_only.lower())
    return "-".join(part for part in limpio.split("-") if part)


def build_path(empresa: str, raiz: pathlib.Path, hoy: dt.date | None = None) -> pathlib.Path:
    fecha = hoy or dt.date.today()
    return raiz / f"{fecha:%Y%m%d}-{slug(empresa)}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Crea output/YYYYMMDD-nombreempresa")
    ap.add_argument("empresa", help="Nombre comercial, p. ej. \"CityPrive\"")
    ap.add_argument(
        "--raiz",
        type=pathlib.Path,
        default=pathlib.Path("output"),
        help="Directorio raiz (por defecto: output)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar la ruta sin crear el directorio",
    )
    args = ap.parse_args()

    destino = build_path(args.empresa, args.raiz)
    if not args.dry_run:
        destino.mkdir(parents=True, exist_ok=True)
    print(destino)
    return 0


if __name__ == "__main__":
    sys.exit(main())
