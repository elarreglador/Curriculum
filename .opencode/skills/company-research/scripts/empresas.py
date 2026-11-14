#!/usr/bin/env python3
"""Gestión del registro de empresas en ofertas/empresas.json.

Upsert parcial por slug: si la empresa ya existe, solo se sobrescriben los
campos presentes y no vacíos; las ofertas se reemplazan solo si se pasan.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent
OFERTAS_DIR = PROJECT_ROOT / "ofertas"
EMPRESAS_PATH = OFERTAS_DIR / "empresas.json"


def slugify(name):
    if not name:
        return None
    decomposed = unicodedata.normalize("NFKD", str(name))
    base = "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or None


def load_records():
    if not EMPRESAS_PATH.exists():
        return []
    try:
        data = json.loads(EMPRESAS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        return [r for r in data.values() if isinstance(r, dict)]
    return []


def save_records(records):
    OFERTAS_DIR.mkdir(parents=True, exist_ok=True)
    records = sorted(
        records,
        key=lambda r: (r.get("nombre") or r.get("slug") or "").lower(),
    )
    tmp = EMPRESAS_PATH.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp, EMPRESAS_PATH)


def normalize_oferta(item):
    if isinstance(item, str):
        item = {"titulo": item}
    if not isinstance(item, dict):
        return None
    out = {}
    for key in ("titulo", "url", "ubicacion", "publicada"):
        if item.get(key) not in (None, ""):
            out[key] = item[key]
    if "titulo" not in out:
        for alt in ("title", "puesto", "name", "cargo"):
            if item.get(alt) not in (None, ""):
                out["titulo"] = item[alt]
                break
    return out if "titulo" in out else None


def _merge_fuentes(existing, incoming):
    merged = list(existing or [])
    for url in incoming or []:
        if url and url not in merged:
            merged.append(url)
    return merged


def upsert_one(incoming):
    if not isinstance(incoming, dict):
        raise ValueError("El registro debe ser un objeto JSON")
    records = load_records()
    slug = incoming.get("slug") or slugify(incoming.get("nombre"))
    if not slug:
        raise ValueError("Falta 'nombre' (o 'slug') para identificar la empresa")

    # Normalizar ofertas si se proporcionan
    ofertas_provided = "ultimas_ofertas_vistas" in incoming
    ofertas_norm = None
    if ofertas_provided:
        ofertas_norm = []
        for item in (incoming.get("ultimas_ofertas_vistas") or []):
            norm = normalize_oferta(item)
            if norm:
                ofertas_norm.append(norm)

    idx = None
    for i, rec in enumerate(records):
        if rec.get("slug") == slug or slugify(rec.get("nombre")) == slug:
            idx = i
            break

    now = datetime.now().isoformat(timespec="seconds")
    today = date.today().isoformat()

    if idx is None:
        record = {
            "slug": slug,
            "nombre": incoming.get("nombre"),
            "ubicacion": incoming.get("ubicacion"),
            "actividad": incoming.get("actividad"),
            "web": incoming.get("web"),
            "url_empleo": incoming.get("url_empleo"),
            "ultima_revision": incoming.get("ultima_revision"),
            "ultimas_ofertas_vistas": ofertas_norm if ofertas_norm is not None else [],
            "actualizado_en": incoming.get("actualizado_en") or now,
            "fuentes": incoming.get("fuentes") or [],
            "modo_consulta": incoming.get("modo_consulta"),
            "instrucciones_agente": incoming.get("instrucciones_agente"),
        },
        if record["ultima_revision"] is None and ofertas_provided:
            record["ultima_revision"] = today
        records.append(record)
    else:
        record = records[idx]
        record["slug"] = record.get("slug") or slug
        for key in ("nombre", "ubicacion", "actividad", "web", "url_empleo"):
            val = incoming.get(key)
            if val not in (None, "", []):
                record[key] = val
        if incoming.get("ultima_revision") not in (None, ""):
            record["ultima_revision"] = incoming["ultima_revision"]
        if ofertas_provided:
            record["ultimas_ofertas_vistas"] = ofertas_norm
            if incoming.get("ultima_revision") in (None, ""):
                record["ultima_revision"] = today
        record["actualizado_en"] = incoming.get("actualizado_en") or now
        if incoming.get("fuentes"):
            record["fuentes"] = _merge_fuentes(record.get("fuentes"), incoming["fuentes"])
        # Persistir modo_consulta e instrucciones_agente si se proporcionan
        for key in ("modo_consulta", "instrucciones_agente"):
            val = incoming.get(key)
            if val not in (None, "", []):
                record[key] = val
        records[idx] = record

    save_records(records)
    return record


def cmd_upsert(args):
    incoming_list = []
    if args.stdin:
        raw = sys.stdin.read()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"JSON invalido en stdin: {exc}", file=sys.stderr)
            sys.exit(2)
        if isinstance(parsed, list):
            incoming_list = parsed
        else:
            incoming_list = [parsed]
    else:
        if args.json:
            try:
                parsed = json.loads(args.json)
            except json.JSONDecodeError as exc:
                print(f"JSON invalido en --json: {exc}", file=sys.stderr)
                sys.exit(2)
            incoming_list = parsed if isinstance(parsed, list) else [parsed]
        else:
            incoming = {}
            if args.slug:
                incoming["slug"] = args.slug
            if args.nombre:
                incoming["nombre"] = args.nombre
            if args.ubicacion is not None:
                incoming["ubicacion"] = args.ubicacion
            if args.actividad is not None:
                incoming["actividad"] = args.actividad
            if args.web is not None:
                incoming["web"] = args.web
            if args.url_empleo is not None:
                incoming["url_empleo"] = args.url_empleo
            if args.ultima_revision is not None:
                incoming["ultima_revision"] = args.ultima_revision
            if args.ofertas_json is not None:
                try:
                    incoming["ultimas_ofertas_vistas"] = json.loads(args.ofertas_json)
                except json.JSONDecodeError as exc:
                    print(f"JSON invalido en --ofertas-json: {exc}", file=sys.stderr)
                    sys.exit(2)
            if args.ofertas_file:
                try:
                    incoming["ultimas_ofertas_vistas"] = json.loads(
                        Path(args.ofertas_file).read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError) as exc:
                    print(f"No se pudo leer --ofertas-file: {exc}", file=sys.stderr)
                    sys.exit(2)
            if args.fuentes:
                incoming["fuentes"] = [u.strip() for u in args.fuentes.split(",") if u.strip()]
            if args.actualizado_en:
                incoming["actualizado_en"] = args.actualizado_en
            if not incoming.get("nombre") and not incoming.get("slug"):
                print("Falta --nombre (o --slug). Use --stdin para pasar un objeto completo.", file=sys.stderr)
                sys.exit(2)
            incoming_list = [incoming]

    results = []
    for inc in incoming_list:
        try:
            rec = upsert_one(inc)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        results.append(rec)

    print(json.dumps(results if len(results) > 1 else results[0], ensure_ascii=False, indent=2))


def cmd_listar(args):
    records = load_records()
    if args.formato == "tabla":
        if not records:
            print("(sin registros)")
            return
        print(f"{'Nombre':<32} {'Ubicación':<20} {'Web':<40} {'Última rev.':<12}")
        for r in records:
            print(
                f"{str(r.get('nombre') or '')[:31]:<32} "
                f"{str(r.get('ubicacion') or '')[:19]:<20} "
                f"{str(r.get('web') or '')[:39]:<40} "
                f"{str(r.get('ultima_revision') or ''):<12}"
            )
    else:
        print(json.dumps(records, ensure_ascii=False, indent=2))


def cmd_mostrar(args):
    records = load_records()
    needle = slugify(args.nombre)
    for rec in records:
        if rec.get("slug") == needle or slugify(rec.get("nombre")) == needle:
            print(json.dumps(rec, ensure_ascii=False, indent=2))
            return
    print(f"No se encontró la empresa '{args.nombre}'", file=sys.stderr)
    sys.exit(1)


def cmd_pendientes(args):
    records = load_records()
    criterio = getattr(args, "criterio", "url_empleo") or "url_empleo"
    pend = []
    for r in records:
        val = r.get(criterio)
        if val in (None, "", []):
            pend.append(r)
    # Ordenar por numero de fuentes desc, luego nombre
    pend.sort(key=lambda r: (-(len(r.get("fuentes") or [])), str(r.get("nombre") or "").lower()))
    limite = getattr(args, "limite", None)
    if limite and limite > 0:
        pend = pend[:limite]
    if args.formato == "tabla":
        if not pend:
            print("(sin pendientes)")
            return
        print(f"{'Nombre':<32} {'Ubicación':<20} {'Fuentes':<8} {'Web':<40}")
        for r in pend:
            print(
                f"{str(r.get('nombre') or '')[:31]:<32} "
                f"{str(r.get('ubicacion') or '')[:19]:<20} "
                f"{len(r.get('fuentes') or []):<8} "
                f"{str(r.get('web') or '')[:39]:<40}"
            )
    else:
        print(json.dumps(pend, ensure_ascii=False, indent=2))


def cmd_eliminar(args):
    records = load_records()
    needle = slugify(args.nombre) if args.nombre else (args.slug or "")
    nueva_lista = [r for r in records if not (r.get("slug") == needle or slugify(r.get("nombre")) == needle)]
    if len(nueva_lista) == len(records):
        print(f"No se encontró la empresa '{args.nombre or args.slug}'", file=sys.stderr)
        sys.exit(1)
    save_records(nueva_lista)
    print(json.dumps({"eliminada": args.nombre or args.slug, "restantes": len(nueva_lista)}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Gestión del registro de empresas (ofertas/empresas.json)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    up = sub.add_parser("upsert", help="añadir o actualizar una empresa")
    up.add_argument("--stdin", action="store_true", help="leer registro(s) JSON desde stdin")
    up.add_argument("--json", default=None, help="registro(s) JSON como string")
    up.add_argument("--slug", default=None)
    up.add_argument("--nombre", default=None)
    up.add_argument("--ubicacion", default=None)
    up.add_argument("--actividad", default=None)
    up.add_argument("--web", default=None)
    up.add_argument("--url-empleo", dest="url_empleo", default=None)
    up.add_argument("--ultima-revision", dest="ultima_revision", default=None)
    up.add_argument("--ofertas-json", default=None, help="JSON con lista de ofertas vistas")
    up.add_argument("--ofertas-file", default=None, help="fichero JSON con lista de ofertas vistas")
    up.add_argument("--fuentes", default=None, help="URLs separadas por comas")
    up.add_argument("--actualizado-en", dest="actualizado_en", default=None)
    up.set_defaults(func=cmd_upsert)

    ls = sub.add_parser("listar", help="listar empresas registradas")
    ls.add_argument("--formato", choices=["json", "tabla"], default="json")
    ls.set_defaults(func=cmd_listar)

    sh = sub.add_parser("mostrar", help="mostrar una empresa")
    sh.add_argument("nombre")
    sh.set_defaults(func=cmd_mostrar)

    pe = sub.add_parser("pendientes", help="listar empresas pendientes de investigacion (sin url_empleo por defecto)")
    pe.add_argument("--criterio", choices=["url_empleo", "web", "actividad"], default="url_empleo",
                    help="campo que debe estar vacio para considerarla pendiente (url_empleo)")
    pe.add_argument("--limite", type=int, default=0, help="maximo de registros a mostrar (0 = todos)")
    pe.add_argument("--formato", choices=["json", "tabla"], default="json")
    pe.set_defaults(func=cmd_pendientes)

    el = sub.add_parser("eliminar", help="eliminar una empresa del registro")
    el.add_argument("nombre", nargs="?", default=None)
    el.add_argument("--slug", default=None)
    el.set_defaults(func=cmd_eliminar)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
