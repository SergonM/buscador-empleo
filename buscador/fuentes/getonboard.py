"""Fuente: GetOnBoard (API pública, sin clave).

Docs: https://www.getonbrd.com/api-doc
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.getonbrd.com/api/v0/search/jobs"
UA = "Mozilla/5.0 (compatible; buscador-empleo/1.0; +https://github.com/SergonM/buscador-empleo)"

SENIORITY = {1: "Sin experiencia", 2: "Junior", 3: "Semi Senior", 4: "Senior", 5: "Experto"}
MODALIDAD = {
    "fully_remote": "Remoto",
    "remote_local": "Remoto (local)",
    "temporarily_remote": "Remoto temporal",
    "hybrid": "Híbrido",
    "no_remote": "Presencial",
}


def _get(url, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  [getonboard] error {e} en {url} (intento {i + 1})", file=sys.stderr)
            time.sleep(2 * (i + 1))
    return None


def _rel_id(attrs, nombre):
    """Devuelve el id de una relación tipo {'data': {'id': ..}}."""
    v = attrs.get(nombre)
    if isinstance(v, dict):
        d = v.get("data")
        if isinstance(d, dict):
            return d.get("id")
    return v if isinstance(v, (int, str)) else None


def _empresa(attrs):
    c = attrs.get("company")
    if isinstance(c, dict):
        d = c.get("data") or {}
        a = d.get("attributes") or {}
        return a.get("name") or d.get("id") or ""
    return str(c or "")


def _fecha(v):
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc).date().isoformat()
        if isinstance(v, str) and v:
            return v[:10]
    except Exception:  # noqa: BLE001
        pass
    return ""


def _a_oferta(item):
    a = item.get("attributes") or {}
    sen_id = _rel_id(a, "seniority")
    try:
        sen_id = int(sen_id) if sen_id is not None else None
    except (TypeError, ValueError):
        sen_id = None
    rm = a.get("remote_modality") or ("fully_remote" if a.get("remote") else "")
    paises = a.get("countries") or []
    if isinstance(paises, str):
        paises = [paises]
    ubic = ", ".join(str(p) for p in paises)
    if a.get("remote_zone"):
        ubic = (ubic + " · " if ubic else "") + str(a.get("remote_zone"))
    partes = [a.get(k) or "" for k in ("description_headline", "description", "functions", "desirable", "projects")]
    return {
        "id": f"gob-{item.get('id')}",
        "fuente": "GetOnBoard",
        "titulo": (a.get("title") or "").strip(),
        "empresa": _empresa(a),
        "url": (item.get("links") or {}).get("public_url") or f"https://www.getonbrd.com/jobs/{item.get('id')}",
        "modalidad": MODALIDAD.get(rm, rm or "No indica"),
        "remoto": rm in ("fully_remote", "remote_local", "temporarily_remote"),
        "remote_modality": rm,
        "paises": [str(p) for p in paises],
        "ubicacion": ubic,
        "fecha": _fecha(a.get("published_at")),
        "seniority_id": sen_id,
        "seniority": SENIORITY.get(sen_id, ""),
        "categoria": a.get("category_name") or "",
        "idioma": a.get("lang") or "",
        "descripcion": " ".join(str(p) for p in partes),
        "salario": _salario(a),
    }


def _salario(a):
    lo, hi = a.get("min_salary"), a.get("max_salary")
    if lo and hi:
        return f"USD {lo:,}–{hi:,}".replace(",", ".")
    if lo or hi:
        return f"USD {(lo or hi):,}".replace(",", ".")
    return ""


def buscar(consultas, paginas=3, por_pagina=100, pausa=0.7):
    """Busca cada consulta y devuelve (ofertas, crudos). Sin duplicados por id."""
    vistos = {}
    crudos = []
    fallidas = 0
    for q in consultas:
        if fallidas >= 2 and not vistos:  # nos están bloqueando: no gastar minutos reintentando
            print("  [getonboard] 2 consultas seguidas sin respuesta: se salta el resto", file=sys.stderr)
            break
        for page in range(1, paginas + 1):
            params = {"query": q, "per_page": por_pagina, "page": page, "expand": '["company"]'}
            data = _get(f"{BASE}?{urllib.parse.urlencode(params)}")
            time.sleep(pausa)
            if not data:
                fallidas += page == 1
                break
            items = data.get("data") or []
            for it in items:
                if len(crudos) < 3:
                    crudos.append(it)
                o = _a_oferta(it)
                vistos.setdefault(o["id"], o)
            total = (data.get("meta") or {}).get("total_pages") or 1
            if page >= total or not items:
                break
        print(f"  [getonboard] '{q}': acumuladas {len(vistos)}")
    return list(vistos.values()), crudos
