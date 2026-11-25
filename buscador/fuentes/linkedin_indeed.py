"""Fuente: LinkedIn e Indeed Colombia vía JobSpy (python-jobspy).

Bajo volumen a propósito: pocas búsquedas, solo ofertas de las últimas `horas`,
pausa entre llamadas y sin proxies. Si JobSpy falla, la corrida sigue con las demás fuentes.
"""
import math
import re
import sys
import time

from .comun import oferta

NIVEL_LINKEDIN = {
    "internship": (1, "Práctica"),
    "entry level": (2, "Junior"),
    "associate": (2, "Junior"),
    "mid-senior level": (4, "Senior"),
    "director": (5, "Director"),
    "executive": (5, "Ejecutivo"),
}
_HIBRIDO = re.compile(r"h[ií]brid|hybrid", re.I)


def _v(x):
    """Convierte NaN/None de pandas en None."""
    if x is None:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def _a_oferta(r):
    site = _v(r.get("site")) or ""
    fuente = "LinkedIn" if site == "linkedin" else "Indeed" if site == "indeed" else site.title()
    ubic = str(_v(r.get("location")) or "")
    desc = str(_v(r.get("description")) or "")
    titulo = str(_v(r.get("title")) or "")
    remoto = bool(_v(r.get("is_remote"))) or bool(re.search(r"\b(remote|remoto|teletrabajo)\b", titulo, re.I))
    if remoto:
        modalidad, rm = "Remoto", "fully_remote"
    elif _HIBRIDO.search(desc) or _HIBRIDO.search(ubic):
        modalidad, rm = "Híbrido", "hybrid"
    else:
        modalidad, rm = "Presencial o híbrido", "no_remote"
    # Las búsquedas se hacen en Colombia; si la ubicación no dice país, se asume Colombia.
    paises = ["Colombia"] if ("colombia" in ubic.lower() or site == "indeed" or not ubic) else [ubic]
    nivel = str(_v(r.get("job_level")) or "").lower()
    sid, sen = NIVEL_LINKEDIN.get(nivel, (None, ""))
    fecha = _v(r.get("date_posted"))
    lo, hi, cur = _v(r.get("min_amount")), _v(r.get("max_amount")), _v(r.get("currency")) or ""
    salario = f"{cur} {int(lo):,}–{int(hi):,}".replace(",", ".").strip() if lo and hi else ""
    return oferta(
        id=f"{site}-{_v(r.get('id')) or _v(r.get('job_url'))}",
        fuente=fuente,
        titulo=_v(r.get("title")) or "",
        empresa=_v(r.get("company")) or "",
        url=_v(r.get("job_url")) or "",
        modalidad=modalidad,
        remoto=remoto,
        remote_modality=rm,
        paises=paises,
        ubicacion=ubic,
        fecha=fecha.isoformat() if hasattr(fecha, "isoformat") else str(fecha or "")[:10],
        seniority_id=sid,
        seniority=sen,
        descripcion=desc + " " + str(_v(r.get("job_function")) or ""),
        salario=salario,
    )


def buscar(cfg):
    """cfg: perfil['jobspy']. Devuelve (ofertas, muestra)."""
    try:
        from jobspy import scrape_jobs
    except Exception as e:  # noqa: BLE001
        print(f"  [jobspy] no está instalado: {e}", file=sys.stderr)
        return [], []
    ofertas, muestra = {}, []
    sitios = [
        ("indeed", {"location": cfg.get("ciudad", "Bogotá"), "country_indeed": "Colombia"}),
        ("linkedin", {"location": cfg.get("pais", "Colombia")}),
    ]
    for sitio, extra in sitios:
        fallos = 0
        terminos = cfg["busquedas"] if sitio == "indeed" else cfg.get("busquedas_linkedin", cfg["busquedas"])
        for termino in terminos:
            if fallos >= 2:  # si el sitio nos está bloqueando, no insistir
                print(f"  [jobspy] {sitio}: demasiados errores, se salta el resto")
                break
            try:
                df = scrape_jobs(
                    site_name=[sitio], search_term=termino,
                    results_wanted=cfg.get("resultados", 25) if sitio == "indeed" else cfg.get("resultados_linkedin", 20),
                    hours_old=cfg.get("horas", 24), description_format="plain", verbose=0, **extra,
                )
                errores = (getattr(df, "attrs", {}) or {}).get("errors") or {}
                if errores:
                    fallos += 1
                    print(f"  [jobspy] {sitio} '{termino}': {errores}", file=sys.stderr)
                filas = df.to_dict("records")
                for r in filas:
                    if len(muestra) < 4:
                        muestra.append({k: str(v)[:200] for k, v in r.items()})
                    o = _a_oferta(r)
                    if o["titulo"] and o["url"]:
                        ofertas.setdefault(o["id"], o)
                print(f"  [jobspy] {sitio} '{termino}': {len(filas)} (acumuladas {len(ofertas)})")
            except Exception as e:  # noqa: BLE001
                fallos += 1
                print(f"  [jobspy] {sitio} '{termino}' falló: {e}", file=sys.stderr)
            time.sleep(cfg.get("pausa", 6) if sitio == "indeed" else cfg.get("pausa_linkedin", 25))
    return list(ofertas.values()), muestra
