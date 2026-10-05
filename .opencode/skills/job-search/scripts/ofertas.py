#!/usr/bin/env python3
"""Busqueda de ofertas de empleo y puntuacion de encaje con el perfil del CV.

El script resuelve solo la parte determinista: recoger, normalizar, filtrar y
puntuar con los criterios que le pasa el agente. El criterio argumental (si la
oferta encaja de verdad y por que) lo pone el agente, no el script.
"""

from __future__ import annotations

import argparse
import hashlib
import html as htmllib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = SKILL_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

USER_AGENT = "job-search-skill/1.0 (+https://github.com/elarreglador/Curriculum)"
REQUEST_TIMEOUT = 20
MIN_INTERVAL_SECONDS = 1.0
DEFAULT_TTL_HOURS = 6
PAGE_SIZE = 25
MAX_PAGES = 12
BASE_VITALIDAD = 25
TOPE_SOLO_DESCRIPCION = 45

LINKEDIN_SEARCH = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
LINKEDIN_DETAIL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
REMOTIVE_SEARCH = "https://remotive.com/api/remote-jobs"
HIMALAYAS_SEARCH = "https://himalayas.app/jobs/api/search"

CONSULTORAS = (
    "randstad", "adecco", "robert half", "michael page", "hays", "grafton",
    "manpower", "gi group", "gi staffing", "kelly services", "activia",
    "challenging group", "talentia", "questionmark", "peopletree",
    "talent solution", "staffing", "recruitment", "seleccion", "selección",
    "consultores", "consulting", "consultoria", "consultoría", "interin",
    "rrhh", "recursos humanos", "interim", "outsourcing",
)

PERFILES_COMERCIALES = re.compile(
    r"\b(teleoperador|telemarketing|comercial|asesor(?:a)? comercial|"
    r"agente comercial|call center|callcentre|preventista|comercializacion|"
    r"sales|marketing|copywriter|recruiter)\b",
    re.IGNORECASE,
)

NIVELES_SENIORITY = (
    ("junior", re.compile(r"\b(junior|jr|trainee|becari\w*|entry[\s-]?level|graduate|intern\w*)\b", re.IGNORECASE)),
    ("lead", re.compile(
        r"\b(staff|principal|distinguished|lead|head[\s-]of|chief|director|gerente|jefe)\b",
        re.IGNORECASE)),
    ("senior", re.compile(r"\b(senior|snr|sr|arquitecto|architect)\b", re.IGNORECASE)),
)

IDIOMA_MARCAS = {
    "es": ("de la que el en y a los del las por con para una se su al es un como mas sobre entre",
           "experiencia trabajo empresa equipo lugar puesto convolutional candidato"),
    "en": ("the and of to in for with is are you your our will have has not this that from they",
           "experience work company team role location required skills knowledge candidate"),
    "de": ("der die das und den dem mit fur auf ist sind sie sich nicht auch eine als werden",
           "aufgaben erfahrung kenntnisse bewerber unternehmen standort ihre"),
    "fr": ("le la les de des et pour avec nous une dans est sont vous votre notre",
           "experience travail entreprise equipe poste lieu candidat"),
    "pt": ("de da do que e para com uma nao se em sao voce seu nossa por mais",
           "experiencia trabalho empresa equipe vaga local candidato"),
}

MARCAS_REMOTO = re.compile(r"\b(remote|remoto|remota|teletrabajo|anywhere|worldwide|home ?-? ?office)\b", re.IGNORECASE)

_last_request_at = 0.0


def load_env() -> None:
    env_path = SKILL_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            clave, _, valor = line.partition("=")
            if valor.strip():
                os.environ.setdefault(clave.strip(), valor.strip())


def cache_path(url: str) -> Path:
    return CACHE_DIR / f"{hashlib.sha1(url.encode('utf-8')).hexdigest()[:20]}.json"


