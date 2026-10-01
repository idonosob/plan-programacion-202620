"""Genera ../index.html con dos vistas (panel izquierdo): planificación actual y propuesta.

Uso:  python3 generador/generar.py
Datos: plan_actual.json (vigente) y plan_propuesta.py (ajuste por suspensión 01–09 oct).
Las celdas de la propuesta se comparan con la vigente en la misma semana y posición:
  · "cambio"  → cambia el contenido, la fecha, el tipo o la prueba corta
  · "renum."  → mismo contenido, solo cambia el número de clase/ayudantía
"""
import html, pathlib
from plan_propuesta import construir

AQUI = pathlib.Path(__file__).parent
CSS_BASE = (AQUI / "estilos.css").read_text()

CSS_EXTRA = """
:root{ --chg:#C2255C; --chg-soft:rgba(194,37,92,.55); --chg-bg:#FCE4EC;
  --side-on-bg:#3B3F46; --side-on-fg:#ffffff; }
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --chg:#F783AC; --chg-soft:rgba(247,131,172,.6); --chg-bg:rgba(247,131,172,.14);
  --side-on-bg:#E8EAEF; --side-on-fg:#111319; }}
:root[data-theme="dark"]{ --chg:#F783AC; --chg-soft:rgba(247,131,172,.6); --chg-bg:rgba(247,131,172,.14);
  --side-on-bg:#E8EAEF; --side-on-fg:#111319; }

.layout{display:grid;grid-template-columns:236px minmax(0,1fr);gap:28px;max-width:1640px;margin:0 auto;padding:28px 24px 64px;}
.side{position:sticky;top:18px;align-self:start;display:flex;flex-direction:column;gap:14px;}
.sidebox{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:var(--shadow);}
.sidebox h2{font-family:"IBM Plex Mono",monospace;font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin:0 0 10px;font-weight:600;}
.nav{display:flex;flex-direction:column;gap:6px;}
.navbtn{display:block;text-decoration:none;color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:9px 11px;background:var(--surface-2);}
.navbtn .t{display:flex;align-items:center;gap:7px;font-weight:600;font-size:.9rem;}
.navbtn .s{display:block;font-size:.74rem;color:var(--muted);margin-top:2px;}
.navbtn:hover{border-color:var(--accent);}
.navbtn:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
.navbtn[aria-current="page"]{background:var(--side-on-bg);color:var(--side-on-fg);border-color:var(--side-on-bg);}
.navbtn[aria-current="page"] .s{color:var(--side-on-fg);opacity:.75;}
.dotc{width:9px;height:9px;border-radius:50%;background:var(--chg);flex:0 0 auto;}
.minilist{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px;font-size:.8rem;color:var(--muted);}
.minilist b{color:var(--ink);font-weight:600;}
.sidebox .btn{width:100%;justify-content:center;}
main{min-width:0;}
.view[hidden]{display:none;}
.view header{margin-bottom:18px;}

.c2.chg{outline:2px solid var(--chg);outline-offset:1px;border-radius:9px;}
.c2.ren{outline:1.5px dashed var(--chg-soft);outline-offset:1px;border-radius:9px;}
.tag{font-family:"IBM Plex Mono",monospace;font-size:.56rem;letter-spacing:.06em;text-transform:uppercase;
  color:var(--chg);font-weight:600;margin-left:4px;}
.chip2.susp{color:var(--chg);border-color:var(--chg-soft);font-weight:600;font-size:.74rem;display:flex;align-items:center;
  background:repeating-linear-gradient(135deg,var(--chg-bg) 0 7px,transparent 7px 14px);}
.wk2.chg .n{color:var(--chg);}
.sw.chg{background:transparent;border:2px solid var(--chg);}
.sw.ren{background:transparent;border:1.5px dashed var(--chg-soft);}
.sw.susp{border-color:var(--chg-soft);background:repeating-linear-gradient(135deg,var(--chg-bg) 0 3px,transparent 3px 6px);}

.cambios{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow);margin:6px 0 18px;
  display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:22px;}
.cambios h3{font-family:"Fraunces",serif;font-weight:600;font-size:1.05rem;margin:0 0 8px;}
.cambios ul{margin:0;padding-left:18px;display:flex;flex-direction:column;gap:6px;font-size:.88rem;}
.cambios li b{font-weight:600;}
.kd{width:100%;border-collapse:collapse;font-size:.84rem;font-variant-numeric:tabular-nums;}
.kd th{font-family:"IBM Plex Mono",monospace;font-size:.64rem;letter-spacing:.08em;text-transform:uppercase;color:var(--faint);text-align:left;font-weight:600;padding:0 6px 6px;border-bottom:1px solid var(--line);}
.kd td{padding:6px;border-bottom:1px solid var(--line-2);}
.kd td.nw{color:var(--chg);font-weight:600;}
.kd td.eq{color:var(--muted);}

@media (max-width:1000px){
  .layout{grid-template-columns:minmax(0,1fr);padding:18px 14px 48px;gap:16px;}
  .side{position:static;}
  .nav{flex-direction:row;flex-wrap:wrap;}
  .navbtn{flex:1 1 200px;}
  .side .sidebox:not(:first-child){display:none;}
  .cambios{grid-template-columns:1fr;}
}
@media print{
  .side{display:none;} .layout{display:block;padding:0;max-width:none;}
  .c2.chg,.c2.ren{outline-offset:0;}
}
"""

