"""Aviso diario por WhatsApp con CallMeBot (gratis). Opcional: solo corre si existen los secretos.

Secretos en GitHub: CALLMEBOT_PHONE (ej. 573001234567) y CALLMEBOT_APIKEY.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PAGINA = "https://sergonm.github.io/buscador-empleo/"


def mensaje(datos):
    r, ofertas = datos["resumen"], datos["ofertas"]
    nuevas = [o for o in ofertas if o.get("nueva")]
    if not nuevas:
        return f"Buscador de empleo: hoy no hay ofertas nuevas ({r['mostradas']} activas). {PAGINA}"
    lineas = [f"Buscador de empleo: {len(nuevas)} ofertas nuevas hoy. Las mejores:"]
    for o in nuevas[:3]:
        lineas.append(f"• {o['puntaje']} · {o['titulo']} – {o['empresa']} ({o['modalidad']})")
    lineas.append(PAGINA)
    return "\n".join(lineas)


def main():
    phone, key = os.environ.get("CALLMEBOT_PHONE"), os.environ.get("CALLMEBOT_APIKEY")
    if not phone or not key:
        print("Sin secretos de CallMeBot: no se envía WhatsApp.")
        return 0
    datos = json.loads((Path(__file__).resolve().parent.parent / "docs" / "ofertas.json").read_text(encoding="utf-8"))
    q = urllib.parse.urlencode({"phone": phone, "apikey": key, "text": mensaje(datos)})
    try:
        with urllib.request.urlopen(f"https://api.callmebot.com/whatsapp.php?{q}", timeout=30) as resp:
            print("WhatsApp enviado, código", resp.status)
    except Exception as e:  # noqa: BLE001
        print("No se pudo enviar el WhatsApp:", e, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
