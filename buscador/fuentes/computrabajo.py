"""Fuente: Computrabajo Colombia, la bolsa de empleo más grande del país.

No tiene API pública: se lee la misma página de resultados que ve una persona
(co.computrabajo.com/trabajo-de-{busqueda}[-en-bogota-dc]), se descartan en el acto los cargos
que no encajan y solo de los que quedan se abre el detalle, que trae los datos de la oferta en
JSON-LD (schema.org JobPosting). Pocas páginas y con pausa, para no cargar el sitio.
"""
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date, timedelta

from ..texto import normalizar
from .workday import pasa_titulo

BASE = "https://co.computrabajo.com"
UA_NAV = ("Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/131.0 Mobile Safari/537.36")
_ENLACE = re.compile(r'<a\b[^>]*href="((?:https://co\.computrabajo\.com)?/ofertas-de-trabajo/oferta-de-trabajo-de-[^"#?]+)'
                     r'[^>]*>(.*?)</a>', re.S | re.I)
_LD = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S | re.I)
_ETIQ = re.compile(r"<[^>]+>")
_HIBRIDO = re.compile(r"h[ií]brid", re.I)
_REMOTO = re.compile(r"\bremot[oa]\b|teletrabajo|trabajo desde casa|home office", re.I)


def _get(url, intentos=2):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA_NAV, "Accept": "text/html", "Accept-Language": "es-CO,es;q=0.9"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            print(f"  [computrabajo] {e} en {url} (intento {i + 1})", file=sys.stderr)
            time.sleep(4 * (i + 1))
    return ""


def _limpio(txt):
    return re.sub(r"\s+", " ", html.unescape(_ETIQ.sub(" ", txt or ""))).strip()


def _titulo_de_slug(url):
    m = re.search(r"oferta-de-trabajo-de-(.+?)(?:-en-[a-z-]+)?-([0-9A-F]{20,})$", url)
    return m.group(1).replace("-", " ").capitalize() if m else ""


def listado(pagina):
    """[(url, titulo)] de una página de resultados, sin repetir."""
    vistos, salida = set(), []
    for href, texto in _ENLACE.findall(pagina):
        url = href if href.startswith("http") else BASE + href
        if url in vistos:
            continue
        vistos.add(url)
        salida.append((url, _limpio(texto) or _titulo_de_slug(url)))
    return salida


def job_posting(pagina):
    """El objeto JobPosting del JSON-LD de una página de detalle (o {})."""
    for bloque in _LD.findall(pagina):
        try:
            datos = json.loads(bloque.strip())
        except ValueError:
            continue
        pila = [datos]
        while pila:
            x = pila.pop()
            if isinstance(x, list):
                pila += x
            elif isinstance(x, dict):
                tipo = x.get("@type")
                if tipo == "JobPosting" or (isinstance(tipo, list) and "JobPosting" in tipo):
                    return x
                pila += [v for v in x.values() if isinstance(v, (dict, list))]
    return {}


def _fecha_rel(txt, hoy):
    t = normalizar(txt or "")
    if "hora" in t or "minuto" in t or "hoy" in t:
        return hoy.isoformat()
    if "ayer" in t:
        return (hoy - timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\s*dia", t)
    return (hoy - timedelta(days=int(m.group(1)))).isoformat() if m else ""


def detalle(url, titulo, pagina, hoy):
    jp = job_posting(pagina)
    lugares = jp.get("jobLocation") or []
    lugares = lugares if isinstance(lugares, list) else [lugares]
    sedes = []
    for l in lugares:
        d = (l or {}).get("address") or {}
        if isinstance(d, dict):
            sedes.append(", ".join(x for x in (d.get("addressLocality"), d.get("addressRegion")) if x))
    ubic = " · ".join(dict.fromkeys(s for s in sedes if s))
    if not ubic:
        m = re.search(r"-en-([a-z-]+)-[0-9A-F]{20,}$", url)
        ubic = m.group(1).replace("-", " ").title() if m else ""
    desc = _limpio(jp.get("description") or "")
    if not desc:
        m = re.search(r'<meta name="description" content="([^"]*)"', pagina)
        desc = _limpio(m.group(1)) if m else ""
    org = jp.get("hiringOrganization") or {}
    empresa = org.get("name") if isinstance(org, dict) else str(org)
    tipo_lugar = str(jp.get("jobLocationType") or "")
    remoto = "TELECOMMUTE" in tipo_lugar.upper() or bool(_REMOTO.search(titulo))
    hibrido = bool(_HIBRIDO.search(titulo + " " + desc))
    if not remoto and _REMOTO.search(desc) and not hibrido:
        remoto = bool(re.search(r"100\s*%\s*remot|modalidad:?\s*remot|trabajo remoto", desc, re.I))
    modalidad, rm = (("Remoto", "remote_local") if remoto else ("Híbrido", "hybrid") if hibrido
                     else ("Presencial", "no_remote"))
    salario = jp.get("baseSalary") or {}
    valor = (salario.get("value") or {}) if isinstance(salario, dict) else {}
    monto = valor.get("value") or valor.get("minValue") if isinstance(valor, dict) else ""
    codigo = re.search(r"([0-9A-F]{20,})$", url)
    return {
        "id": f"computrabajo-{codigo.group(1) if codigo else url.rsplit('-', 1)[-1]}",
        "fuente": "Computrabajo", "titulo": _limpio(jp.get("title")) or titulo,
        "empresa": empresa or "Empresa confidencial", "url": url, "modalidad": modalidad,
        "remoto": remoto, "remote_modality": rm, "paises": ["Colombia"], "ubicacion": ubic,
        "fecha": str(jp.get("datePosted") or "")[:10] or _fecha_rel((re.search(r"(Hace [^<]{1,25}|Ayer|Hoy)", pagina) or [""])[0], hoy),
        "descripcion": desc + " " + str(jp.get("employmentType") or ""),
        "salario": f"${int(float(monto)):,}".replace(",", ".") if monto else "",
    }


def buscar(cfg, perfil, hoy=None, pausa=2.0):
    """cfg: {"busquedas": [...], "max_detalles": 40}. Devuelve (ofertas, muestra)."""
    from .comun import oferta
    hoy = hoy or date.today()
    candidatos, vistos, total = [], set(), 0
    for q in cfg.get("busquedas", []):
        slug = re.sub(r"[^a-z0-9]+", "-", normalizar(q)).strip("-")
        for sufijo in ("-en-bogota-dc", ""):  # Bogotá primero; sin ciudad trae también las remotas
            pagina = _get(f"{BASE}/trabajo-de-{slug}{sufijo}")
            time.sleep(pausa)
            for url, titulo in listado(pagina):
                total += 1
                if url not in vistos and pasa_titulo(titulo, perfil):
                    vistos.add(url)
                    candidatos.append((url, titulo))
    ofertas, muestra = [], []
    for url, titulo in candidatos[: cfg.get("max_detalles", 40)]:
        pagina = _get(url)
        time.sleep(pausa)
        if not pagina:
            continue
        o = oferta(**detalle(url, titulo, pagina, hoy))
        ofertas.append(o)
        if len(muestra) < 3:
            muestra.append({k: str(v)[:200] for k, v in o.items()})
    print(f"  [computrabajo] {total} vistas, {len(candidatos)} encajan por cargo, {len(ofertas)} guardadas")
    if total and not candidatos:
        return [], muestra
    if not total:
        raise RuntimeError("Computrabajo no devolvió resultados (¿cambió la página o bloqueó?)")
    return ofertas, muestra
