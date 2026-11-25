"""Piezas comunes de las fuentes: HTTP con reintentos y forma estándar de una oferta."""
import json
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (compatible; buscador-empleo/1.0; +https://github.com/SergonM/buscador-empleo)"


def get_json(url, intentos=3, etiqueta="http"):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"  [{etiqueta}] error {e} en {url} (intento {i + 1})", file=sys.stderr)
            time.sleep(3 * (i + 1))
    return None


def oferta(**k):
    """Oferta con todos los campos que esperan filtros, ranking y página."""
    base = {
        "id": "", "fuente": "", "titulo": "", "empresa": "", "url": "", "modalidad": "No indica",
        "remoto": False, "remote_modality": "", "paises": [], "ubicacion": "", "fecha": "",
        "seniority_id": None, "seniority": "", "categoria": "", "idioma": "", "descripcion": "", "salario": "",
    }
    base.update({key: v for key, v in k.items() if v is not None})
    base["titulo"] = str(base["titulo"]).strip()
    base["empresa"] = str(base["empresa"] or "").strip()
    return base
