"""Ejecuta la búsqueda diaria: python -m buscador"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .filtros import deduplicar, motivo_descarte
from .fuentes import ats, computrabajo, getonboard, linkedin_indeed, remotos, workday
from .pagina import archivos_pwa, generar
from .ranking import puntuar

RAIZ = Path(__file__).resolve().parent.parent
HISTORIAL = RAIZ / "data" / "historial.json"
DOCS = RAIZ / "docs"
# Fuentes que solo traen lo más reciente: sus ofertas de días anteriores se conservan.
INCREMENTALES = {"LinkedIn", "Indeed", "Jobicy", "Remote OK", "Remotive", "Himalayas"}


def _leer(p, defecto):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def main():
    perfil = _leer(RAIZ / "perfil.json", None)
    hoy = datetime.now(timezone(timedelta(hours=-5))).date()  # hora Bogotá
    historial = _leer(HISTORIAL, {})  # id -> fecha en que la vimos por primera vez

    activas = perfil.get("fuentes", {"getonboard": True})
    jobicy_cfg = perfil.get("jobicy", {})
    fuentes = [
        ("LinkedIn + Indeed", "linkedin_indeed", lambda: linkedin_indeed.buscar(perfil["jobspy"])),
        ("Workday (multinacionales)", "workday", lambda: workday.buscar(perfil.get("workday", []), perfil, hoy)),
        ("Portales de empresas", "empresas", lambda: ats.buscar(perfil.get("empresas", {}))),
        ("Computrabajo", "computrabajo", lambda: computrabajo.buscar(perfil.get("computrabajo", {}), perfil, hoy)),
        ("GetOnBoard", "getonboard", lambda: getonboard.buscar(perfil["busquedas"])),
        ("Remotive", "remotive", lambda: remotos.remotive()),
        ("Himalayas", "himalayas", lambda: remotos.himalayas(perfil.get("himalayas", []))),
        ("Jobicy", "jobicy", lambda: remotos.jobicy(jobicy_cfg.get("geos", ["latam"]), jobicy_cfg.get("tags", []))),
        ("Remote OK", "remoteok", lambda: remotos.remoteok()),
    ]
    inicio = time.time()

    def correr(nombre, fn):
        t0 = time.time()
        print(f"Buscando en {nombre}…")
        try:
            lista, muestra = fn()
            return nombre, lista, muestra, {"ok": True, "ofertas": len(lista), "segundos": round(time.time() - t0)}
        except Exception as e:  # noqa: BLE001  una fuente rota no tumba la corrida
            print(f"  {nombre} falló: {e}", file=sys.stderr)
            return nombre, [], [], {"ok": False, "ofertas": 0, "segundos": round(time.time() - t0), "error": str(e)[:120]}

    # Las fuentes corren en paralelo: cada una tiene sus propias pausas para no saturar a nadie.
    elegidas = [(n, fn) for n, clave, fn in fuentes if activas.get(clave)]
    crudas, estado, muestras = [], {}, {}
    with ThreadPoolExecutor(max_workers=len(elegidas) or 1) as ex:
        for nombre, lista, muestra, est in ex.map(lambda x: correr(*x), elegidas):
            if est["ok"] and not lista:
                est["ok"], est["error"] = False, "no devolvió ofertas"
            estado[nombre] = est
            muestras[nombre] = muestra
            crudas += lista
    if not crudas:
        print("No llegó ninguna oferta: todas las fuentes fallaron. No se cambia la página.", file=sys.stderr)
        return 1

    # Ofertas de días anteriores: LinkedIn/Indeed solo traen las últimas 24 h, y si una fuente
    # falla hoy no queremos que sus ofertas desaparezcan. Se conservan hasta `dias_mostrar`.
    previas = _leer(DOCS / "ofertas.json", {}).get("ofertas", [])
    ids_hoy = {o["id"] for o in crudas}
    fuentes_ok = {o["fuente"] for o in crudas}
    # Workday limita a veces por empresa (429): si una empresa no respondió hoy, se conservan sus ofertas.
    empresas_ok = {(o["fuente"], o["empresa"]) for o in crudas}
    conservar = [o for o in previas if o["id"] not in ids_hoy
                 and (o.get("fuente") in INCREMENTALES or o.get("fuente") not in fuentes_ok
                      or (o.get("fuente") == "Workday" and (o["fuente"], o.get("empresa")) not in empresas_ok))]

    # Al quitar duplicados gana la fuente más directa (portal de la empresa > agregadores).
    prioridad = {f: i for i, f in enumerate(perfil.get("fuentes_directas", []))}
    crudas.sort(key=lambda o: prioridad.get(o["fuente"], 99))

    ofertas, descartes = [], {}
    for o in deduplicar(crudas):
        m = motivo_descarte(o, perfil)
        if m:
            clave = m.split(" (")[0]
            descartes[clave] = descartes.get(clave, 0) + 1
            continue
        ofertas.append(puntuar(o, perfil, hoy))

    limite = (hoy - timedelta(days=perfil["dias_mostrar"])).isoformat()
    # Se vuelven a filtrar por si cambió perfil.json.
    ofertas += [o for o in conservar if o.get("visto", "") >= limite and not motivo_descarte(o, perfil)]
    ofertas = deduplicar(ofertas)
    ofertas = [o for o in ofertas if not o["fecha"] or o["fecha"] >= limite]
    for o in ofertas:
        o["visto"] = historial.setdefault(o["id"], hoy.isoformat())
        o["nueva"] = o["visto"] == hoy.isoformat()
        o.pop("descripcion", None)
    ofertas.sort(key=lambda o: (o["puntaje"], o["fecha"]), reverse=True)

    # Limpia el historial de más de 90 días.
    corte = (hoy - timedelta(days=90)).isoformat()
    historial = {k: v for k, v in historial.items() if v >= corte}

    anterior = _leer(DOCS / "ofertas.json", {}).get("resumen", {})
    historia = [h for h in anterior.get("historia", []) if h.get("fecha") != hoy.isoformat()][-29:]
    historia.append({"fecha": hoy.isoformat(), "revisadas": len(crudas), "mostradas": len(ofertas),
                     "nuevas": sum(o["nueva"] for o in ofertas)})
    resumen = {
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "fecha": hoy.isoformat(),
        "revisadas": len(crudas),
        "mostradas": len(ofertas),
        "nuevas": sum(o["nueva"] for o in ofertas),
        "descartes": dict(sorted(descartes.items(), key=lambda x: -x[1])),
        "fuentes": [f for f, e in estado.items() if e["ofertas"]],
        "por_fuente": {f: e["ofertas"] for f, e in estado.items()},
        "estado_fuentes": estado,
        "duracion": round(time.time() - inicio),
        "historia": historia,
    }
    HISTORIAL.parent.mkdir(exist_ok=True)
    HISTORIAL.write_text(json.dumps(historial, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "data" / "muestras.json").write_text(json.dumps(muestras, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    DOCS.mkdir(exist_ok=True)
    (DOCS / "ofertas.json").write_text(json.dumps({"resumen": resumen, "ofertas": ofertas}, ensure_ascii=False, indent=1), encoding="utf-8")
    (DOCS / "index.html").write_text(generar(ofertas, resumen, perfil.get("carta", {})), encoding="utf-8")
    for nombre, contenido in archivos_pwa().items():
        (DOCS / nombre).write_text(contenido, encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
