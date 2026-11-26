"""Fuente: tableros públicos de empresas (Greenhouse, Lever, Ashby, SmartRecruiters, Workable).

Todos son endpoints públicos sin clave que las propias empresas exponen para su página de empleo.
La lista de empresas está en perfil.json → "empresas". Una empresa que falle o no exista se salta.
Se guardan solo ofertas en Colombia o remotas con LATAM/global (el resto se filtra aquí mismo
para no cargar cientos de ofertas de Brasil o EE. UU.).
"""
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone

from .comun import get_json, oferta

# Una ubicación sirve si menciona alguna de estas palabras.
_UBIC_OK = re.compile(
    r"colombia|bogot|latam|latin america|latinoam|america latina|south america|americas|worldwide|anywhere|global|remote|remoto",
    re.I,
)
_REMOTO = re.compile(r"remote|remoto|teletrabajo|anywhere|work from home", re.I)
_HIBRIDO = re.compile(r"h[ií]brid|hybrid", re.I)


def _ubic_ok(texto):
    return bool(_UBIC_OK.search(texto or ""))


def _fecha_ms(v):
    try:
        return datetime.fromtimestamp(int(v) / 1000, tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def _modalidad(ubic, workplace=""):
    w = (workplace or "").lower()
    if w in ("remote", "remoto") or (not w and _REMOTO.search(ubic or "")):
        return "Remoto", True, "fully_remote"
    if w == "hybrid" or _HIBRIDO.search(ubic or ""):
        return "Híbrido", False, "hybrid"
    if w in ("onsite", "on-site", "in office"):
        return "Presencial", False, "no_remote"
    return "No indica", False, "no_remote"


def _paises(ubic, codigo=""):
    p = [ubic] if ubic else []
    if re.search(r"bogot", ubic or "", re.I) or (codigo or "").upper() in ("CO", "COL"):
        p.append("Colombia")
    return p


def _hacer(fuente, empresa, id_, titulo, url, ubic, workplace="", fecha="", desc="", codigo="", extra=None):
    modalidad, remoto, rm = _modalidad(ubic, workplace)
    return oferta(
        id=f"{fuente.lower()}-{id_}", fuente=fuente, titulo=titulo, empresa=empresa, url=url,
        modalidad=modalidad, remoto=remoto, remote_modality=rm, paises=_paises(ubic, codigo),
        ubicacion=ubic, fecha=fecha, descripcion=desc, **(extra or {}),
    )


def greenhouse(slug, nombre):
    data = get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true", intentos=2, etiqueta="greenhouse")
    salida = []
    for j in (data or {}).get("jobs", []):
        ubic = (j.get("location") or {}).get("name", "")
        oficinas = " ".join(o.get("name", "") for o in j.get("offices") or [])
        ubic_total = (ubic + " " + oficinas).strip()
        if not _ubic_ok(ubic_total):
            continue
        salida.append(_hacer("Greenhouse", nombre, j.get("id"), j.get("title"), j.get("absolute_url"), ubic_total,
                             fecha=str(j.get("updated_at") or j.get("first_published") or "")[:10],
                             desc=j.get("content") or ""))
    return salida


def lever(slug, nombre):
    data = get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json", intentos=2, etiqueta="lever")
    salida = []
    for j in data if isinstance(data, list) else []:
        cat = j.get("categories") or {}
        ubic = " · ".join(dict.fromkeys([cat.get("location") or ""] + list(cat.get("allLocations") or [])))
        ubic = ubic.strip(" ·")
        wt = j.get("workplaceType") or ""
        if not _ubic_ok(ubic) and wt != "remote":
            continue
        listas = " ".join(f"{l.get('text', '')} {l.get('content', '')}" for l in j.get("lists") or [])
        salida.append(_hacer("Lever", nombre, j.get("id"), j.get("text"), j.get("hostedUrl"), ubic, wt,
                             _fecha_ms(j.get("createdAt")), (j.get("descriptionPlain") or "") + " " + listas,
                             j.get("country") or ""))
    return salida


def ashby(slug, nombre):
    data = get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true", intentos=2, etiqueta="ashby")
    salida = []
    for j in (data or {}).get("jobs", []):
        if j.get("isListed") is False:
            continue
        ubic = " · ".join([j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]).strip(" ·")
        wt = (j.get("workplaceType") or "").lower()
        if j.get("isRemote") and wt != "hybrid":
            wt = "remote"
        if not _ubic_ok(ubic) and wt != "remote":
            continue
        pais = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry") or ""
        comp = (j.get("compensation") or {}).get("compensationTierSummary") or ""
        salida.append(_hacer("Ashby", nombre, j.get("id") or j.get("jobUrl"), j.get("title"), j.get("jobUrl"),
                             ubic + (f" · {pais}" if pais and pais not in ubic else ""), wt,
                             str(j.get("publishedAt") or "")[:10], j.get("descriptionPlain") or j.get("descriptionHtml") or "",
                             "CO" if "colombia" in pais.lower() else "", {"salario": comp}))
    return salida


def smartrecruiters(slug, nombre):
    data = get_json(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?country=co&limit=100", intentos=2, etiqueta="smartrecruiters")
    salida = []
    for j in (data or {}).get("content", []):
        loc = j.get("location") or {}
        ubic = ", ".join(x for x in [loc.get("city"), loc.get("region"), (loc.get("country") or "").upper()] if x)
        wt = "remote" if loc.get("remote") else ("hybrid" if loc.get("hybrid") else "")
        nivel = ((j.get("experienceLevel") or {}).get("label") or "")
        salida.append(_hacer("SmartRecruiters", (j.get("company") or {}).get("name") or nombre, j.get("id"), j.get("name"),
                             f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}", ubic, wt,
                             str(j.get("releasedDate") or "")[:10], nivel + " " + ((j.get("function") or {}).get("label") or ""),
                             loc.get("country") or ""))
    return salida


def workable(slug, nombre):
    data = get_json(f"https://apply.workable.com/api/v1/widget/accounts/{slug}", intentos=2, etiqueta="workable")
    salida = []
    for j in (data or {}).get("jobs", []):
        locs = j.get("locations") or [{"country": j.get("country"), "city": j.get("city"), "countryCode": ""}]
        ubic = " · ".join(", ".join(x for x in [l.get("city"), l.get("country")] if x) for l in locs)
        codigos = [str(l.get("countryCode") or "") for l in locs]
        wt = "remote" if j.get("telecommuting") else ""
        if not _ubic_ok(ubic) and "CO" not in codigos and wt != "remote":
            continue
        salida.append(_hacer("Workable", (data or {}).get("name") or nombre, j.get("shortcode"), j.get("title"),
                             j.get("url") or j.get("shortlink"), ubic, wt, str(j.get("published_on") or "")[:10],
                             j.get("department") or "", "CO" if "CO" in codigos else ""))
    return salida


ATS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "smartrecruiters": smartrecruiters, "workable": workable}


def buscar(empresas, pausa=0.4):
    """empresas: {"greenhouse": {"slug": "Nombre", ...}, "lever": {...}, ...}. Devuelve (ofertas, muestra)."""
    ofertas, muestra, por_empresa = {}, [], {}
    for ats, lista in empresas.items():
        fn = ATS.get(ats)
        if not fn or not isinstance(lista, dict):
            continue
        for slug, nombre in lista.items():
            try:
                encontradas = fn(slug, nombre)
            except Exception as e:  # noqa: BLE001  una empresa rota no tumba la fuente
                print(f"  [{ats}] {slug} falló: {e}", file=sys.stderr)
                encontradas = []
            for o in encontradas:
                if o["titulo"] and o["url"]:
                    ofertas.setdefault(o["id"], o)
                    if len(muestra) < 3:
                        muestra.append({k: str(v)[:200] for k, v in o.items()})
            por_empresa[nombre] = len(encontradas)
            time.sleep(pausa)
    activas = {k: v for k, v in por_empresa.items() if v}
    print(f"  [empresas] {len(ofertas)} ofertas en Colombia/remoto de {len(activas)} empresas: {json.dumps(activas, ensure_ascii=False)}")
    return list(ofertas.values()), muestra
