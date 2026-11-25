#!/usr/bin/env python3
"""Alta, consulta e índice de cuentas creadas en webs de empresas.

El índice vive en SENSIBLE/cuentas.json (ignorado por git) y no guarda
contraseñas: ésas están en SENSIBLE/credenciales.env. La deduplicación usa el
dominio normalizado. Toda respuesta, incluidos los errores, se imprime como JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[4]
DEFAULT_INDEX = REPO / "SENSIBLE" / "cuentas.json"
DEFAULT_ENV = REPO / "SENSIBLE" / "credenciales.env"
ESTADOS = {"creada", "pendiente-verificacion", "verificada", "error"}
CLAVES = ("CV_EMAIL", "CV_PASSWORD", "PROTON_EMAIL", "PROTON_PASSWORD")


def load_index(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "cuentas": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cuentas"), list):
        raise ValueError(f"Índice mal formado: {path}")
    return data


def save_index(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=".cuentas-", delete=False
    )
    try:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.close()
        os.replace(handle.name, path)
    finally:
        if os.path.exists(handle.name):
            os.unlink(handle.name)


def normalizar_dominio(valor: str) -> str:
    """De una URL o un dominio devuelve el host sin esquema, www ni puerto."""
    texto = (valor or "").strip().lower()
    if "://" in texto:
        texto = urlparse(texto).netloc
    texto = texto.split("/")[0].split("@")[-1].split(":")[0]
    if texto.startswith("www."):
        texto = texto[4:]
    return texto.strip(".")


def entry_key(entry: dict) -> str:
    dominio = normalizar_dominio(entry.get("dominio") or entry.get("url") or "")
    return dominio or f"empresa:{(entry.get('empresa') or '').strip().lower()}"


def registrar(args: argparse.Namespace) -> int:
    if args.estado not in ESTADOS:
        print(
            json.dumps({"error": "estado no válido", "permitidos": sorted(ESTADOS)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 3

    dominio = normalizar_dominio(args.dominio or args.url)
    if not dominio and not (args.empresa or "").strip():
        print(json.dumps({"error": "faltan dominio o empresa"}, ensure_ascii=False), file=sys.stderr)
        return 3

    data = load_index(args.index)
    nueva = {
        "empresa": (args.empresa or "").strip(),
        "dominio": dominio,
        "url": args.url or "",
        "email": args.email or "",
        "fecha_creacion": args.fecha or datetime.now().astimezone().date().isoformat(),
        "estado": args.estado,
        "fecha_verificacion": args.fecha_verificacion or "",
        "notas": args.notas or "",
    }
    clave = entry_key(nueva)

    for position, existing in enumerate(data["cuentas"]):
        if entry_key(existing) == clave:
            # Una actualización parcial no debe borrar lo que ya estaba guardado.
            conservar = ("dominio", "url", "email", "notas", "fecha_verificacion")
            if not args.fecha and existing.get("fecha_creacion"):
                nueva["fecha_creacion"] = existing["fecha_creacion"]
            for campo in conservar:
                if not nueva[campo] and existing.get(campo):
                    nueva[campo] = existing[campo]
            data["cuentas"][position].update(nueva)
            save_index(args.index, data)
            print(json.dumps({"registrado": True, "duplicado": True, "entrada": nueva}, ensure_ascii=False))
            return 0

    data["cuentas"].append(nueva)
    save_index(args.index, data)
    print(json.dumps({"registrado": True, "duplicado": False, "entrada": nueva}, ensure_ascii=False))
    return 0


def buscar(args: argparse.Namespace) -> int:
    destino = normalizar_dominio(args.dominio or args.url)
    if not destino and not (args.empresa or "").strip():
        print(json.dumps({"error": "faltan dominio, url o empresa"}, ensure_ascii=False), file=sys.stderr)
        return 3
    clave = destino or f"empresa:{(args.empresa or '').strip().lower()}"
    data = load_index(args.index)
    for entrada in data["cuentas"]:
        if entry_key(entrada) == clave:
            print(json.dumps({"encontrada": True, "entrada": entrada}, ensure_ascii=False))
            return 0
    print(json.dumps({"encontrada": False, "entrada": None}, ensure_ascii=False))
    return 0


def listar(args: argparse.Namespace) -> int:
    data = load_index(args.index)
    print(json.dumps({"cuentas": data["cuentas"]}, ensure_ascii=False))
    return 0


def verificar_credenciales(args: argparse.Namespace) -> int:
    """Comprueba qué claves hay, sin imprimir nunca sus valores."""
    presentes: list[str] = []
    if args.env.exists():
        for linea in args.env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            clave = clave.strip()
            valor = valor.strip().strip('"').strip("'")
            if clave in CLAVES and valor and clave not in presentes:
                presentes.append(clave)
    faltantes = [clave for clave in CLAVES if clave not in presentes]
    print(
        json.dumps(
            {"ok": not faltantes, "claves_presentes": presentes, "claves_faltantes": faltantes},
            ensure_ascii=False,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV)
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("registrar", help="alta o actualización por dominio")
    register.add_argument("--empresa", required=True)
    register.add_argument("--dominio", default="")
    register.add_argument("--url", default="")
    register.add_argument("--email", default="")
    register.add_argument("--estado", required=True, help=", ".join(sorted(ESTADOS)))
    register.add_argument("--fecha", help="ISO 8601 o fecha; por defecto, hoy")
    register.add_argument("--fecha-verificacion", default="")
    register.add_argument("--notas", default="")
    register.set_defaults(handler=registrar)

    find = subparsers.add_parser("buscar", help="buscar cuenta por dominio o empresa")
    find.add_argument("--dominio", default="")
    find.add_argument("--url", default="")
    find.add_argument("--empresa", default="")
    find.set_defaults(handler=buscar)

    listing = subparsers.add_parser("listar", help="listar el índice sin credenciales")
    listing.set_defaults(handler=listar)

    check = subparsers.add_parser("verificar-credenciales", help="comprobar claves sin imprimir valores")
    check.add_argument("--env", type=Path, default=argparse.SUPPRESS)
    check.set_defaults(handler=verificar_credenciales)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