def esc(t): return html.escape(t or "", quote=False)

# ---------- comparación ----------
def firma(c, completa):
    if c is None: return None
    keys = ("kind","date","text","name","sub","note")
    f = tuple(c.get(k) for k in keys)
    pc = c.get("pc")
    f += ((tuple(pc) if completa else tuple(pc[1:])) if pc else None,)
    if completa: f += (c.get("code"),)
    return f

def estado(c, ref):
    if ref is None: return "chg"
    if firma(c, True) == firma(ref, True): return ""
    if firma(c, False) == firma(ref, False): return "ren"
    return "chg"

# ---------- render ----------
def celda(c, sep, est=""):
    cls = "c2" + (" sep" if sep else "") + (f" {est}" if est else "")
    if c["kind"] == "empty":
        return f'<div class="{cls}"></div>'
    tag = {"chg": '<span class="tag">cambio</span>', "ren": '<span class="tag">renum.</span>'}.get(est, "")
    d = f'<div class="cdate">{esc(c.get("date"))}{tag}</div>'
    k = c["kind"]
    if k in ("clase", "ayud"):
        body = f'<div class="chip2 {k}"><span class="code">{esc(c["code"])}</span>{esc(c["text"])}</div>'
    elif k == "cat":
        body = f'<div class="chip2 cat"><span class="cn">{esc(c["name"])}</span><span class="cs">{esc(c["sub"])}</span></div>'
    else:  # libre, exam, susp
        body = f'<div class="chip2 {k}">{esc(c["text"])}</div>'
    pc = c.get("pc")
    b = f'<span class="badge2"><b>{pc[0]}</b> · Cát {pc[1]} · {esc(pc[2])}</span>' if pc else ""
    n = f'<span class="note2">{esc(c["note"])}</span>' if c.get("note") else ""
    return f'<div class="{cls}">{d}{body}{b}{n}</div>'

def grilla(semanas, ref=None):
    refmap = {w["sem"]: w for w in ref} if ref else {}
    head = ('<div class="ghead spacer"></div>'
            '<div class="ghead gspan g-ital"><span class="who">Paralelo C1</span>Ítalo Donoso</div>'
            '<div class="ghead gspan g-otro"><span class="who">Paralelo C2</span>Benjamín Miranda</div>'
            '<div class="dhead">Sem.</div>'
            '<div class="dhead">Martes</div><div class="dhead">Jueves</div><div class="dhead">Viernes · Ay.</div>'
            '<div class="dhead sep">Lunes · Ay.</div><div class="dhead">Miércoles</div><div class="dhead">Jueves</div>')
    filas = []
    for w in semanas:
        r = refmap.get(w["sem"])
        if "full" in w:
            f = w["full"]
            est = ""
            if ref is not None and not (r and "full" in r and r["full"] == f):
                est = "chg"
            tagdiv = '<div class="cdate"><span class="tag">cambio</span></div>' if est else ""
            clsf = "c2 fullrow" + (" " + est if est else "")
            meta = f'<div class="wk2{" chg" if est else ""}"><span class="n">Sem {w["sem"]}</span><span class="d">{esc(w["label"])}</span></div>'
            filas.append(meta + f'<div class="{clsf}">{tagdiv}'
                         f'<div class="chip2 {f["kind"]}">{esc(f["text"])}</div></div>')
            continue
        ests = []
        for i, c in enumerate(w["cells"]):
            refc = None
            if r and "cells" in r: refc = r["cells"][i]
            ests.append(estado(c, refc) if ref is not None else "")
        semchg = any(e == "chg" for e in ests)
        meta = f'<div class="wk2{" chg" if semchg else ""}"><span class="n">Sem {w["sem"]}</span><span class="d">{esc(w["label"])}</span></div>'
        filas.append(meta + "".join(celda(c, i == 3, ests[i]) for i, c in enumerate(w["cells"])))
    return f'<div class="cmpwrap"><div class="cmp">{head}{"".join(filas)}</div></div>'

