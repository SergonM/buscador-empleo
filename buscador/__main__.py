"""Ejecuta la búsqueda diaria: python -m buscador"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .filtros import deduplicar, motivo_descarte
from .fuentes import getonboard, linkedin_indeed, remotos
from .pagina import generar
from .ranking import puntuar

RAIZ = Path(__file__).resolve().parent.parent
HISTORIAL = RAIZ / "data" / "historial.json"
DOCS = RAIZ / "docs"
INCREMENTALES = {"LinkedIn", "Indeed"}


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
    fuentes = [
        ("GetOnBoard", "getonboard", lambda: getonboard.buscar(perfil["busquedas"])),
        ("LinkedIn + Indeed", "linkedin_indeed", lambda: linkedin_indeed.buscar(perfil["jobspy"])),
        ("Remotive", "remotive", lambda: remotos.remotive()),
        ("Himalayas", "himalayas", lambda: remotos.himalayas(perfil.get("himalayas", []))),
    ]
    crudas, estado, muestras = [], {}, {}
    for nombre, clave, fn in fuentes:
        if not activas.get(clave):
            continue
        print(f"Buscando en {nombre}…")
        try:
            lista, muestra = fn()
        except Exception as e:  # noqa: BLE001  una fuente rota no tumba la corrida
            print(f"  {nombre} falló: {e}", file=sys.stderr)
            lista, muestra = [], []
        estado[nombre] = len(lista)
        muestras[clave] = muestra
        crudas += lista
    if not crudas:
        print("No llegó ninguna oferta: todas las fuentes fallaron. No se cambia la página.", file=sys.stderr)
        return 1

    # Ofertas de días anteriores: LinkedIn/Indeed solo traen las últimas 24 h, y si una fuente
    # falla hoy no queremos que sus ofertas desaparezcan. Se conservan hasta `dias_mostrar`.
    previas = _leer(DOCS / "ofertas.json", {}).get("ofertas", [])
    ids_hoy = {o["id"] for o in crudas}
    fuentes_ok = {o["fuente"] for o in crudas}
    conservar = [o for o in previas if o["id"] not in ids_hoy
                 and (o.get("fuente") in INCREMENTALES or o.get("fuente") not in fuentes_ok)]

    ofertas, descartes = [], {}
    for o in deduplicar(crudas):
        m = motivo_descarte(o, perfil)
        if m:
            clave = m.split(" (")[0]
            descartes[clave] = descartes.get(clave, 0) + 1
            continue
        ofertas.append(puntuar(o, perfil, hoy))

    limite = (hoy - timedelta(days=perfil["dias_mostrar"])).isoformat()
    ofertas += [o for o in conservar if o.get("visto", "") >= limite]
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

    resumen = {
        "actualizado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "fecha": hoy.isoformat(),
        "revisadas": len(crudas),
        "mostradas": len(ofertas),
        "nuevas": sum(o["nueva"] for o in ofertas),
        "descartes": dict(sorted(descartes.items(), key=lambda x: -x[1])),
        "fuentes": [f for f, n in estado.items() if n],
        "por_fuente": estado,
    }
    HISTORIAL.parent.mkdir(exist_ok=True)
    HISTORIAL.write_text(json.dumps(historial, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "data" / "muestras.json").write_text(json.dumps(muestras, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    DOCS.mkdir(exist_ok=True)
    (DOCS / "ofertas.json").write_text(json.dumps({"resumen": resumen, "ofertas": ofertas}, ensure_ascii=False, indent=1), encoding="utf-8")
    (DOCS / "index.html").write_text(generar(ofertas, resumen), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
