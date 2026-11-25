"""Ejecuta la búsqueda diaria: python -m buscador"""
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .filtros import deduplicar, motivo_descarte
from .fuentes import getonboard
from .pagina import generar
from .ranking import puntuar

RAIZ = Path(__file__).resolve().parent.parent
HISTORIAL = RAIZ / "data" / "historial.json"
DOCS = RAIZ / "docs"


def _leer(p, defecto):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def main():
    perfil = _leer(RAIZ / "perfil.json", None)
    hoy = datetime.now(timezone(timedelta(hours=-5))).date()  # hora Bogotá
    historial = _leer(HISTORIAL, {})  # id -> fecha en que la vimos por primera vez

    print("Buscando en GetOnBoard…")
    crudas, muestra = getonboard.buscar(perfil["busquedas"])
    if not crudas:
        print("No llegó ninguna oferta: la fuente falló. No se cambia la página.", file=sys.stderr)
        return 1

    ofertas, descartes = [], {}
    for o in deduplicar(crudas):
        m = motivo_descarte(o, perfil)
        if m:
            clave = m.split(" (")[0]
            descartes[clave] = descartes.get(clave, 0) + 1
            continue
        ofertas.append(puntuar(o, perfil, hoy))

    limite = (hoy - timedelta(days=perfil["dias_mostrar"])).isoformat()
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
        "fuentes": ["GetOnBoard"],
    }
    HISTORIAL.parent.mkdir(exist_ok=True)
    HISTORIAL.write_text(json.dumps(historial, indent=0, sort_keys=True), encoding="utf-8")
    (RAIZ / "data" / "muestra_getonboard.json").write_text(json.dumps(muestra, indent=1, ensure_ascii=False)[:60000], encoding="utf-8")
    DOCS.mkdir(exist_ok=True)
    (DOCS / "ofertas.json").write_text(json.dumps({"resumen": resumen, "ofertas": ofertas}, ensure_ascii=False, indent=1), encoding="utf-8")
    (DOCS / "index.html").write_text(generar(ofertas, resumen), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