def contar(semanas):
    clases, ayud_c1, ayud_c2, pcs = set(), 0, 0, set()
    for w in semanas:
        for i, c in enumerate(w.get("cells", [])):
            if c["kind"] == "clase": clases.add(c["code"])
            if c["kind"] == "ayud":
                if i < 3: ayud_c1 += 1
                else: ayud_c2 += 1
            if c.get("pc"): pcs.add(c["pc"][0])
    return len(clases), ayud_c1, ayud_c2, len(pcs)

def totales(semanas):
    n, a1, a2, p = contar(semanas)
    ay = str(a1) if a1 == a2 else f"{a1} / {a2}"
    return ('<div class="totals">'
            f'<div class="stat"><div class="n">{n}</div><div class="l">clases · por paralelo</div></div>'
            '<div class="stat"><div class="n">3</div><div class="l">cátedras · jueves</div></div>'
            f'<div class="stat"><div class="n">{p}</div><div class="l">pruebas cortas · jueves</div></div>'
            f'<div class="stat"><div class="n">{ay}</div><div class="l">ayudantías · por paralelo</div></div></div>')

LEYENDA = ('<div class="legend" role="list">'
  '<span class="lg" role="listitem"><span class="sw clase"></span>Clase</span>'
  '<span class="lg" role="listitem"><span class="sw cat"></span>Cátedra</span>'
  '<span class="lg" role="listitem"><span class="sw pc"></span>Prueba corta (jueves)</span>'
  '<span class="lg" role="listitem"><span class="sw ayud"></span>Ayudantía</span>'
  '<span class="lg" role="listitem"><span class="sw libre"></span>Sin clases</span>{extra}</div>')
LEYENDA_CAMBIOS = ('<span class="lg" role="listitem"><span class="sw chg"></span>Cambia respecto de la vigente</span>'
  '<span class="lg" role="listitem"><span class="sw ren"></span>Solo cambia el número</span>'
  '<span class="lg" role="listitem"><span class="sw susp"></span>Suspendida</span>')

PIE_ACTUAL = ("Ambos paralelos cubren el mismo contenido y rinden las evaluaciones el mismo jueves. En el paralelo del otro profesor la ayudantía es el <b>lunes</b> (inicio de semana), por lo que repasa el contenido de la semana anterior; por eso su numeración de ayudantías va corrida respecto a la del viernes. Semana 1: ambos usan la ayudantía como clase. El lunes 12-oct es feriado (Encuentro de Dos Mundos), sin ayudantía. El miércoles 09-dic, en el horario del otro profesor, se destina a la toma de exámenes pendientes (feriado del 08-dic).")

PIE_PROP = ("Se mantienen las reglas acordadas: evaluaciones solo los jueves, a lo más una prueba corta por semana, ninguna en semana de cátedra, la de arreglos después del receso de autocuidado y archivos evaluado en la Cátedra 2. "
  "Supuesto: la ayudantía del viernes 02-oct (C1) se realiza, como preparación para la Cátedra 1. "
  "Si en cambio se prefiere mantener la Cátedra 2 el 12-nov, arreglos queda con solo 6 clases antes de ella.")

CAMBIOS_HTML = """
<section class="cambios" aria-label="Resumen de cambios">
  <div>
    <h3>Qué cambia</h3>
    <ul>
      <li><b>Suspendidas</b> la clase del jue 01-oct y toda la semana del 05-oct (clases y ayudantías) en ambos paralelos.</li>
      <li><b>Cátedra 1 → jue 15-oct.</b> En la clase previa (mar 13 / mié 14) se adelanta <b>lectura/escritura de archivos</b>, que se evalúa en la Cátedra 2; no hay clase de repaso.</li>
      <li><b>Cátedra 2 → jue 19-nov</b> para repartir la pérdida entre las dos unidades: arreglos queda en 8 clases (con archivos) y subprogramas en 6.</li>
      <li><b>Fusiones:</b> vectores creación + recorrido; funciones que reciben + retornan arreglos; descomposición modular + buenas prácticas/recursión. Búsqueda y ordenamiento quedan en clases separadas.</li>
      <li><b>Pruebas cortas</b> PC3 a PC6 se corren a un jueves posterior; siguen siendo 6.</li>
    </ul>
  </div>
  <div>
    <h3>Fechas clave</h3>
    <table class="kd">
      <thead><tr><th></th><th>Vigente</th><th>Propuesta</th></tr></thead>
      <tbody>
        <tr><td>Cátedra 1</td><td>jue 01-oct</td><td class="nw">jue 15-oct</td></tr>
        <tr><td>Cátedra 2</td><td>jue 12-nov</td><td class="nw">jue 19-nov</td></tr>
        <tr><td>Cátedra 3</td><td>jue 17-dic</td><td class="eq">sin cambio</td></tr>
        <tr><td>PC3 · arreglos</td><td>jue 29-oct</td><td class="nw">jue 05-nov</td></tr>
        <tr><td>PC4 · funciones</td><td>jue 19-nov</td><td class="nw">jue 26-nov</td></tr>
        <tr><td>PC5</td><td>jue 26-nov</td><td class="nw">jue 03-dic</td></tr>
        <tr><td>PC6</td><td>jue 03-dic</td><td class="nw">jue 10-dic</td></tr>
        <tr><td>Clases</td><td>27</td><td class="nw">24</td></tr>
        <tr><td>Ayudantías</td><td>13</td><td class="nw">12</td></tr>
      </tbody>
    </table>
  </div>
</section>
"""