def cache_read(url: str, ttl_horas: float, usar_cache: bool) -> str | None:
    if not usar_cache:
        return None
    ruta = cache_path(url)
    if not ruta.exists():
        return None
    try:
        carga = json.loads(ruta.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if time.time() - carga.get("ts", 0) > ttl_horas * 3600:
        return None
    return carga.get("body")


def cache_write(url: str, body: str) -> None:
    try:
        cache_path(url).write_text(
            json.dumps({"url": url, "ts": time.time(), "body": body}), encoding="utf-8"
        )
    except OSError:
        pass


def http_get(url: str, usar_cache: bool, ttl_horas: float, accept: str = "text/html") -> str | None:
    global _last_request_at
    guardada = cache_read(url, ttl_horas, usar_cache)
    if guardada is not None:
        return guardada
    espera = MIN_INTERVAL_SECONDS - (time.monotonic() - _last_request_at)
    if espera > 0:
        time.sleep(espera)
    peticion = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": accept, "Accept-Language": "es,en;q=0.8"}
    )
    _last_request_at = time.monotonic()
    try:
        with urllib.request.urlopen(peticion, timeout=REQUEST_TIMEOUT) as respuesta:
            cuerpo = respuesta.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as error:
        print(f"[aviso] {url} -> {error}", file=sys.stderr)
        return None
    cache_write(url, cuerpo)
    return cuerpo


def normalizar(texto: str) -> str:
    plano = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in plano if not unicodedata.combining(c)).strip()


