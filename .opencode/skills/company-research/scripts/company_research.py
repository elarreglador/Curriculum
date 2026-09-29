#!/usr/bin/env python3
"""Recuperacion de datos estructurados de empresas desde fuentes publicas sin clave."""

import argparse
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

USER_AGENT = "company-research-skill/1.0 (+https://github.com/elarreglador/Curriculum)"
REQUEST_TIMEOUT = 20
MIN_INTERVAL_SECONDS = 0.7
_last_request_at = 0.0

WIKIDATA_PROPERTIES = {
    "P17": ("pais", False, 1),
    "P159": ("sede", False, 1),
    "P571": ("fundacion", False, 1),
    "P1128": ("empleados", False, 1),
    "P856": ("web_oficial", False, 1),
    "P1454": ("forma_juridica", False, 1),
    "P452": ("sector", True, 6),
    "P112": ("fundada_por", True, 4),
    "P169": ("ceo", True, 3),
    "P1037": ("directivo", True, 3),
    "P463": ("pertenece_a", True, 4),
    "P749": ("matriz", True, 3),
    "P355": ("subsidiarias", True, 10),
    "P154": ("logo", False, 1),
    "P2139": ("ingresos", True, 3),
    "P414": ("bolsa", False, 1),
    "P2002": ("twitter", True, 2),
    "P2397": ("youtube", True, 1),
    "P2013": ("facebook", True, 1),
}

WIKIDATA_LABELS = {
    "es": {
        "P17": "País",
        "P159": "Sede",
        "P571": "Fundación",
        "P1128": "Empleados",
        "P856": "Web oficial",
        "P1454": "Forma jurídica",
        "P452": "Sector",
        "P112": "Fundada por",
        "P169": "CEO",
        "P1037": "Directivo",
        "P463": "Pertenece a",
        "P749": "Matriz",
        "P355": "Subsidiarias",
        "P154": "Logotipo",
        "P2139": "Ingresos",
        "P414": "Bolsa",
        "P1056": "Nombre corto",
        "P2002": "Twitter",
        "P2397": "YouTube",
        "P2013": "Facebook",
    },
    "en": {
        "P17": "Country",
        "P159": "Headquarters",
        "P571": "Founded",
        "P1128": "Employees",
        "P856": "Website",
        "P1454": "Legal form",
        "P452": "Industry",
        "P112": "Founded by",
        "P169": "CEO",
        "P1037": "Director",
        "P463": "Member of",
        "P749": "Parent",
        "P355": "Subsidiaries",
        "P154": "Logo",
        "P2139": "Revenue",
        "P414": "Stock exchange",
        "P1056": "Short name",
        "P2002": "Twitter",
        "P2397": "YouTube",
        "P2013": "Facebook",
    },
}
YEARLY_PROPERTIES = ("P2139", "P1128")

SECTION_ALIASES = {
    "identify": "identity",
    "identity": "identity",
    "perfil": "profile",
    "profile": "profile",
    "financiero": "financials",
    "financials": "financials",
    "finanzas": "financials",
    "registro": "registry",
    "registry": "registry",
    "legal": "registry",
    "todas": "all",
    "all": "all",
}

RESEARCH_AGENDA = {
    "web": "{company} official website products services qué hace",
    "news": "{company} noticias recientes {year}",
    "reputation": "{company} opinión empleados Glassdoor culture",
    "presence": "{company} LinkedIn perfil oficial tamaño empresa",
}


def load_env():
    env_path = SKILL_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            if value.strip():
                os.environ.setdefault(key.strip(), value.strip())


def http_get(url, headers=None, accept="application/json"):
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < MIN_INTERVAL_SECONDS:
        time.sleep(MIN_INTERVAL_SECONDS - elapsed)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept, **(headers or {})},
    )
    _last_request_at = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return json.dumps({"error": f"HTTP {error.code}", "url": url})
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return json.dumps({"error": str(error), "url": url})


def http_json(url, headers=None):
    raw = http_get(url, headers)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "respuesta no JSON", "raw": raw[:300]}


def cache_path(company, section):
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    return CACHE_DIR / f"{slug}-{section}.json"