JS = """
<script>
(function(){
  var vistas=["actual","propuesta"];
  function mostrar(v){
    if(vistas.indexOf(v)<0) v="actual";
    document.querySelectorAll(".view").forEach(function(s){ s.hidden = (s.id!=="v-"+v); });
    document.querySelectorAll(".navbtn").forEach(function(b){
      if(b.dataset.v===v) b.setAttribute("aria-current","page"); else b.removeAttribute("aria-current");
    });
  }
  window.addEventListener("hashchange",function(){ mostrar(location.hash.slice(1)); });
  mostrar(location.hash.slice(1));
})();
</script>
"""

def pagina():
    actual, prop = construir()
    side = f"""
<aside class="side" aria-label="Vistas de la planificación">
  <div class="sidebox">
    <h2>Vistas</h2>
    <nav class="nav">
      <a class="navbtn" data-v="actual" href="#actual"><span class="t">Planificación actual</span><span class="s">Vigente · Cátedra 1 el 01-oct</span></a>
      <a class="navbtn" data-v="propuesta" href="#propuesta"><span class="t"><span class="dotc"></span>Propuesta de ajuste</span><span class="s">Suspensión 01–09 oct · Cátedra 1 el 15-oct</span></a>
    </nav>
  </div>
  <div class="sidebox">
    <h2>En la propuesta</h2>
    <ul class="minilist">
      <li><b>Borde rosa:</b> la celda cambia respecto de la vigente.</li>
      <li><b>Borde punteado:</b> mismo contenido, solo cambia el número.</li>
      <li><b>Rayado:</b> clase suspendida.</li>
    </ul>
  </div>
  <div class="sidebox"><button class="btn" onclick="window.print()">🖨️ Imprimir esta vista</button></div>
</aside>"""
    v_actual = f"""
<section class="view" id="v-actual" aria-label="Planificación actual">
  <header>
    <p class="eyebrow">Segundo semestre 2026 · v2.0 · planificación vigente</p>
    <h1>Programación 202620</h1>
    <p class="sub">Los dos paralelos, semana a semana. <b>C1 · Ítalo Donoso:</b> clases martes y jueves, ayudantía viernes. <b>C2 · Benjamín Miranda:</b> clases miércoles y jueves, ayudantía lunes. Mismo contenido y mismas cátedras; las <b>evaluaciones de los jueves coinciden</b> en ambos.</p>
  </header>
  {LEYENDA.format(extra="")}
  {grilla(actual)}
  {totales(actual)}
  <p class="foot">{PIE_ACTUAL}</p>
</section>"""
    v_prop = f"""
<section class="view" id="v-propuesta" aria-label="Propuesta de ajuste" hidden>
  <header>
    <p class="eyebrow">Propuesta de ajuste · 1 de octubre de 2026</p>
    <h1>Programación 202620</h1>
    <p class="sub">No se realizan la clase del <b>jueves 01-oct</b> ni ninguna de la <b>semana del 05-oct</b> en ambos paralelos, y la <b>Cátedra 1 pasa al jueves 15-oct</b>. Lo marcado en rosa cambia respecto de la planificación vigente.</p>
  </header>
  {CAMBIOS_HTML}
  {LEYENDA.format(extra=LEYENDA_CAMBIOS)}
  {grilla(prop, ref=actual)}
  {totales(prop)}
  <p class="foot">{PIE_PROP}</p>
</section>"""
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>Programación 202620</title>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">\n'
            f'<style>\n{CSS_BASE}\n{CSS_EXTRA}\n</style>\n</head>\n<body>\n'
            f'<div class="layout">{side}\n<main>{v_actual}\n{v_prop}\n</main></div>\n{JS}</body>\n</html>\n')

if __name__ == "__main__":
    out = AQUI.parent / "index.html"
    out.write_text(pagina())
    print("escrito", out)
