"""Utilidades de texto: normalizar y buscar palabras completas."""
import html
import re
import unicodedata

_TAG = re.compile(r"<[^>]+>")


def normalizar(s):
    """Minúsculas, sin tildes, sin HTML y con espacios simples."""
    if not s:
        return ""
    s = html.unescape(_TAG.sub(" ", str(s)))
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", s).strip()


_cache = {}


def _patron(palabra):
    p = _cache.get(palabra)
    if p is None:
        p = re.compile(r"(?<![a-z0-9])" + re.escape(normalizar(palabra)) + r"(?![a-z0-9])")
        _cache[palabra] = p
    return p


def contiene(texto_norm, palabra):
    return bool(_patron(palabra).search(texto_norm))


def encontradas(texto_norm, palabras):
    return [p for p in palabras if contiene(texto_norm, p)]


_ANIOS = re.compile(
    r"(?:al menos|minimo|mas de|\+)?\s*(\d{1,2})\s*(?:\+|-\s*\d+)?\s*(?:anos|years|yrs)\s*(?:o mas\s*)?(?:de|of)?\s*(?:experiencia|experience)"
)


def anios_experiencia(texto_norm):
    """Mínimo de años de experiencia pedidos (el menor número que aparezca), o None."""
    nums = [int(m.group(1)) for m in _ANIOS.finditer(texto_norm)]
    nums = [n for n in nums if 0 < n < 30]
    return min(nums) if nums else None