def read_cache(company, section, ttl_hours):
    path = cache_path(company, section)
    if not path.exists():
        return None
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    if age > timedelta(hours=ttl_hours):
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def write_cache(company, section, payload):
    cache_path(company, section).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def extract_claim_value(snak, lang="es"):
    value = snak.get("datavalue", {}).get("value")
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "time" in value:
            return value["time"].lstrip("+").split("T")[0]
        if "amount" in value:
            return normalize_amount(value["amount"])
        if "id" in value:
            entity_id = value["id"]
            label = fetch_wikidata_label(entity_id, lang)
            return f"{label} ({entity_id})" if label else entity_id
        if "text" in value:
            return value["text"]
    if isinstance(value, (int, float)):
        return value
    return None


def normalize_amount(amount):
    try:
        return int(str(amount).lstrip("+"))
    except ValueError:
        return str(amount)


def extract_reference_year(entry):
    for qualifier in entry.get("qualifiers", {}).get("P585", []):
        year = extract_claim_value(qualifier)
        if isinstance(year, str) and len(year) >= 4:
            return year[:4]
    return None


def format_amount(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return str(value)
    if abs(value) < 10000:
        return f"{value:g}"
    return f"{value:,.0f}".replace(",", ".")


_LABEL_CACHE = {}


def fetch_wikidata_label(entity_id, lang="es"):
    cached = _LABEL_CACHE.get(entity_id)
    if cached:
        return cached
    languages = "es" if lang == "es" else "en"
    if lang != "es":
        languages = "en"
    data = http_json(
        f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}"
        f"&format=json&props=labels&languages={languages}|en"
    )
    entity = data.get("entities", {}).get(entity_id, {})
    entity_labels = entity.get("labels", {})
    label = entity_labels.get(lang, {}).get("value") or entity_labels.get("en", {}).get("value")
    _LABEL_CACHE[entity_id] = label
    return label


def wikidata_search(company, lang="en"):
    url = (
        "https://www.wikidata.org/w/api.php?action=wbsearchentities"
        f"&search={urllib.parse.quote(company)}&language={lang}&format=json&limit=5"
    )
    data = http_json(url)
    hits = data.get("search", []) or []
    return [
        {
            "qid": hit.get("id"),
            "label": hit.get("label"),
            "description": hit.get("description"),
            "matches": hit.get("match", {}).get("text", ""),
        }
        for hit in hits
    ]


def wikidata_entity(qid, lang="en"):
    url = (
        f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}"
        f"&format=json&languages={lang}|en&props=labels|descriptions|claims|aliases"
    )
    data = http_json(url)
    return data.get("entities", {}).get(qid, {})


LEGAL_SUFFIXES = (
    "s.a.u.",
    "s.a.",
    "s.l.",
    "s.l.u.",
    "s.p.a.",
    "s.a.s.",
    "s.à.r.l.",
    "s.a. de c.v.",
    "s.a.p.i.",
    "sa",
    "sau",
    "sas",
    "slu",
    "sl",
    "spa",
    "sarl",
    "inc",
    "inc.",
    "corp",
    "corp.",
    "ltd",
    "ltd.",
    "llc",
    "plc",
    "gmbh",
    "ag",
    "bv",
    "nv",
    "sarl",
    "oy",
    "ab",
    "as",
    "co",
    "company",
    "group",
    "grupo",
    "holding",
)


def strip_diacritics(text):
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def name_variants(company):
    variants = [company]
    base = strip_diacritics(company).lower().strip()
    without_suffix = base
    for suffix in LEGAL_SUFFIXES:
        if without_suffix.endswith(" " + suffix):
            without_suffix = without_suffix[: -len(suffix) - 1]
            break
    without_suffix = without_suffix.strip(" .,()")
    for candidate in (without_suffix, without_suffix.replace(" ", "")):
        if candidate and candidate != base and candidate not in variants:
            variants.append(candidate)
    return variants


LEGAL_NOISE = (
    " v ",
    " v.",
    " vs ",
    "commission",
    "court",
    "tribunal",
    "judgment",
    "sentencia",
    "auto",
    "caso",
    "expediente",
    "desahucio",
    "expulsion",
    "filing",
    "appeal",
    "case",
)


def normalize_label(text):
    return re.sub(r"[^a-z0-9]+", " ", strip_diacritics(text or "").lower()).strip()


