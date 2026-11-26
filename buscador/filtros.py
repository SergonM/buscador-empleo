"""Filtros: descarta senior, experiencia alta, ubicación fuera de Colombia/LATAM y ofertas sin relación."""
import re

from .texto import anios_experiencia, contiene, encontradas, normalizar


def motivo_descarte(o, perfil):
    """Devuelve un texto con el motivo si la oferta se descarta, o None si pasa."""
    titulo = normalizar(o["titulo"])
    desc = normalizar(o.get("descripcion", ""))
    es_junior_titulo = bool(encontradas(titulo, perfil["junior_titulo"]))

    # 1. Senior por título
    malas = encontradas(titulo, perfil["excluir_titulo"])
    if malas and not es_junior_titulo:
        return f"título senior ({malas[0]})"

    otras = encontradas(titulo, perfil.get("excluir_otros_titulo", []))
    if otras:
        return f"rol no buscado ({otras[0]})"

    # 2. Senior por nivel declarado en la fuente
    sid = o.get("seniority_id")
    if sid is not None and sid >= 4:
        return f"nivel {o.get('seniority')}"
    if sid == 3 and not es_junior_titulo and not perfil.get("incluir_semi_senior"):
        return "nivel Semi Senior"

    # 3. Años de experiencia pedidos
    anios = anios_experiencia(desc)
    if anios is not None and anios > perfil["max_anios_experiencia"]:
        return f"pide {anios} años de experiencia"

    # 4. Ubicación
    if not ubicacion_ok(o, perfil):
        return f"ubicación ({o.get('modalidad')}: {o.get('ubicacion') or 'sin país'})"

    # 5. Relación con las áreas buscadas
    if not areas_en_titulo(titulo, perfil):
        return "fuera de las áreas buscadas"
    return None


def ubicacion_ok(o, perfil):
    paises = normalizar(" ".join(o.get("paises") or []) + " " + (o.get("ubicacion") or ""))
    en_colombia = contiene(paises, "colombia")
    if o.get("remote_modality") == "fully_remote":
        # Remoto: sirve si no restringe país, o si incluye Colombia/LATAM/global.
        # "Remote - US" o "Remote, Brazil" no sirven: piden vivir en otro país.
        especificas = [p for p in perfil["paises_ok"] if p not in ("remote", "remoto")]
        if any(contiene(paises, p) for p in especificas):
            return True
        if encontradas(paises, perfil.get("zonas_excluidas", [])):
            return False
        return not paises or any(contiene(paises, p) for p in perfil["paises_ok"])
    if o.get("remoto"):
        # Remoto local: solo si el país es Colombia.
        return en_colombia
    # Híbrido o presencial: Colombia y, si menciona ciudad, que sea Bogotá.
    if not en_colombia:
        return False
    otras = perfil.get("ciudades_otras", [])
    ubic = normalizar(o.get("ubicacion", "") + " " + o.get("titulo", ""))
    if contiene(ubic, perfil["ciudad"]):
        return True
    if encontradas(ubic, otras):
        return False
    texto = normalizar(o.get("descripcion", ""))
    return contiene(texto, perfil["ciudad"]) or not encontradas(texto, otras)


GENERICAS = {"analista", "analyst", "consultor", "consultant"}


def areas_en_titulo(titulo_norm, perfil):
    """Áreas cuyo vocabulario aparece en el cargo. 'Analista' a secas solo cuenta como
    Negocio / Producto si el cargo no es claramente de otra área."""
    especificas, genericas = [], []
    for a, cfg in perfil["areas"].items():
        hits = encontradas(titulo_norm, cfg["titulo"])
        if any(h not in GENERICAS for h in hits):
            especificas.append(a)
        elif hits:
            genericas.append(a)
    return especificas or genericas


def deduplicar(ofertas):
    """Quita duplicados por id y por (título, empresa) normalizados."""
    vistos, salida = set(), []
    for o in ofertas:
        clave = (_clave(o["titulo"]), _clave(o["empresa"], empresa=True))
        if o["id"] in vistos or clave in vistos:
            continue
        vistos.update([o["id"], clave])
        salida.append(o)
    return salida


_SUFIJOS = re.compile(r"\b(s ?a ?s|s ?a|ltda|inc|llc|ltd|corp|colombia|group|grupo)\b")


def _clave(texto, empresa=False):
    t = re.sub(r"[^a-z0-9 ]", " ", normalizar(texto))
    if empresa:
        t = _SUFIJOS.sub(" ", t)
    return " ".join(t.split())
