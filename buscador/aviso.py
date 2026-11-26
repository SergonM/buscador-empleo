"""Aviso diario gratis. Opcional: cada canal solo se usa si existen sus secretos en GitHub.

- WhatsApp con CallMeBot: CALLMEBOT_PHONE (ej. 573001234567) y CALLMEBOT_APIKEY.
- Telegram con un bot propio: TELEGRAM_TOKEN y TELEGRAM_CHAT_ID (más estable que CallMeBot).
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
    for o in sorted(nuevas, key=lambda o: -o["puntaje"])[:5]:
        lineas.append(f"• {o['puntaje']} · {o['titulo']} – {o['empresa']} ({o['modalidad']})")
    lineas.append(PAGINA)
    return "\n".join(lineas)


def _enviar(nombre, url, datos=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=datos), timeout=30) as resp:
            print(f"{nombre} enviado, código", resp.status)
    except Exception as e:  # noqa: BLE001
        print(f"No se pudo enviar {nombre}:", e, file=sys.stderr)


def main():
    datos = json.loads((Path(__file__).resolve().parent.parent / "docs" / "ofertas.json").read_text(encoding="utf-8"))
    texto = mensaje(datos)
    enviados = 0
    phone, key = os.environ.get("CALLMEBOT_PHONE"), os.environ.get("CALLMEBOT_APIKEY")
    if phone and key:
        q = urllib.parse.urlencode({"phone": phone, "apikey": key, "text": texto})
        _enviar("WhatsApp", f"https://api.callmebot.com/whatsapp.php?{q}")
        enviados += 1
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        cuerpo = urllib.parse.urlencode({"chat_id": chat, "text": texto, "disable_web_page_preview": "true"}).encode()
        _enviar("Telegram", f"https://api.telegram.org/bot{token}/sendMessage", cuerpo)
        enviados += 1
    if not enviados:
        print("Sin secretos de WhatsApp ni Telegram: no se envía aviso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