def score_candidate(hit, query):
    label = normalize_label(hit.get("label"))
    normalized_query = normalize_label(query)
    padded_label = f" {label} "
    padded_query = f" {normalized_query} "
    score = 0
    if label == normalized_query:
        score += 100
    if label and (padded_query.startswith(padded_label) or padded_label.startswith(padded_query)):
        score += 40
    if any(token in padded_label for token in LEGAL_NOISE):
        score -= 1000
    if not hit.get("description"):
        score -= 500
    return score


def resolve_entity(company, lang="en"):
    attempts = []
    for variant in name_variants(company):
        hits = wikidata_search(variant, lang)
        attempts.append({"consulta": variant, "resultados": len(hits)})
        if not hits:
            continue
        ranked = sorted(
            hits,
            key=lambda hit: score_candidate(hit, variant),
            reverse=True,
        )
        if score_candidate(ranked[0], variant) <= 0:
            continue
        top = ranked[0]
        entity = wikidata_entity(top["qid"], lang)
        if not entity:
            continue
        labels = entity.get("labels", {})
        descriptions = entity.get("descriptions", {})
        return (
            {
                "qid": top["qid"],
                "nombre": labels.get(lang, labels.get("en", {})).get("value", top["label"]),
                "nombre_en": labels.get("en", {}).get("value", top["label"]),
                "descripcion": descriptions.get(lang, descriptions.get("en", {})).get(
                    "value", top["description"]
                ),
                "url": f"https://www.wikidata.org/wiki/{top['qid']}",
                "wikidata_url": f"https://www.wikidata.org/wiki/{top['qid']}",
                "consulta_resuelta": variant,
                "puntuacion": score_candidate(top, variant),
            },
            ranked,
            attempts,
        )
    return {}, [], attempts


def build_profile(entity, lang="es"):
    claims = entity.get("claims", {})
    labels = WIKIDATA_LABELS.get(lang, WIKIDATA_LABELS["es"])
    pairs = []
    for prop, (_, multi, limit) in WIKIDATA_PROPERTIES.items():
        if prop not in labels:
            continue
        entries = []
        for entry in claims.get(prop, []):
            if entry.get("rank") == "deprecated":
                continue
            value = extract_claim_value(entry.get("mainsnak", {}), lang)
            if value is None or value in entries:
                continue
            year = extract_reference_year(entry) if prop in YEARLY_PROPERTIES else None
            if isinstance(value, (int, float)):
                value = format_amount(value)
            entries.append((year or "", value, year))
        if not entries:
            continue
        entries.sort(key=lambda item: item[0], reverse=True)
        if not multi:
            entries = entries[:1]
        else:
            entries = entries[:limit]
        rendered = [
            f"{value} ({year})" if year and not str(value).endswith(f"({year})") else value
            for _, value, year in entries
        ]
        pairs.append((labels[prop], rendered[0] if len(rendered) == 1 else rendered))
    if entity.get("id"):
        pairs.append(("Wikidata", f"https://www.wikidata.org/wiki/{entity['id']}"))
    return dict(pairs)


def wikipedia_search_title(company, lang="es"):
    url = (
        f"https://{lang}.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(company)}&format=json&limit=5&srlimit=5"
    )
    data = http_json(url)
    hits = (data.get("query", {}) or {}).get("search", []) or []
    return [
        {"titulo": hit.get("title"), "qid": (hit.get("pageid"))}
        for hit in hits
        if not hit.get("title", "").lower().startswith(("discusión:", "discussion:", "wikipedia:"))
    ]


def wikipedia_summary(title, lang="es"):
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}"
    data = http_json(url)
    if data.get("type") != "standard":
        return None
    return {
        "titulo": data.get("title"),
        "resumen": data.get("extract"),
        "url": (data.get("content_urls", {}).get("desktop", {}) or {}).get("page"),
        "wikidata_id": data.get("wikibase_item"),
    }


def yahoo_chart(ticker):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}"
        "?range=5d&interval=1d"
    )
    data = http_json(url)
    chart = data.get("chart", {})
    if chart.get("error"):
        return {"error": chart["error"].get("description", "sin datos")}
    results = chart.get("result") or []
    if not results:
        return {"error": "sin resultados"}
    result = results[0]
    meta = result.get("meta", {})
    closes = [c for c in (result.get("indicators", {}).get("quote", [{}])[0].get("close") or []) if c]
    return {
        "ticker": meta.get("symbol"),
        "nombre": meta.get("longName") or meta.get("shortName"),
        "moneda": meta.get("currency"),
        "bolsa": meta.get("fullExchangeName"),
        "ultimo_cierre": closes[-1] if closes else None,
        "fuente": "Yahoo Finance",
        "url": f"https://finance.yahoo.com/quote/{urllib.parse.quote(ticker)}",
    }