def texto_plano(fragmento: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def inferir_seniority(titulo: str) -> str:
    for nivel, patron in NIVELES_SENIORITY:
        if patron.search(titulo):
            return nivel
    return "mid"


def inferir_idioma(texto: str) -> str | None:
    if not texto or len(texto) < 120:
        return None
    palabras = set(normalizar(texto).split())
    mejor_idioma, mejor_puntuacion = None, 0
    for idioma, marcas in IDIOMA_MARCAS.items():
        comunes = marcas[0].split()
        puntuacion = sum(1 for marca in comunes if normalizar(marca) in palabras)
        extras = marcas[1].split() if len(marcas) > 1 else []
        puntuacion += 2 * sum(1 for marca in extras if normalizar(marca) in palabras)
        if puntuacion > mejor_puntuacion:
            mejor_idioma, mejor_puntuacion = idioma, puntuacion
    return mejor_idioma if mejor_puntuacion >= 4 else None


def contiene(texto: str, termino: str) -> bool:
    """Coincidencia por palabra completa: 'go' no debe casar dentro de 'algorithm'."""
    patron = r"(?<!\w)" + re.escape(normalizar(termino)) + r"(?!\w)"
    return re.search(patron, texto) is not None


def es_consultora(empresa: str) -> bool:
    return any(marca in normalizar(empresa) for marca in CONSULTORAS)


def es_comercial(titulo: str) -> bool:
    return bool(PERFILES_COMERCIALES.search(titulo))


def antiguedad_dias(fecha: str | None, hoy: datetime) -> int | None:
    if not fecha:
        return None
    try:
        publicada = datetime.strptime(fecha[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return max((hoy - publicada).days, 0)


def parse_linkedin(html: str) -> list[dict]:
    ofertas = []
    for tarjeta in re.findall(r"<li[^>]*>(.*?)</li>", html, re.S):
        idm = re.search(r"urn:li:jobPosting:(\d+)", tarjeta)
        titulo = re.search(r"base-search-card__title[^>]*>(.*?)</h3>", tarjeta, re.S)
        subtitulo = re.search(r"base-search-card__subtitle[^>]*>(.*?)</h4>", tarjeta, re.S)
        ubicacion = re.search(r"job-search-card__location[^>]*>(.*?)</span>", tarjeta, re.S)
        fecha = re.search(r"<time[^>]*datetime=\"([^\"]+)\"", tarjeta)
        enlace = re.search(r"href=\"(https://[^\"]*?/jobs/view/[^\"]+)\"", tarjeta)
        beneficios = texto_plano(" ".join(re.findall(r"job-posting-benefits__text[^>]*>(.*?)</span>", tarjeta, re.S)))
        if not (idm and titulo):
            continue
        url = htmllib.unescape(enlace.group(1)).split("?")[0] if enlace else ""
        location = texto_plano(ubicacion.group(1)) if ubicacion else ""
        ofertas.append({
            "id": idm.group(1),
            "titulo": texto_plano(titulo.group(1)),
            "empresa": texto_plano(subtitulo.group(1)) if subtitulo else "",
            "ubicacion": location,
            "remoto": bool(MARCAS_REMOTO.search(f"{location} {beneficios}")),
            "fecha": fecha.group(1) if fecha else None,
            "url": url,
            "beneficios": beneficios,
            "descripcion": None,
            "idioma": None,
            "seniority": None,
            "consultora": None,
            "comercial": None,
            "fuente": "linkedin",
        })
    return ofertas


def linkedin_search(terminos: str, ubicacion: str | None, dias: int, paginas: int,
                    limite: int, usar_cache: bool, ttl_horas: float) -> list[dict]:
    palabras = {"24h": "r86400", "3d": "r259200", "7d": "r604800", "14d": "r1209600", "30d": "r2592000"}
    ventana = palabras.get(f"{dias}d", "r1209600")
    encontradas: list[dict] = []
    paso = PAGE_SIZE
    for pagina in range(paginas):
        parametros = {"keywords": terminos, "f_TPR": ventana, "start": pagina * paso}
        if ubicacion:
            parametros["location"] = ubicacion
        url = f"{LINKEDIN_SEARCH}?{urllib.parse.urlencode(parametros)}"
        cuerpo = http_get(url, usar_cache, ttl_horas)
        if cuerpo is None:
            break
        lote = parse_linkedin(cuerpo)
        if not lote:
            break
        paso = len(lote)
        encontradas.extend(lote)
        if len(encontradas) >= limite:
            break
    return encontradas


def linkedin_detail(identificador: str, usar_cache: bool, ttl_horas: float) -> dict:
    cuerpo = http_get(LINKEDIN_DETAIL.format(identificador), usar_cache, ttl_horas)
    if cuerpo is None:
        return {}
    descripcion = re.search(r'show-more-less-html__markup[^>]*>(.*?)</div>', cuerpo, re.S)
    empresa = re.search(r'topcard__org-name-link[^>]*>(.*?)</a>', cuerpo, re.S)
    titulo = re.search(r'top-card-layout__title[^>]*>(.*?)</h2>', cuerpo, re.S)
    etiquetas = re.findall(r'description__job-criteria-subheader[^>]*>(.*?)</h3>', cuerpo, re.S)
    valores = re.findall(r'description__job-criteria-text[^>]*>(.*?)</span>', cuerpo, re.S)
    criterios = [
        f"{texto_plano(e)}: {texto_plano(v)}"
        for e, v in zip(etiquetas, valores)
    ]
    return {
        "descripcion": texto_plano(descripcion.group(1)) if descripcion else None,
        "empresa": texto_plano(empresa.group(1)) if empresa else None,
        "titulo": texto_plano(titulo.group(1)) if titulo else None,
        "criterios": criterios,
    }


def remotive_search(terminos: str, limite: int, usar_cache: bool, ttl_horas: float) -> list[dict]:
    url = f"{REMOTIVE_SEARCH}?{urllib.parse.urlencode({'search': terminos, 'limit': min(limite, 100)})}"
    cuerpo = http_get(url, usar_cache, ttl_horas, accept="application/json")
    if cuerpo is None:
        return []
    try:
        datos = json.loads(cuerpo).get("jobs", [])
    except json.JSONDecodeError:
        return []
    ofertas = []
    for oferta in datos:
        publicada = (oferta.get("publication_date") or "")[:10]
        ofertas.append({
            "id": str(oferta.get("id")),
            "titulo": oferta.get("title", ""),
            "empresa": oferta.get("company_name", ""),
            "ubicacion": oferta.get("candidate_required_location", ""),
            "remoto": True,
            "fecha": publicada or None,
            "url": oferta.get("url", ""),
            "beneficios": oferta.get("job_type", ""),
            "descripcion": re.sub(r"<[^>]+>", " ", oferta.get("description", "")) or None,
            "idioma": None,
            "seniority": None,
            "consultora": None,
            "comercial": None,
            "fuente": "remotive",
        })
    return ofertas


def himalayas_search(terminos: str, limite: int, usar_cache: bool, ttl_horas: float) -> list[dict]:
    url = f"{HIMALAYAS_SEARCH}?{urllib.parse.urlencode({'query': terminos, 'limit': min(limite, 50)})}"
    cuerpo = http_get(url, usar_cache, ttl_horas, accept="application/json")
    if cuerpo is None:
        return []
    try:
        datos = json.loads(cuerpo).get("jobs", [])
    except json.JSONDecodeError:
        return []
    ofertas = []
    for oferta in datos:
        publicada = oferta.get("pubDate")
        fecha = datetime.fromtimestamp(publicada, tz=timezone.utc).strftime("%Y-%m-%d") if publicada else None
        paises = oferta.get("locationRestrictions") or []
        if not paises:
            restricciones = "Remoto"
        elif len(paises) <= 6:
            restricciones = ", ".join(paises)
        else:
            restricciones = f"Remoto, {len(paises)} paises ({', '.join(paises[:4])}, ...)"
        seniority = (oferta.get("seniority") or [None])[0]
        ofertas.append({
            "id": oferta.get("guid", ""),
            "titulo": oferta.get("title", ""),
            "empresa": oferta.get("companyName", ""),
            "ubicacion": restricciones,
            "remoto": True,
            "fecha": fecha,
            "url": oferta.get("applicationLink", ""),
            "beneficios": ", ".join(oferta.get("employmentType") or []),
            "descripcion": re.sub(r"<[^>]+>", " ", oferta.get("description", "")) or None,
            "idioma": None,
            "seniority": normalizar(seniority).replace("-", "").replace("level", "") if seniority else None,
            "consultora": None,
            "comercial": None,
            "fuente": "himalayas",
        })
    return ofertas


def deduplicar(ofertas: list[dict]) -> list[dict]:
    vistas: set[str] = set()
    unicas = []
    for oferta in ofertas:
        clave = oferta.get("id") or f"{normalizar(oferta['empresa'])}|{normalizar(oferta['titulo'])}"
        firma = f"{normalizar(oferta['empresa'])}|{normalizar(oferta['titulo'])}"
        if clave in vistas or firma in vistas:
            continue
        vistas.add(clave)
        vistas.add(firma)
        unicas.append(oferta)
    return unicas


def puntuar(oferta: dict, criterios: dict, hoy: datetime) -> tuple[int, list[str]]:
    desglose: list[str] = []
    puntos = BASE_VITALIDAD
    desglose.append(f"+{BASE_VITALIDAD} oferta vigente y no es empresa de selección")
    titulo = normalizar(oferta["titulo"])
    descripcion = normalizar(oferta.get("descripcion") or "")

    aciertos_titulo = [c for c in criterios["clave"] if contiene(titulo, c)]
    aciertos_desc = []
    if aciertos_titulo:
        puntos += min(len(aciertos_titulo), 3) * 12
        desglose.append(f"+{min(len(aciertos_titulo), 3) * 12} clave en el titulo: {', '.join(aciertos_titulo[:4])}")
    if descripcion:
        aciertos_desc = [c for c in criterios["clave"] if contiene(descripcion, c)]
        if aciertos_desc:
            puntos += min(len(aciertos_desc), 2) * 6
            desglose.append(
                f"+{min(len(aciertos_desc), 2) * 6} clave en la descripcion: {', '.join(aciertos_desc[:4])}"
            )
    evidencia_debil = bool(aciertos_desc) and not aciertos_titulo

    ubicacion = normalizar(oferta.get("ubicacion") or "")
    if criterios["ubicacion"] and any(contiene(ubicacion, u) for u in criterios["ubicacion"]):
        puntos += 15
        desglose.append("+15 ubicación objetivo")
    if oferta.get("remoto") and criterios["remoto"]:
        puntos += 10
        desglose.append("+10 remoto")

    antiguedad = oferta.get("antiguedad_dias")
    if antiguedad is None:
        antiguedad = antiguedad_dias(oferta.get("fecha"), hoy)
        oferta["antiguedad_dias"] = antiguedad
    if antiguedad is not None:
        if antiguedad <= 7:
            puntos += 10
            desglose.append("+10 publicada esta semana")
        elif antiguedad <= 14:
            puntos += 5
            desglose.append("+5 publicada hace dos semanas")

    if oferta.get("idioma") and criterios["idioma_ok"] and oferta["idioma"] not in criterios["idioma_ok"]:
        puntos -= 25
        desglose.append(f"-25 idioma no habitual: {oferta['idioma']}")

    nivel = oferta.get("seniority") or inferir_seniority(oferta["titulo"])
    oferta["seniority"] = nivel
    if nivel not in criterios["seniority"]:
        puntos -= 15
        desglose.append(f"-15 nivel fuera de la banda buscada: {nivel}")

    if oferta.get("comercial"):
        puntos -= 25
        desglose.append("-25 perfil comercial o de telemarketing")

    empresa = normalizar(oferta.get("empresa") or "")
    penalizaciones = [d for d in criterios["descartar"] if contiene(f"{titulo} {descripcion} {empresa}", d)]
    if penalizaciones:
        puntos -= min(len(penalizaciones), 2) * 20
        desglose.append(f"-{min(len(penalizaciones), 2) * 20} descarte: {', '.join(penalizaciones[:3])}")

    if evidencia_debil:
        desglose.append(
            f"tope {TOPE_SOLO_DESCRIPCION}: sin clave en el titulo, la descripcion es evidencia debil"
        )
        puntos = min(puntos, TOPE_SOLO_DESCRIPCION)

    return max(0, min(100, puntos)), desglose


def evaluar(ofertas: list[dict], criterios: dict, hoy: datetime, minimo: int = 1) -> tuple[list[dict], list[dict]]:
    validas, descartadas = [], []
    for oferta in ofertas:
        dias_max = criterios["dias"]
        antiguedad = oferta["antiguedad_dias"]
        if antiguedad is not None and antiguedad > dias_max:
            oferta["motivo_descarte"] = f"publicada hace {antiguedad} días (límite {dias_max})"
            descartadas.append(oferta)
            continue
        if oferta["consultora"]:
            oferta["motivo_descarte"] = "empresa de selección"
            descartadas.append(oferta)
            continue
        if oferta["comercial"]:
            oferta["motivo_descarte"] = "perfil comercial o de telemarketing"
            descartadas.append(oferta)
            continue
        if criterios["clave"] and criterios["exigir_clave"]:
            texto = f"{normalizar(oferta['titulo'])} {normalizar(oferta.get('descripcion') or '')}"
            if not any(contiene(texto, c) for c in criterios["clave"]):
                oferta["motivo_descarte"] = "ninguna palabra clave del perfil en titulo ni descripcion"
                descartadas.append(oferta)
                continue
        validas.append(oferta)
    for oferta in validas:
        oferta["puntuacion"], oferta["desglose"] = puntuar(oferta, criterios, hoy)
    validas.sort(key=lambda o: o["puntuacion"], reverse=True)
    sin_señal = [o for o in validas if o["puntuacion"] < minimo]
    validas = [o for o in validas if o["puntuacion"] >= minimo]
    for oferta in sin_señal:
        oferta["motivo_descarte"] = f"sin señales de encaje (puntuación {oferta['puntuacion']})"
    descartadas.extend(sin_señal)
    return validas, descartadas


def parsear_lista(valor: str | None) -> list[str]:
    return [v.strip() for v in (valor or "").split(",") if v.strip()]


def construir_criterios(args: argparse.Namespace) -> dict:
    ubicacion = parsear_lista(getattr(args, "ubicacion", None))
    return {
        "clave": parsear_lista(getattr(args, "clave", None)),
        "descartar": parsear_lista(getattr(args, "descartar", None)),
        "ubicacion": ubicacion,
        "remoto": bool(getattr(args, "remoto", False)),
        "dias": getattr(args, "dias", 14),
        "seniority": parsear_lista(getattr(args, "seniority", None) or "junior,mid,senior"),
        "idioma_ok": parsear_lista(getattr(args, "idioma_ok", None) or "es,en"),
        "exigir_clave": not getattr(args, "permitir_sin_clave", False),
    }


def preparar(oferta: dict, hoy: datetime) -> dict:
    if oferta.get("seniority") is None:
        oferta["seniority"] = inferir_seniority(oferta["titulo"])
    if oferta.get("consultora") is None:
        oferta["consultora"] = es_consultora(oferta["empresa"])
    if oferta.get("comercial") is None:
        oferta["comercial"] = es_comercial(oferta["titulo"])
    if oferta.get("idioma") is None:
        oferta["idioma"] = inferir_idioma(oferta.get("descripcion") or "")
    if "antiguedad_dias" not in oferta:
        oferta["antiguedad_dias"] = antiguedad_dias(oferta.get("fecha"), hoy)
    return oferta


def celda(valor: object) -> str:
    """Escapa el separador de columna: un titre con barras rompe la tabla."""
    return str(valor).replace("|", "\\|").replace("\n", " ")


def tabla_markdown(resultado: dict) -> str:
    lineas = [
        "| Empresa | Puesto | Ubicación | Remota | Publicada | Días | Encaje | Oferta |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for oferta in resultado["ofertas"]:
        dias = oferta["antiguedad_dias"]
        lineas.append(
            f"| {celda(oferta['empresa'])} | {celda(oferta['titulo'])} | "
            f"{celda(oferta['ubicacion'] or '-')} | {'si' if oferta['remoto'] else 'no'} | "
            f"{celda(oferta.get('fecha') or '-')} | {dias if dias is not None else '-'} | "
            f"{oferta['puntuacion']} | {celda(oferta['url'])} |"
        )
    if resultado["descartadas"]:
        lineas += ["", "## Descartadas", "", "| Empresa | Puesto | Motivo |", "| --- | --- | --- |"]
        for oferta in resultado["descartadas"]:
            lineas.append(
                f"| {celda(oferta['empresa'])} | {celda(oferta['titulo'])} | "
                f"{celda(oferta.get('motivo_descarte', ''))} |"
            )
    return "\n".join(lineas)


def cmd_buscar(args: argparse.Namespace) -> int:
    hoy = datetime.now(timezone.utc)
    terminos = " ".join(args.terminos)
    criterios = construir_criterios(args)
    print(f"[buscar] '{terminos}' ubicacion={args.geo or '-'} remoto={args.remoto}", file=sys.stderr)

    if args.fuente == "linkedin":
        ofertas = linkedin_search(terminos, args.geo or None, args.dias,
                                  min(args.paginas, MAX_PAGES), args.limite,
                                  not args.sin_cache, args.ttl_horas)
    elif args.fuente == "remotive":
        ofertas = remotive_search(terminos, args.limite, not args.sin_cache, args.ttl_horas)
    else:
        ofertas = himalayas_search(terminos, args.limite, not args.sin_cache, args.ttl_horas)

    ofertas = [preparar(o, hoy) for o in deduplicar(ofertas)]
    validas, descartadas = evaluar(ofertas, criterios, hoy, args.minimo)

    if args.detalle:
        hidratadas = 0
        for oferta in validas[: args.detalle]:
            if oferta["fuente"] != "linkedin" or oferta.get("descripcion"):
                continue
            detalle = linkedin_detail(oferta["id"], not args.sin_cache, args.ttl_horas)
            if detalle.get("descripcion"):
                oferta["descripcion"] = detalle["descripcion"]
                oferta["criterios"] = detalle.get("criterios", [])
                oferta["idioma"] = inferir_idioma(oferta["descripcion"])
                hidratadas += 1
        print(f"[buscar] {hidratadas} ofertas hidratadas con su descripcion", file=sys.stderr)
        for oferta in validas:
            oferta["puntuacion"], oferta["desglose"] = puntuar(oferta, criterios, hoy)
        validas.sort(key=lambda o: o["puntuacion"], reverse=True)
        validas = [o for o in validas if o["puntuacion"] >= args.minimo]

    resultado = {
        "generado": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "consulta": {
            "terminos": terminos, "ubicacion": args.geo, "remoto": args.remoto,
            "dias": args.dias, "paginas": args.paginas, "fuente": args.fuente,
        },
        "criterios": criterios,
        "recogidas": len(ofertas),
        "ofertas": validas[: args.limite],
        "descartadas": descartadas,
    }
    resultado["resumen"] = {
        "ofertas_validas": len(validas),
        "descartadas": len(descartadas),
        "con_descripcion": sum(1 for o in resultado["ofertas"] if o.get("descripcion")),
    }

    if args.formato == "markdown":
        print(tabla_markdown(resultado))
    else:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


def cmd_remoto(args: argparse.Namespace) -> int:
    hoy = datetime.now(timezone.utc)
    terminos = " ".join(args.terminos)
    criterios = construir_criterios(args)
    print(f"[remoto] '{terminos}'", file=sys.stderr)
    ofertas = remotive_search(terminos, args.limite, not args.sin_cache, args.ttl_horas)
    ofertas += himalayas_search(terminos, args.limite, not args.sin_cache, args.ttl_horas)
    ofertas = [preparar(o, hoy) for o in deduplicar(ofertas)]
    objetivos = criterios["ubicacion"]
    if objetivos:
        dentro, fuera = [], []
        for oferta in ofertas:
            ubicacion = normalizar(oferta.get("ubicacion") or "")
            (dentro if any(contiene(ubicacion, u) for u in objetivos) else fuera).append(oferta)
        for oferta in fuera:
            oferta["motivo_descarte"] = f"fuera de la geografia objetivo ({oferta.get('ubicacion')})"
        ofertas = dentro
    validas, descartadas = evaluar(ofertas, criterios, hoy, args.minimo)
    resultado = {
        "generado": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "consulta": {"terminos": terminos, "ubicacion": objetivos, "remoto": True,
                     "dias": args.dias, "paginas": args.paginas, "fuente": "remoto"},
        "criterios": criterios,
        "recogidas": len(ofertas),
        "ofertas": validas[: args.limite],
        "descartadas": descartadas,
        "resumen": {"ofertas_validas": len(validas), "descartadas": len(descartadas)},
    }
    if args.formato == "markdown":
        print(tabla_markdown(resultado))
    else:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


def cmd_detalle(args: argparse.Namespace) -> int:
    identificador = args.identificador
    if "jobs/view" in identificador:
        encontrado = re.search(r"-(\d{6,})", identificador)
        identificador = encontrado.group(1) if encontrado else identificador
    detalle = linkedin_detail(identificador, not args.sin_cache, args.ttl_horas)
    if not detalle:
        print(f"[error] no se pudo obtener el detalle de {identificador}", file=sys.stderr)
        return 1
    detalle["idioma"] = inferir_idioma(detalle.get("descripcion") or "")
    detalle["id"] = identificador
    detalle["url"] = f"https://www.linkedin.com/jobs/view/{identificador}"
    if args.formato == "json":
        print(json.dumps(detalle, ensure_ascii=False, indent=2))
    else:
        print(f"# {detalle.get('titulo') or ''} — {detalle.get('empresa') or ''}\n")
        if detalle.get("criterios"):
            print("## Criterios\n")
            for criterio in detalle["criterios"]:
                print(f"- {criterio}")
            print()
        print("## Descripción\n")
        print(detalle.get("descripcion") or "Sin descripción.")
    return 0


def argumentos_comunes(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--clave", help="palabras clave positivas, separadas por comas")
    parser.add_argument("--descartar", help="palabras que restan encaje, separadas por comas")
    parser.add_argument("--seniority", help="niveles admitidos: junior,mid,senior,lead")
    parser.add_argument("--idioma-ok", help="idiomas admitidos (por defecto es,en)")
    parser.add_argument("--ubicacion", help="ubicaciones objetivo, separadas por comas")
    parser.add_argument("--dias", type=int, default=14, help="antiguedad maxima en dias (14)")
    parser.add_argument("--limite", type=int, default=50)
    parser.add_argument("--minimo", type=int, default=1, help="descartar por debajo de esta puntuacion")
    parser.add_argument("--permitir-sin-clave", action="store_true",
                        help="no descartar ofertas sin palabras clave del perfil")
    parser.add_argument("--formato", choices=["json", "markdown"], default="json")
    parser.add_argument("--sin-cache", action="store_true")
    parser.add_argument("--ttl-horas", type=float, default=float(os.environ.get("CACHE_TTL_HOURS", DEFAULT_TTL_HOURS)))


def main() -> int:
    load_env()
    parser = argparse.ArgumentParser(
        prog="ofertas.py",
        description="Busca ofertas de empleo y puntua su encaje con criterios dados.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    buscar = sub.add_parser("buscar", help="buscar ofertas en una fuente concreta")
    buscar.add_argument("terminos", nargs="+")
    buscar.add_argument("--fuente", choices=["linkedin", "remotive", "himalayas"], default="linkedin")
    buscar.add_argument("--geo", help="ubicacion para LinkedIn (texto)")
    buscar.add_argument("--remoto", action="store_true", help="sumar encaje a las ofertas remotas")
    buscar.add_argument("--paginas", type=int, default=2, help="paginas de 25 ofertas")
    buscar.add_argument("--detalle", type=int, default=10, help="cuantas ofertas hidratar con su descripcion")
    argumentos_comunes(buscar)
    buscar.set_defaults(func=cmd_buscar)

    remoto = sub.add_parser("remoto", help="buscar en agregadores de empleo remoto")
    remoto.add_argument("terminos", nargs="+")
    remoto.add_argument("--paginas", type=int, default=1)
    remoto.set_defaults(func=cmd_remoto)
    argumentos_comunes(remoto)

    detalle = sub.add_parser("detalle", help="descripcion completa de una oferta")
    detalle.add_argument("identificador", help="id de la oferta o URL completa")
    detalle.add_argument("--formato", choices=["json", "texto"], default="texto")
    detalle.add_argument("--sin-cache", action="store_true")
    detalle.add_argument("--ttl-horas", type=float, default=float(os.environ.get("CACHE_TTL_HOURS", DEFAULT_TTL_HOURS)))
    detalle.set_defaults(func=cmd_detalle)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())