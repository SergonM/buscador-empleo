import json, sys
sys.path.insert(0, ".")
from buscador.fuentes import computrabajo as ct
from buscador.filtros import motivo_descarte
from buscador.ranking import puntuar
perfil = json.load(open("perfil.json"))
cfg = dict(perfil["computrabajo"]); cfg["busquedas"] = cfg["busquedas"][:6]; cfg["max_detalles"] = 15
ofs, muestra = ct.buscar(cfg, perfil)
pag = ct._get("https://co.computrabajo.com/trabajo-de-analista-de-datos-en-bogota-dc")
print("LISTADO", ct.listado(pag)[:5])
for o in ofs:
    m = motivo_descarte(o, perfil) if motivo_descarte.__code__.co_argcount == 2 else None
    print("-", o["titulo"], "|", o["empresa"], "|", o["ubicacion"], "|", o["modalidad"], "|", o["fecha"], "|", o["salario"], "| descarte:", m, "|", o["descripcion"][:120])