def yahoo_fundamentals(ticker):
    base = "https://query2.finance.yahoo.com"
    modules = (
        "financialData,defaultKeyStatistics,summaryDetail,assetProfile,"
        "incomeStatementHistoryQuarterly"
    )
    url = f"{base}/v10/finance/quoteSummary/{urllib.parse.quote(ticker)}?modules={modules}"
    data = http_json(url)
    results = (data.get("quoteSummary", {}) or {}).get("result") or []
    if not results:
        return None
    result = results[0]

    def raw(module, field):
        return (result.get(module, {}) or {}).get(field, {}).get("raw")

    fundamentals = {
        "empleados": raw("assetProfile", "fullTimeEmployees"),
        "sector": raw("assetProfile", "sector"),
        "industria": raw("assetProfile", "industry"),
        "sede": raw("assetProfile", "city"),
        "pais": raw("assetProfile", "country"),
        "web_oficial": raw("assetProfile", "website"),
        "descripcion": raw("assetProfile", "longBusinessSummary"),
        "capitalizacion": raw("summaryDetail", "marketCap"),
        "ingresos_anuales": raw("financialData", "totalRevenue"),
        "crecimiento_ingresos": raw("financialData", "revenueGrowth"),
        "margen_neto": raw("financialData", "profitMargins"),
        "deuda_neta": raw("financialData", "totalDebt"),
        "flujo_caja": raw("financialData", "operatingCashflow"),
        "fuente": "Yahoo Finance",
    }
    return {key: value for key, value in fundamentals.items() if value is not None}


def opencorporates(company, jurisdiction=None):
    api_key = os.environ.get("OPENCORPORATES_API_KEY")
    params = {"q": company, "per_page": "3"}
    if jurisdiction:
        params["jurisdiction_code"] = jurisdiction
    url = "https://api.opencorporates.com/v0.4/companies/search?" + urllib.parse.urlencode(params)
    headers = {"Authorization": f"Token token={api_key}"} if api_key else None
    data = http_json(url, headers)
    companies = (data.get("results", {}) or {}).get("companies", [])
    if not companies:
        return {"note": "sin resultados en el registro mercantil", "fuente": "OpenCorporates"}
    records = []
    for entry in companies:
        item = entry.get("company", {})
        records.append(
            {
                "nombre_legal": item.get("name"),
                "jurisdiccion": item.get("jurisdiction_code"),
                "numero_registro": item.get("company_number"),
                "constitucion": item.get("incorporation_date"),
                "tipo": item.get("company_type"),
                "estado": item.get("current_status"),
                "domicilio": item.get("registered_address_in_full"),
                "url": item.get("opencorporates_url"),
            }
        )
    return {"registros": records, "fuente": "OpenCorporates"}


def sec_company(company):
    url = "https://www.sec.gov/files/company_tickers.json"
    data = http_json(url, {"Accept-Encoding": "gzip, deflate"})
    if "error" in data:
        return None
    needle = company.lower()
    for entry in data.values():
        title = str(entry.get("title", "")).lower()
        if needle in title or title in needle:
            return {
                "nombre": entry.get("title"),
                "cik": str(entry.get("cik_str")).zfill(10),
                "ticker": entry.get("ticker"),
                "fuente": "SEC EDGAR",
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={entry.get('cik_str')}",
            }
    return None


def build_agenda(company, year):
    return {
        key: query.format(company=company, year=year)
        for key, query in RESEARCH_AGENDA.items()
    }


def collect_warnings(bundle):
    warnings = []
    if not bundle.get("identity"):
        warnings.append(
            "Sin entidad en Wikidata. La empresa no esta identificada: "
            "confirme nombre legal y pais antes de continuar."
        )
    quote = bundle.get("quote") or {}
    if quote.get("error"):
        warnings.append(f"Mercado: {quote['error']} (indique --ticker si la empresa cotiza).")
    registry = bundle.get("registry") or {}
    if registry.get("note"):
        warnings.append(
            f"Registro mercantil: {registry['note']} "
            "(configure OPENCORPORATES_API_KEY para improve cobertura)."
        )
    if registry.get("error"):
        warnings.append(f"Registro mercantil: {registry['error']}")
    summary = bundle.get("summary") or {}
    if "summary" in bundle and not summary.get("resumen"):
        warnings.append(
            "Sin resumen en Wikipedia. Revise `wikipedia_candidatos` en la salida JSON."
        )
    if bundle.get("wikipedia_candidatos"):
        titles = ", ".join(
            candidate.get("titulo", "") for candidate in bundle["wikipedia_candidatos"][:3]
        )
        warnings.append(f"Sin Wikidata. Wikipedia tiene artículos titulados: {titles}")
    return warnings


