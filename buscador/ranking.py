"""Ranking: puntaje de 0 a 100 según encaje con el perfil y una línea de por qué encaja."""
from datetime import date

from .filtros import areas_en_titulo
from .texto import encontradas, normalizar


def puntuar(o, perfil, hoy=None):
    hoy = hoy or date.today()
    titulo = normalizar(o["titulo"])
    desc = normalizar(o.get("descripcion", ""))
    puntos, razones = 0, []

    # Área (lo más importante): título pesa más que descripción.
    areas = areas_en_titulo(titulo, perfil)
    if areas:
        puntos += 35 + 5 * (len(areas) - 1)
    habilidades = []
    for area in areas or perfil["areas"]:
        habilidades += encontradas(desc, perfil["areas"][area]["texto"])
    habilidades = list(dict.fromkeys(habilidades))
    puntos += min(len(habilidades), 5) * 3

    # Nivel junior
    if encontradas(titulo, perfil["junior_titulo"]):
        puntos += 15
        razones.append("junior/trainee")
    elif o.get("seniority_id") in (1, 2):
        puntos += 12
        razones.append(o["seniority"].lower())
    elif o.get("seniority_id") == 3:
        puntos -= 8
        razones.append("semi senior sin pedir más de 2 años (vale intentar)")

    # Modalidad y ubicación
    paises = normalizar(" ".join(o.get("paises") or []))
    if o.get("remoto"):
        puntos += 10
        razones.append("remoto" + (" desde Colombia" if "colombia" in paises else ""))
    elif "colombia" in paises:
        puntos += 8
        donde = "Bogotá" if "bogota" in normalizar(o.get("ubicacion", "")) else "Colombia"
        razones.append(o["modalidad"].lower() + " en " + donde)

    # Bonus por experiencia previa y palabras clave
    extras = []
    for palabra, frase in perfil["bonus"]["palabras"].items():
        en_titulo = encontradas(titulo, [palabra])
        # Compliance cuenta solo si está en el cargo (en la descripción aparece en casi todas).
        if en_titulo or (palabra not in ("compliance", "cumplimiento") and encontradas(desc, [palabra])):
            if frase not in extras:
                extras.append(frase)
    puntos += min(len(extras), 3) * 4

    # Frescura: hasta 6 puntos si es de los últimos días
    try:
        dias = (hoy - date.fromisoformat(o["fecha"])).days
        puntos += max(0, 6 - dias // 2)
    except (ValueError, TypeError, KeyError):
        pass

    if areas:
        razones.insert(0, " + ".join(areas))
    if habilidades:
        razones.append("pide " + ", ".join(habilidades[:3]))
    razones += [e for e in extras if not e.startswith("pide ")][:1]

    o["puntaje"] = min(100, puntos)
    o["areas"] = areas
    linea = " · ".join(razones)
    o["por_que"] = (linea[:1].upper() + linea[1:]) if linea else "Coincide con tu búsqueda"
    return o
