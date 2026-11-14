#!/usr/bin/env python3
"""Revisa output/ en busca de candidaturas previas para una empresa.

Uso:
    python3 revisar_output.py "ERNI"
    python3 revisar_output.py "ERNI" --puesto "Embedded Firmware Engineer"
    python3 revisar_output.py "ERNI" --json
"""
import argparse
import json
import pathlib
import re
import unicodedata


def ascii_only(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    return normalizado.encode("ascii", "ignore").decode("ascii")


def slug(empresa: str) -> str:
    limpio = "".join(c if c.isalnum() else "-" for c in ascii_only(empresa).lower())
    return "-".join(part for part in limpio.split("-") if part)


def parse_info(ruta: pathlib.Path) -> dict:
    texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""

    def campo(etiqueta: str) -> str:
        patron = re.compile(rf"- \*\*{re.escape(etiqueta)}:\*\*\s*(.*)")
        coincidencia = patron.search(texto)
        return coincidencia.group(1).strip() if coincidencia else ""

    return {
        "fecha": campo("Fecha"),
        "puesto": campo("Puesto"),
        "link": campo("Link de la oferta"),
    }


def buscar(empresa: str, raiz: pathlib.Path) -> list[dict]:
    company_slug = slug(empresa)
    resultados = []
    if not raiz.is_dir():
        return resultados
    for directorio in sorted(raiz.iterdir()):
        if not directorio.is_dir():
            continue
        coincidencia = re.match(r"^\d{8}-(.+)$", directorio.name)
        if not coincidencia:
            continue
        suffix_slug = slug(coincidencia.group(1))
        if suffix_slug == company_slug or suffix_slug.startswith(company_slug + "-"):
            info = parse_info(directorio / "info.md")
            resultados.append(
                {
                    "directorio": str(directorio),
                    "slug": suffix_slug,
                    "fecha": info["fecha"],
                    "puesto": info["puesto"],
                    "link": info["link"],
                }
            )
    return resultados


def main() -> int:
    ap = argparse.ArgumentParser(description="Revisa output/ por candidaturas previas")
    ap.add_argument("empresa", help='Nombre comercial, p. ej. "ERNI"')
    ap.add_argument("--puesto", default="", help="Puesto a comparar (opcional)")
    ap.add_argument(
        "--raiz",
        type=pathlib.Path,
        default=pathlib.Path("output"),
        help="Directorio raiz (por defecto: output)",
    )
    ap.add_argument("--json", action="store_true", help="Salida en JSON")
    args = ap.parse_args()

    coincidencias = buscar(args.empresa, args.raiz)
    puesto_solicitado = args.puesto.strip().lower()
    for item in coincidencias:
        item["mismo_puesto"] = bool(
            puesto_solicitado and item["puesto"].strip().lower() == puesto_solicitado
        )

    if args.json:
        print(
            json.dumps(
                {
                    "empresa": args.empresa,
                    "slug": slug(args.empresa),
                    "coincidencias": coincidencias,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not coincidencias:
        print(f"No se encontraron candidaturas previas para {args.empresa}.")
        return 0

    print(f"Candidaturas previas para {args.empresa}: {len(coincidencias)}")
    for item in coincidencias:
        marca = "  <-- MISMO PUESTO" if item["mismo_puesto"] else ""
        print(f"- {item['directorio']}")
        print(f"    Fecha: {item['fecha'] or 'No consta'}")
        print(f"    Puesto: {item['puesto'] or 'No consta'}{marca}")
        if item["link"] and item["link"].lower() != "no facilitado":
            print(f"    Oferta: {item['link']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
