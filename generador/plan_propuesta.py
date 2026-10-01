"""Propuesta de ajuste (01-oct-2026): se suspenden la clase del jueves 01-oct y toda la
semana del 05-oct en ambos paralelos; Cátedra 1 pasa al jueves 15-oct.

Cada semana tiene 6 celdas: C1 Ítalo (mar, jue, vie) + C2 Benjamín (lun, mié, jue).
Las semanas que no aparecen en CAMBIOS se copian tal cual desde plan_actual.json.
"""
import copy, json, pathlib

AQUI = pathlib.Path(__file__).parent

def C(date, code, text, pc=None, note=None):
    d = dict(date=date, kind="clase", code=code, text=text)
    if pc: d["pc"] = list(pc)
    if note: d["note"] = note
    return d
def A(date, code, text): return dict(date=date, kind="ayud", code=code, text=text)
def K(date, name, sub): return dict(date=date, kind="cat", name=name, sub=sub)
def L(date, text, note=None):
    d = dict(date=date, kind="libre", text=text)
    if note: d["note"] = note
    return d
def S(date, text, note=None):
    d = dict(date=date, kind="susp", text=text)
    if note: d["note"] = note
    return d
def X(date, text): return dict(date=date, kind="exam", text=text)
E = dict(date=None, kind="empty")

CAT1 = ("Cátedra 1", "Áreas 1–3 · sin archivos")
CAT2 = ("Cátedra 2", "Área 5 + archivos")
CAT3 = ("Cátedra 3", "Área 4 · subprogramas")

CAMBIOS = {
 6: [C("29 sep","C10","Integración y repaso"),
     S("01 oct","Suspendida",note="Cátedra 1 → jue 15-oct"),
     A("02 oct","A4","integradores de elementos básicos"),
     A("28 sep","A4","validación y problemas matemáticos"),
     C("30 sep","C10","Integración y repaso"),
     S("01 oct","Suspendida",note="Cátedra 1 → jue 15-oct")],
 7: dict(kind="susp", text="Semana sin clases ni ayudantías en ambos paralelos (suspensión)"),
 8: [C("13 oct","C11","Repaso previo a Cátedra 1"),
     K("15 oct",*CAT1),
     A("16 oct","A5","integradores de mayor complejidad (cierre de unidad)"),
     L("12 oct","Feriado — Encuentro de Dos Mundos",note="lunes: sin ayudantía"),
     C("14 oct","C11","Repaso previo a Cátedra 1"),
     K("15 oct",*CAT1)],
 10: [C("27 oct","C12","📄 Lectura / escritura de archivos"),
      C("29 oct","C13","Vectores: creación, recorrido y operaciones"),
      A("30 oct","A6","archivos y vectores"),
      A("26 oct","A5","integradores de elementos básicos"),
      C("28 oct","C12","📄 Lectura / escritura de archivos"),
      C("29 oct","C13","Vectores: creación, recorrido y operaciones")],
 11: [C("03 nov","C14","Búsqueda y ordenamiento"),
      C("05 nov","C15","Inserción y eliminación",pc=("PC3","2","vectores, búsqueda y orden · trazado")),
      A("06 nov","A7","búsqueda, ordenamiento e inserción/eliminación"),
      A("02 nov","A6","archivos y vectores"),
      C("04 nov","C14","Búsqueda y ordenamiento"),
      C("05 nov","C15","Inserción y eliminación",pc=("PC3","2","vectores, búsqueda y orden · trazado"))],
 12: [C("10 nov","C16","Vectores / listas paralelas"),
      C("12 nov","C17","Matrices (2D)"),
      A("13 nov","A8","vectores paralelas y matrices"),
      A("09 nov","A7","búsqueda, ordenamiento e inserción/eliminación"),
      C("11 nov","C16","Vectores / listas paralelas"),
      C("12 nov","C17","Matrices (2D)")],
 13: [C("17 nov","C18","Integración y repaso de arreglos"),
      K("19 nov",*CAT2),
      A("20 nov","A9","integradores de arreglos y archivos"),
      A("16 nov","A8","vectores paralelas y matrices"),
      C("18 nov","C18","Integración y repaso de arreglos"),
      K("19 nov",*CAT2)],
 14: [C("24 nov","C19","Funciones: def, retorno y parámetros"),
      C("26 nov","C20","Traspaso · alcance · descomponer",pc=("PC4","3","funciones")),
      A("27 nov","A10","funciones, parámetros y alcance"),
      A("23 nov","A9","integradores de arreglos y archivos"),
      C("25 nov","C19","Funciones: def, retorno y parámetros"),
      C("26 nov","C20","Traspaso · alcance · descomponer",pc=("PC4","3","funciones"))],
 15: [C("01 dic","C21","Funciones con arreglos · diseño modular"),
      C("03 dic","C22","Descomposición modular · buenas prácticas · recursión",pc=("PC5","3","traspaso, alcance y arreglos")),
      A("04 dic","A11","funciones sobre arreglos, modular y recursión"),
      A("30 nov","A10","funciones, parámetros y alcance"),
      C("02 dic","C21","Funciones con arreglos · diseño modular"),
      C("03 dic","C22","Descomposición modular · buenas prácticas · recursión",pc=("PC5","3","traspaso, alcance y arreglos"))],
 16: [L("08 dic","Feriado — Inmaculada",note="mié 09: exámenes pendientes"),
      C("10 dic","C23","Proyecto integrador",pc=("PC6","3","modular y recursión")),
      A("11 dic","A12","integradores de subprogramas · última"),
      A("07 dic","A11","funciones sobre arreglos, modular y recursión"),
      X("09 dic","Exámenes pendientes"),
      C("10 dic","C23","Proyecto integrador",pc=("PC6","3","modular y recursión"))],
 17: [C("15 dic","C24","Repaso general y cierre"),
      K("17 dic",*CAT3),
      E,
      A("14 dic","A12","integradores de subprogramas · última"),
      C("16 dic","C24","Repaso general y cierre"),
      K("17 dic",*CAT3)],
}

def construir():
    actual = json.loads((AQUI / "plan_actual.json").read_text())
    prop = copy.deepcopy(actual)
    for w in prop:
        cambio = CAMBIOS.get(w["sem"])
        if cambio is None:
            continue
        if isinstance(cambio, dict):
            w.pop("cells", None); w["full"] = cambio
        else:
            w.pop("full", None); w["cells"] = copy.deepcopy(cambio)
    return actual, prop
