"""Fuente: portales de empleo Workday de multinacionales (J&J, Medtronic, Pfizer, Mastercard…).

Workday expone para cada empresa el mismo endpoint público que usa su página de empleo:
POST https://{host}/wday/cxs/{tenant}/{sitio}/jobs. Se busca "Colombia", se descartan en el acto
los cargos que no encajan (senior, otras áreas) y solo de los que quedan se pide el detalle
(descripción, sedes y fecha). Workday limita ráfagas (429): se va despacio y se reintenta.
"""
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

from ..filtros import areas_en_titulo, es_generico
from ..texto import encontradas, normalizar
from .comun import UA, oferta

_HIBRIDO = re.compile(r"h[ií]brid|hybrid", re.I)
_REMOTO = re.compile(r"\bremote|remoto|teletrabajo", re.I)


def _pedir(url, cuerpo=None, intentos=3):
    for i in range(intentos):
        try:
            datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
            req = urllib.request.Request(url, data=datos, headers={
                "User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 422):
                print(f"  [workday] {e.code} en {url}", file=sys.stderr)
                return None
            espera = 10 * (i + 1) if e.code == 429 else 3 * (i + 1)
            print(f"  [workday] {e.code} en {url} (intento {i + 1}, espero {espera} s)", file=sys.stderr)
            time.sleep(espera)
        except Exception as e:  # noqa: BLE001
            print(f"  [workday] error {e} en {url} (intento {i + 1})", file=sys.stderr)
            time.sleep(3 * (i + 1))
    return None


def _fecha_rel(txt, hoy):
    """'Posted Today', 'Posted 5 Days Ago', 'Posted 30+ Days Ago' → fecha ISO aproximada."""
    t = (txt or "").lower()
    if "today" in t or "hoy" in t:
        return hoy.isoformat()
    if "yesterday" in t or "ayer" in t:
        return (hoy - timedelta(days=1)).isoformat()
    m = re.search(r"(\d+)\+?\s*(days|dias|días)", t)
    return (hoy - timedelta(days=int(m.group(1)))).isoformat() if m else ""


def pasa_titulo(titulo, perfil):
    t = normalizar(titulo)
    junior = encontradas(t, perfil["junior_titulo"])
    if encontradas(t, perfil["excluir_titulo"]) and not junior:
        return False
    if encontradas(t, perfil.get("excluir_otros_titulo", [])):
        return False
    return bool(areas_en_titulo(t, perfil)) or es_generico(t, perfil)


def _empresa(host, tenant, site, nombre, perfil, hoy, max_detalles=12, pausa=1.5):
    base = f"https://{host}/wday/cxs/{tenant}/{site}"
    publicos = f"https://{host}/{site}"
    candidatos, offset, total = [], 0, None
    while offset < 200:
        data = _pedir(f"{base}/jobs", {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": "Colombia"})
        time.sleep(pausa)
        if not data:
            break
        total = data.get("total") if total is None else total
        posts = data.get("jobPostings") or []
        for p in posts:
            if p.get("title") and p.get("externalPath") and pasa_titulo(p["title"], perfil):
                candidatos.append(p)
        offset += 20
        if not posts or offset >= (total or 0):
            break
    salida = []
    for p in candidatos[:max_detalles]:
        det = _pedir(f"{base}{p['externalPath']}") or {}
        time.sleep(pausa)
        info = det.get("jobPostingInfo") or {}
        sedes = [info.get("location") or p.get("locationsText") or ""] + list(info.get("additionalLocations") or [])
        ubic = " · ".join(s for s in dict.fromkeys(sedes) if s)
        pais = ((info.get("country") or {}).get("descriptor") or "")
        texto_ubic = f"{ubic} {pais}"
        if "colombia" not in normalizar(texto_ubic) and "bogota" not in normalizar(texto_ubic):
            continue
        desc = info.get("jobDescription") or ""
        remoto = bool(_REMOTO.search(info.get("remoteType") or "")) or bool(_REMOTO.search(p["title"]))
        hibrido = bool(_HIBRIDO.search(info.get("remoteType") or "") or _HIBRIDO.search(desc))
        modalidad, rm = ("Remoto", "remote_local") if remoto else ("Híbrido", "hybrid") if hibrido else ("Presencial o híbrido", "no_remote")
        # Si hay varias sedes, mostramos primero la de Colombia.
        en_co = [s for s in sedes if re.search(r"colombia|bogot", s or "", re.I)]
        salida.append(oferta(
            id=f"workday-{tenant}-{info.get('jobReqId') or p['externalPath'].rsplit('_', 1)[-1]}",
            fuente="Workday", titulo=p["title"], empresa=nombre,
            url=info.get("externalUrl") or publicos + p["externalPath"], modalidad=modalidad, remoto=remoto,
            remote_modality=rm, paises=["Colombia"], ubicacion=(en_co[0] if en_co else ubic),
            fecha=str(info.get("startDate") or "")[:10] or _fecha_rel(p.get("postedOn"), hoy),
            descripcion=desc + " " + (info.get("timeType") or ""),
        ))
    print(f"  [workday] {nombre}: {total or 0} en Colombia, {len(candidatos)} encajan por cargo, {len(salida)} guardadas")
    return salida


def buscar(empresas, perfil, hoy=None, hilos=5):
    """empresas: lista de "host tenant sitio Nombre". Devuelve (ofertas, muestra)."""
    hoy = hoy or date.today()
    ofertas, muestra = {}, []

    def una(linea):
        partes = linea.split(maxsplit=3)
        if len(partes) < 4:
            return []
        host, tenant, site, nombre = partes
        try:
            return _empresa(host, tenant, site, nombre, perfil, hoy)
        except Exception as e:  # noqa: BLE001
            print(f"  [workday] {nombre} falló: {e}", file=sys.stderr)
            return []

    # Varias empresas a la vez (cada una va despacio); hilos pocos para no provocar 429.
    with ThreadPoolExecutor(max_workers=hilos) as ex:
        for lista in ex.map(una, empresas):
            for o in lista:
                ofertas.setdefault(o["id"], o)
                if len(muestra) < 3:
                    muestra.append({k: str(v)[:200] for k, v in o.items()})
    return list(ofertas.values()), muestra
