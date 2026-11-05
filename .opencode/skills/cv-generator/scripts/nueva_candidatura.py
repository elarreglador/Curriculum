#!/usr/bin/env python3
"""Prepara el andamiaje de una candidatura: output/YYYYMMDD-nombreempresa.

Deja el directorio con la foto de la cabecera, los assets referenciados por el
CV (iconos de LinkedIn/GitHub, etc.) y una copia del CV base, ya con el nombre
de la empresa. El agente adapta esa copia en lugar de escribir el CV desde
cero: asi la estructura (cabecera con foto, contacto al final) es siempre la
misma y lo unico que cambia de una candidatura a otra son las palabras.

Si el directorio ya existe no falla: lo reutiliza y no sobrescribe ni la foto
ni el CV, de modo que reejecutar la skill tras revisar el .md no pierde el
trabajo.

    python3 nueva_candidatura.py "CityPrive"            # -> output/20260929-cityprive
    python3 nueva_candidatura.py "Banco Santander"      # -> output/20260929-banco-santander
    python3 nueva_candidatura.py "Wecity" --dry-run     # solo muestra la ruta
    python3 nueva_candidatura.py "EDICOM" --foto assets/foto2.jpeg
"""

import argparse
import datetime as dt
import pathlib
import re
import shutil
import sys
import unicodedata


def ascii_only(texto: str) -> str:
    """Elimina acentos y diacriticos, para que la ruta no dependa de la codificacion."""
    normalizado = unicodedata.normalize("NFKD", texto)
    return normalizado.encode("ascii", "ignore").decode("ascii")


def slug(empresa: str) -> str:
    """Normaliza un nombre comercial a un identificador de directorio.

    Minúsculas, sin acentos ni caracteres no alfanuméricos, para que la ruta
    sea estable entre sistemas y no dependa de la codificacion.
    """
    limpio = "".join(c if c.isalnum() else "-" for c in ascii_only(empresa).lower())
    return "-".join(part for part in limpio.split("-") if part)


def etiqueta(empresa: str) -> str:
    """Normaliza el nombre comercial a la etiqueta de los ficheros internos.

    Mayusculas, como se lee en la carta: curriculum-EDICOM.md, carta-EDICOM.md.
    """
    limpio = "".join(c if c.isalnum() else "-" for c in ascii_only(empresa).upper())
    return "-".join(part for part in limpio.split("-") if part)


def build_path(empresa: str, raiz: pathlib.Path, hoy: dt.date | None = None) -> pathlib.Path:
    fecha = hoy or dt.date.today()
    return raiz / f"{fecha:%Y%m%d}-{slug(empresa)}"


def copiar(origen: pathlib.Path, destino: pathlib.Path) -> bool:
    """Copia `origen` a `destino` si este no existe. Devuelve True si lo copio.

    No sobrescribe a proposito: si el usuario ha retocado el CV a mano o ha
    cambiado la foto, reejecutar el script no debe tirar ese trabajo.
    """
    if not origen.is_file():
        raise SystemExit(f"error: no existe {origen}")
    if destino.exists():
        return False
    shutil.copy2(origen, destino)
    return True


def copiar_assets_referenciados(base: pathlib.Path, destino: pathlib.Path, dir_assets: pathlib.Path, excluir: set[str] | None = None) -> None:
    """Copia al directorio de salida las imagenes referenciadas por el CV base.

    El CV base referencia imagenes con rutas relativas (pin.png,
    linkedin16x16.png, github16x16.png, ...). Si no se copian, el CV renderizado
    en el directorio de la candidatura muestra iconos rotos. Copia cada una que
    exista en `dir_assets`, sin sobrescribir si ya esta.
    """
    if not base.is_file():
        return
    excluir = excluir or set()
    texto = base.read_text(encoding="utf-8")
    refs = set(re.findall(r'src=["\']([^"\']+)["\']', texto))
    for ref in sorted(refs):
        nombre = pathlib.PurePosixPath(ref).name
        if not nombre or nombre in excluir:
            continue
        origen = dir_assets / nombre
        if not origen.is_file():
            origen = base.parent / ref
            if not origen.is_file():
                continue
        destino_archivo = destino / nombre
        if destino_archivo.exists():
            print(f"  {nombre}  ya estaba, se conserva")
            continue
        shutil.copy2(origen, destino_archivo)
        print(f"  {nombre}  (asset referenciado por el CV, desde {origen})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepara output/YYYYMMDD-nombreempresa")
    ap.add_argument("empresa", help='Nombre comercial, p. ej. "CityPrive"')
    ap.add_argument(
        "--raiz",
        type=pathlib.Path,
        default=pathlib.Path("output"),
        help="Directorio raiz (por defecto: output)",
    )
    ap.add_argument(
        "--base",
        type=pathlib.Path,
        default=pathlib.Path("sources/curriculum-base.md"),
        help="CV base a copiar como curriculum-EMPRESA.md",
    )
    ap.add_argument(
        "--foto",
        type=pathlib.Path,
        default=pathlib.Path("assets/pin.png"),
        help="Imagen de la cabecera del CV",
    )
    ap.add_argument(
        "--sin-foto",
        action="store_true",
        help="No copiar la imagen de la cabecera",
    )
    ap.add_argument(
        "--assets",
        type=pathlib.Path,
        default=pathlib.Path("assets"),
        help="Directorio con las imagenes referenciadas por el CV (por defecto: assets)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar la ruta sin crear nada",
    )
    args = ap.parse_args()

    destino = build_path(args.empresa, args.raiz)
    curriculum = destino / f"curriculum-{etiqueta(args.empresa)}.md"
    carta = destino / f"carta-{etiqueta(args.empresa)}.md"

    if args.dry_run:
        print(destino)
        return 0

    destino.mkdir(parents=True, exist_ok=True)
    print(f"{destino}/")

    foto = destino / args.foto.name
    if args.sin_foto:
        print("  foto     omitida (--sin-foto): quita el <img> de la cabecera")
    elif copiar(args.foto, foto):
        print(f"  {foto.name}  (cabecera del CV, desde {args.foto})")
    else:
        print(f"  {foto.name}  ya estaba, se conserva")

    if copiar(args.base, curriculum):
        print(f"  {curriculum.name}  (copia de {args.base}: adaptar, no reescribir)")
    else:
        print(f"  {curriculum.name}  ya estaba, se conserva")

    copiar_assets_referenciados(args.base, destino, args.assets, excluir={args.foto.name})

    print(f"  {carta.name}  pendiente de redactar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