def build_report(company, sections, bundle, lang="es"):
    lines = [f"# Informe de empresa: {company}", ""]
    identity = bundle.get("identity") or {}
    if identity and identity.get("nombre"):
        lines.append(f"**Nombre:** {identity['nombre']}")
    if identity and identity.get("descripcion"):
        lines.append(f"**Descripcion:** {identity['descripcion']}")
    if identity and identity.get("qid"):
        lines.append(f"**Wikidata:** {identity['qid']}")
    if not identity and bundle.get("summary", {}).get("titulo"):
        lines.append(f"**Nombre:** {bundle['summary']['titulo']} (via Wikipedia, sin Wikidata)")
    if identity:
        lines.append("")
        lines.append(f"> Verifique esta entidad: consulta `{identity.get('consulta_resuelta')}`, "
                     f"puntuacion {identity.get('puntuacion')}. Wikidata es punto de partida, "
                     f"no fuente primaria.")
        alternatives = bundle.get("alternativas_wikidata") or []
        if len(alternatives) > 1:
            lines.append(">")
            lines.append("> Otras candidatas descartadas:")
            for candidate in alternatives[1:4]:
                lines.append(f"> - {candidate.get('label')} ({candidate.get('qid')})")
    lines.append("")

    if "profile" in sections:
        profile = bundle.get("profile") or {}
        summary = bundle.get("summary") or {}
        if profile or summary.get("resumen"):
            lines.append("## Perfil")
            for key, value in profile.items():
                rendered = ", ".join(map(str, value)) if isinstance(value, list) else value
                lines.append(f"- **{key}:** {rendered}")
            if summary.get("resumen"):
                lines.append("")
                lines.append(summary["resumen"])
            lines.append("")

    if "financials" in sections:
        quote = bundle.get("quote") or {}
        fundamentals = bundle.get("fundamentals") or {}
        if quote.get("ticker") or fundamentals:
            lines.append("## Mercado y finanzas")
            for source in (quote, fundamentals):
                for key, value in source.items():
                    if key in ("fuente", "url") or value in (None, ""):
                        continue
                    lines.append(f"- **{key}:** {format_amount(value)}")
            lines.append("")
        else:
            lines.append("## Mercado y finanzas")
            lines.append("- Sin datos de mercado. Reintentelo indicando `--ticker`.")
            lines.append("")

    if "registry" in sections:
        registry = bundle.get("registry") or {}
        sec = bundle.get("sec")
        if registry.get("registros"):
            lines.append("## Registro mercantil")
            for record in registry["registros"]:
                lines.append(f"### {record.get('nombre_legal')}")
                for key, value in record.items():
                    if key in ("nombre_legal", "fuente") or not value:
                        continue
                    lines.append(f"- **{key}:** {value}")
                lines.append("")
        if sec:
            lines.append("## SEC EDGAR")
            for key, value in sec.items():
                if key in ("fuente", "url") or not value:
                    continue
                lines.append(f"- **{key}:** {value}")
            lines.append("")

    agenda = bundle.get("agenda") or {}
    if agenda and sections & set(agenda):
        lines.append("## Consultas pendientes para el agente")
        lines.append("Resuelvalas con las herramientas web nativas y cite las URLs usadas.")
        lines.append("")
        for key, query in agenda.items():
            if key in sections:
                lines.append(f"- `{key}`: {query}")
        lines.append("")

    warnings = collect_warnings(bundle)
    if warnings:
        lines.append("## Avisos")
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")

    sources = [bundle.get("identity", {}).get("url")] if identity else []
    sources += [
        bundle.get("summary", {}).get("url"),
        bundle.get("quote", {}).get("url"),
        bundle.get("sec", {}).get("url"),
    ]
    sources += [record.get("url") for record in (bundle.get("registry") or {}).get("registros", [])]
    unique_sources = list(dict.fromkeys(s for s in sources if s))
    if unique_sources:
        lines.append("## Fuentes")
        lines.extend(f"- {url}" for url in unique_sources)
        lines.append("")

    lines.append("---")
    lines.append("Datos estructurados automaticos. Verifique y complete con fuentes oficiales.")
    return "\n".join(lines)


