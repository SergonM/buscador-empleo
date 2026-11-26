"""Ranking: puntaje de 0 a 100 según encaje con el perfil y una línea de por qué encaja."""
import re
from datetime import date

from .filtros import areas_en_titulo
from .texto import anios_experiencia, contiene, encontradas, normalizar


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
        mod = o["modalidad"].lower()
        razones.append(("en " if mod in ("no indica", "") else mod + " en ") + donde)

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

    # Señales de nivel en la descripción
    anios = anios_experiencia(desc)
    if any(contiene(desc, f) for f in perfil.get("frases_junior", [])):
        puntos += 6
        razones.append("acepta poca o ninguna experiencia")
    elif anios == 2:
        puntos -= 3
    if encontradas(titulo, perfil.get("penalizar_titulo", [])):
        puntos -= 8

    ayudas(o, perfil, titulo, desc, anios)
    if o["ingles"]:
        razones.append("pide inglés (lo tienes)")

    o["puntaje"] = max(0, min(100, puntos))
    o["areas"] = areas
    linea = " · ".join(razones)
    o["por_que"] = (linea[:1].upper() + linea[1:]) if linea else "Coincide con tu búsqueda"
    return o


_EN = {"the", "and", "with", "you", "will", "our", "for", "experience", "team", "skills", "are", "your"}
_ES = {"de", "la", "el", "con", "para", "los", "las", "experiencia", "equipo", "conocimientos", "una", "del"}


def idioma(texto_norm):
    palabras = texto_norm.split()[:400]
    en = sum(p in _EN for p in palabras)
    es = sum(p in _ES for p in palabras)
    return "en" if en > es else "es"


def ayudas(o, perfil, titulo=None, desc=None, anios=None):
    """Datos para postular: palabras clave de la oferta para la hoja de vida, idioma, inglés pedido,
    años pedidos y un puntaje de calidad de la oferta (qué tan completa y confiable es)."""
    titulo = titulo if titulo is not None else normalizar(o["titulo"])
    desc = desc if desc is not None else normalizar(o.get("descripcion", ""))
    texto = titulo + " " + desc
    vocab = perfil.get("vocabulario_cv", [])
    mias = {normalizar(h) for h in perfil.get("mis_habilidades", [])}
    if not desc and "claves" in o:  # oferta conservada: ya tiene sus palabras clave
        return o
    claves = encontradas(texto, vocab)
    o["claves"] = [c for c in claves if normalizar(c) in mias][:8]
    o["reforzar"] = [c for c in claves if normalizar(c) not in mias][:6]
    if desc:
        o["idioma"] = idioma(desc)
        o["ingles"] = o["idioma"] == "en" or bool(re.search(r"\b(ingles|english)\b", desc))
        o["anios"] = anios
    else:  # oferta conservada de otro día: se mantiene lo calculado antes
        o.setdefault("ingles", False)
        o.setdefault("anios", None)
    if desc or "calidad" not in o:
        cal = 40
        cal += 15 if o.get("salario") else 0
        cal += 15 if len(desc) > 1500 else 8 if len(desc) > 400 else 0
        cal += 10 if o.get("fuente") in perfil.get("fuentes_directas", []) else 0
        cal += 10 if normalizar(o.get("empresa", "")) in {normalizar(e) for e in perfil.get("empresas_destacadas", [])} else 0
        cal += 10 if o.get("seniority") or anios is not None else 0
        cal -= 25 if not o.get("empresa") or re.search(r"confidencial|importante empresa|empresa del sector", normalizar(o.get("empresa", ""))) else 0
        o["calidad"] = max(0, min(100, cal))
    return o
