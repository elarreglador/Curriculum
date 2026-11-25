#!/usr/bin/env python3
"""Alta y recuento de envíos en ofertas/envios.json.

La deduplicación usa la URL; si falta, empresa + puesto. No hay tope diario:
`contar` sólo informa de los envíos de hoy y `registrar` nunca rechaza un alta
por cantidad, únicamente por estado no válido o índice mal formado.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DEFAULT_INDEX = REPO / "ofertas" / "envios.json"
ESTADOS = {"enviada", "descartada-por-filtro", "bloqueada", "sin-responder", "error"}


def load_index(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "envios": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("envios"), list):
        raise ValueError(f"Índice mal formado: {path}")
    return data


def save_index(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=".envios-", delete=False
    )
    try:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.close()
        os.replace(handle.name, path)
    finally:
        if os.path.exists(handle.name):
            os.unlink(handle.name)


def entry_key(entry: dict) -> str:
    url = (entry.get("url") or "").strip().rstrip("/").lower()
    if url:
        return url
    return f"{(entry.get('empresa') or '').lower()}|{(entry.get('puesto') or '').lower()}"


def sent_today(data: dict, today: date) -> int:
    total = 0
    for entry in data["envios"]:
        if entry.get("estado") != "enviada":
            continue
        try:
            sent_on = datetime.fromisoformat(entry["fecha_envio"]).date()
        except (KeyError, ValueError):
            continue
        if sent_on == today:
            total += 1
    return total


def registrar(args: argparse.Namespace) -> int:
    if args.estado not in ESTADOS:
        print(
            json.dumps(
                {"error": "estado no válido", "permitidos": sorted(ESTADOS)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 3

    data = load_index(args.index)
    new_entry = {
        "empresa": args.empresa,
        "puesto": args.puesto,
        "url": args.url or "",
        "fecha_envio": args.fecha or datetime.now().astimezone().isoformat(timespec="seconds"),
        "estado": args.estado,
        "directorio": args.directorio or "",
    }
    key = entry_key(new_entry)

    for position, existing in enumerate(data["envios"]):
        if entry_key(existing) == key:
            data["envios"][position].update(new_entry)
            save_index(args.index, data)
            print(
                json.dumps(
                    {"registrado": True, "duplicado": True, "entrada": new_entry},
                    ensure_ascii=False,
                )
            )
            return 0

    data["envios"].append(new_entry)
    save_index(args.index, data)
    print(json.dumps({"registrado": True, "duplicado": False, "entrada": new_entry}, ensure_ascii=False))
    return 0


def contar(args: argparse.Namespace) -> int:
    data = load_index(args.index)
    print(json.dumps({"enviadas_hoy": sent_today(data, date.today())}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("registrar")
    register.add_argument("--empresa", required=True)
    register.add_argument("--puesto", required=True)
    register.add_argument("--url", default="")
    register.add_argument("--estado", required=True)
    register.add_argument("--directorio", default="")
    register.add_argument("--fecha", help="ISO 8601; por defecto, ahora")
    register.set_defaults(handler=registrar)

    count = subparsers.add_parser("contar")
    count.set_defaults(handler=contar)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