def main():
    load_env()
    parser = argparse.ArgumentParser(
        description="Datos estructurados de empresa: Wikidata, Wikipedia, Yahoo Finance, registro mercantil."
    )
    parser.add_argument("company", help="Nombre de la empresa")
    parser.add_argument(
        "--section",
        default="all",
        choices=sorted(set(SECTION_ALIASES.values()) | set(SECTION_ALIASES.keys())),
        help="Seccion a recuperar (all usa todas).",
    )
    parser.add_argument("--ticker", default=None, help="Simbolo bursatico, p.ej. ITX.MC")
    parser.add_argument("--lang", default="es", choices=["es", "en"], help="Idioma de las etiquetas")
    parser.add_argument("--jurisdiction", default=None, help="Codigo de jurisdiccion, p.ej. es, gb, us")
    parser.add_argument("--format", default="markdown", choices=["json", "markdown"])
    parser.add_argument("--no-cache", action="store_true", help="Ignorar la cache")
    args = parser.parse_args()

    section = SECTION_ALIASES.get(args.section, args.section)
    sections = (
        ["identity", "profile", "financials", "registry"]
        if section == "all"
        else [section]
    )
    ttl_hours = int(os.environ.get("CACHE_TTL_HOURS", "24"))
    company = args.company
    year = datetime.now().year

    def cached_or_fetch(name, fetcher):
        if not args.no_cache:
            hit = read_cache(company, name, ttl_hours)
            if hit is not None:
                return hit
        result = fetcher()
        write_cache(company, name, result)
        return result

    bundle: dict = {"agenda": build_agenda(company, year)}
    identity: dict = {}
    if "identity" in sections or "profile" in sections:
        resolved = cached_or_fetch("identity", lambda: resolve_entity(company, args.lang))
        identity = resolved[0]
        bundle["identity"] = identity
        bundle["alternativas_wikidata"] = resolved[1][:5]
        bundle["intentos_normalizacion"] = resolved[2]

    if "profile" in sections and identity.get("qid"):
        entity = cached_or_fetch("entity", lambda: wikidata_entity(identity["qid"], args.lang))
        bundle["profile"] = build_profile(entity, args.lang) if entity else {}
        title = identity.get("nombre_en") or identity.get("nombre")
        bundle["summary"] = cached_or_fetch(
            "summary", lambda: wikipedia_summary(title, args.lang) or {}
        )
    else:
        entity = {}
        bundle["profile"] = {}
        candidates = cached_or_fetch("wiki_titles", lambda: wikipedia_search_title(company, args.lang))
        bundle["wikipedia_candidatos"] = candidates[:5]
        title = candidates[0]["titulo"] if candidates else company
        bundle["summary"] = cached_or_fetch(
            "summary", lambda: wikipedia_summary(title, args.lang) or {}
        )

    if "financials" in sections:
        ticker = args.ticker
        if not ticker:
            profile = bundle.get("profile", {})
            ticker = profile.get("Bolsa")
        bundle["quote"] = (
            cached_or_fetch("quote", lambda: yahoo_chart(ticker)) if ticker else {"error": "sin ticker"}
        )
        bundle["fundamentals"] = (
            cached_or_fetch("fundamentals", lambda: yahoo_fundamentals(ticker) or {}) if ticker else {}
        )
    else:
        bundle["quote"] = {}
        bundle["fundamentals"] = {}

    if "registry" in sections:
        bundle["registry"] = cached_or_fetch(
            "registry", lambda: opencorporates(company, args.jurisdiction)
        )
        bundle["sec"] = cached_or_fetch("sec", lambda: sec_company(company) or {})
    else:
        bundle["registry"] = {}
        bundle["sec"] = {}

    bundle["sections"] = sections
    bundle["consultas_pendientes"] = build_agenda(company, year)

    if args.format == "json":
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
    else:
        print(build_report(company, set(sections), bundle, args.lang))


if __name__ == "__main__":
    main()
