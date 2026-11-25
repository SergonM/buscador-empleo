"""Fuentes de trabajo remoto sin clave: Remotive e Himalayas.

Remotive pide pocas llamadas al día (máx. ~4) y citar la fuente; Himalayas pide atribución.
Ambas se citan en cada tarjeta ("Ver oferta en …") y en el pie de la página.
"""
import time
import urllib.parse
from datetime import datetime, timezone

from .comun import get_json, oferta

ZONAS_OK = ["worldwide", "anywhere", "global", "latam", "latin america", "americas", "south america", "colombia"]


def _zona_ok(texto):
    t = (texto or "").lower()
    return not t or any(z in t for z in ZONAS_OK)


def remotive(categorias=("data", "product", "all-others"), busquedas=("security",)):
    ofertas, muestra = {}, []
    llamadas = [{"category": c} for c in categorias] + [{"search": s} for s in busquedas]
    for params in llamadas[:4]:
        data = get_json("https://remotive.com/api/remote-jobs?" + urllib.parse.urlencode(params), etiqueta="remotive")
        time.sleep(2)
        for j in (data or {}).get("jobs", []):
            if len(muestra) < 2:
                muestra.append({k: str(v)[:200] for k, v in j.items()})
            zona = j.get("candidate_required_location") or ""
            if not _zona_ok(zona):
                continue
            o = oferta(
                id=f"remotive-{j.get('id')}", fuente="Remotive", titulo=j.get("title"),
                empresa=j.get("company_name"), url=j.get("url"), modalidad="Remoto", remoto=True,
                remote_modality="fully_remote", paises=[zona or "Worldwide"], ubicacion=zona,
                fecha=str(j.get("publication_date") or "")[:10], categoria=j.get("category") or "",
                descripcion=j.get("description") or "", salario=j.get("salary") or "",
            )
            ofertas.setdefault(o["id"], o)
        print(f"  [remotive] {params}: acumuladas {len(ofertas)}")
    return list(ofertas.values()), muestra


SEN_HIMALAYAS = {"entry-level": (2, "Junior"), "entry level": (2, "Junior"), "internship": (1, "Práctica"),
                 "mid-level": (3, "Semi Senior"), "senior": (4, "Senior"), "manager": (5, "Manager"),
                 "director": (5, "Director"), "executive": (5, "Ejecutivo")}


def himalayas(busquedas, paginas=1):
    ofertas, muestra = {}, []
    for q in busquedas:
        for page in range(1, paginas + 1):
            url = "https://himalayas.app/jobs/api/search?" + urllib.parse.urlencode({"q": q, "page": page, "sort": "recent"})
            data = get_json(url, etiqueta="himalayas")
            time.sleep(1.5)
            jobs = (data or {}).get("jobs") or []
            for j in jobs:
                if len(muestra) < 2:
                    muestra.append({k: str(v)[:200] for k, v in j.items()})
                restr = j.get("locationRestrictions") or []
                nombres = [r.get("name", "") if isinstance(r, dict) else str(r) for r in restr]
                zona = ", ".join(nombres)
                if not _zona_ok(zona):
                    continue
                sens = [str(s).lower() for s in (j.get("seniority") or [])]
                niveles = [SEN_HIMALAYAS.get(s, (None, "")) for s in sens]
                niveles = [n for n in niveles if n[0]]
                sid, sen = min(niveles) if niveles else (None, "")
                pub = j.get("pubDate")
                try:
                    fecha = datetime.fromtimestamp(int(pub), tz=timezone.utc).date().isoformat()
                except (TypeError, ValueError):
                    fecha = str(pub or "")[:10]
                o = oferta(
                    id=f"himalayas-{j.get('guid') or j.get('applicationLink')}", fuente="Himalayas",
                    titulo=j.get("title"), empresa=j.get("companyName"),
                    url=j.get("applicationLink") or j.get("guid"), modalidad="Remoto", remoto=True,
                    remote_modality="fully_remote", paises=nombres or ["Worldwide"], ubicacion=zona or "Worldwide",
                    fecha=fecha, seniority_id=sid, seniority=sen,
                    descripcion=(j.get("excerpt") or "") + " " + (j.get("description") or ""),
                )
                ofertas.setdefault(o["id"], o)
            if not jobs:
                break
        print(f"  [himalayas] '{q}': acumuladas {len(ofertas)}")
    return list(ofertas.values()), muestra
