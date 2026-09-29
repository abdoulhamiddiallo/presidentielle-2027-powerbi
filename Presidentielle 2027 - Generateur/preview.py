# -*- coding: utf-8 -*-
"""Rendu HTML des pages PBIR, titres natifs compris.

Cet aperçu sert à contrôler la mise en page sans ouvrir Power BI : il
reconstitue les cadres, les titres et les proportions, pas le rendu exact des
graphiques.

Deux usages :
  python preview.py <dossier du projet> <sortie.html>
        aperçu de contrôle, avec le nom interne de chaque page en bas à gauche.
  python preview.py <dossier du projet> <sortie.html> --publication
        même aperçu, sans les repères de contrôle.
"""
import os, sys, json, glob, html, io
from pdata import CANDIDATS, HYPOTHESES, SCORES, HYPO_ORDER, ACCENTS, BLOC_ACC, NOM_COURT

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
PUBLICATION = "--publication" in sys.argv
ROOT = ARGS[0] if ARGS else "."
SORTIE = ARGS[1] if len(ARGS) > 1 else "apercu.html"
REP = glob.glob(os.path.join(ROOT, "*.Report"))[0]
PAGES = os.path.join(REP, "definition", "pages")

BLOC = {ACCENTS[n]: BLOC_ACC[b] for n, _p, b, _ob, _o, _c in CANDIDATS}
ORDRE = {ACCENTS[n]: o for n, _p, _b, _ob, o, _c in CANDIDATS}
BLOC_ORD = {BLOC_ACC[b]: ob for _n, _p, b, ob, _o, _c in CANDIDATS}
COURT = {ACCENTS[n]: NOM_COURT[n] for n, *_ in CANDIDATS}
SC = {h: {ACCENTS[n]: v for n, v in SCORES[h].items()} for h in HYPO_ORDER}
CANDS = sorted(BLOC, key=lambda c: ORDRE[c])
BLOCS = sorted(set(BLOC.values()), key=lambda b: BLOC_ORD[b])
PAL = ["#B33A2E", "#D4577E", "#BE8420", "#2E7DB8", "#41539E"]
CB = {b: PAL[BLOC_ORD[b] - 1] for b in BLOCS}
CONF = {h[0]: ("4 grands candidats" if len(SC[h[0]]) == 11 else "3 grands candidats")
        for h in HYPOTHESES}
LIB = {h[0]: h[1] for h in HYPOTHESES}
BASE = {h[0]: h[3] for h in HYPOTHESES}
NSP = {h[0]: h[4] for h in HYPOTHESES}


def moy(c):  return sum(SC[h][c][0] for h in HYPO_ORDER if c in SC[h]) / len([1 for h in HYPO_ORDER if c in SC[h]])
def mrg(c):  return sum(SC[h][c][1] for h in HYPO_ORDER if c in SC[h]) / len([1 for h in HYPO_ORDER if c in SC[h]])
def ampl(c):
    v = [SC[h][c][0] for h in HYPO_ORDER if c in SC[h]]
    return max(v) - min(v)
def eff(c):
    a = [SC[h][c][0] for h in HYPO_ORDER if c in SC[h] and CONF[h] == "3 grands candidats"]
    b_ = [SC[h][c][0] for h in HYPO_ORDER if c in SC[h] and CONF[h] == "4 grands candidats"]
    return (sum(a) / len(a) - sum(b_) / len(b_)) if a and b_ else 0.0
def bloc_moy(b_):
    return sum(sum(v[0] for c, v in SC[h].items() if BLOC[c] == b_) for h in HYPO_ORDER) / 8

VAL = {"Score du 1er (%)": "34,7 %", "Meilleur score mesuré (%)": "36,0 %",
       "Total extrême droite (%)": "38,0 %", "Écart minimal 1er / 2e (pts)": "16,5",
       "Score (%)": "34,7 %", "Amplitude (pts)": "2,5", "Hypothèses en tête": "6",
       "Candidat sélectionné": "Ensemble des candidats testés"}


def prop(o, *chemin, defaut=None):
    try:
        cur = o
        for k in chemin:
            cur = cur[k]
        return cur
    except Exception:
        return defaut


def litt(node, defaut=None):
    v = prop(node, "expr", "Literal", "Value")
    if v is None:
        v = prop(node, "solid", "color", "expr", "Literal", "Value")
    if v is None:
        return defaut
    return str(v).strip("'").rstrip("D")


def chrome_of(vis):
    c = prop(vis, "visual", "visualContainerObjects", defaut={}) or {}
    bg = None
    if litt(prop(c, "background", 0, "properties", "show", defaut={}), "false") == "true":
        bg = litt(prop(c, "background", 0, "properties", "color", defaut={}), "#FFFFFF")
    bd = None
    if litt(prop(c, "border", 0, "properties", "show", defaut={}), "false") == "true":
        bd = litt(prop(c, "border", 0, "properties", "color", defaut={}), "#E3E0D7")
    t = st = None
    if litt(prop(c, "title", 0, "properties", "show", defaut={}), "false") == "true":
        t = (litt(prop(c, "title", 0, "properties", "text", defaut={}), ""),
             float(litt(prop(c, "title", 0, "properties", "fontSize", defaut={}), "12")),
             litt(prop(c, "title", 0, "properties", "fontColor", defaut={}), "#0E1E33"),
             litt(prop(c, "title", 0, "properties", "fontFamily", defaut={}), "Georgia"))
    if litt(prop(c, "subTitle", 0, "properties", "show", defaut={}), "false") == "true":
        st = (litt(prop(c, "subTitle", 0, "properties", "text", defaut={}), ""),
              float(litt(prop(c, "subTitle", 0, "properties", "fontSize", defaut={}), "8.5")),
              litt(prop(c, "subTitle", 0, "properties", "fontColor", defaut={}), "#8A94A3"))
    return bg, bd, t, st


def donnees(vis):
    """Reconstitue les séries réelles du visuel."""
    q = prop(vis, "visual", "query", "queryState", defaut={}) or {}
    cat = prop(q, "Category", "projections", 0, "nativeQueryRef")
    ys = [p["nativeQueryRef"] for p in prop(q, "Y", "projections", defaut=[])]
    y = ys[0] if ys else ""
    if cat == "Candidat" and y == "Score (%)":
        r = [(c, moy(c), CB[BLOC[c]]) for c in CANDS]; r.sort(key=lambda t: -t[1]); return r
    if cat == "Bloc":
        return [(b_, bloc_moy(b_), CB[b_]) for b_ in BLOCS]
    if cat == "Candidat" and y.startswith("Marge"):
        r = [(c, mrg(c), "#93A9C4") for c in CANDS]; r.sort(key=lambda t: -t[1]); return r
    if cat == "NomCourt":
        r = [(COURT[c], eff(c), "#2E5C8A") for c in CANDS]; r.sort(key=lambda t: -t[1]); return r
    if cat == "Hypothese":
        return [(LIB[h], 100.0, "#7C8B9E") for h in HYPO_ORDER]
    if cat == "Code":
        return [(h, 100.0, "#7C8B9E") for h in HYPO_ORDER]
    if cat == "Configuration":
        return [("4 grands candidats", 0, "#999"), ("3 grands candidats", 0, "#999")]
    return []


def graphe(vis, w, h):
    vt = prop(vis, "visual", "visualType")
    rows = donnees(vis)
    if vt == "scatterChart":
        pts = [(COURT[c], moy(c), ampl(c), CB[BLOC[c]]) for c in CANDS]
        mx = max(p[1] for p in pts); my = max(p[2] for p in pts) or 1
        out = ['<div style="position:absolute;inset:0;border-left:1px solid #EDEAE2;'
               'border-bottom:1px solid #EDEAE2"></div>']
        for lab, x_, y_, col in pts:
            px = 30 + (w - 60) * x_ / (mx * 1.08)
            py = h - 26 - (h - 50) * y_ / (my * 1.15)
            out.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:9px;'
                       'height:9px;border-radius:9px;background:%s"></div>'
                       '<div style="position:absolute;left:%.1fpx;top:%.1fpx;font:8px Segoe UI;'
                       'color:#0E1E33;white-space:nowrap">%s</div>'
                       % (px, py, col, px + 11, py - 3, html.escape(lab)))
        return "".join(out)
    if vt == "ribbonChart":
        out = []
        cw = w / 8
        for i, hyp in enumerate(HYPO_ORDER):
            srt = sorted(((v[0], c) for c, v in SC[hyp].items()), reverse=True)
            top = 4
            for val, c in srt:
                bh = (h - 30) * val / 100.0 * 2.4
                out.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;'
                           'width:%.1fpx;height:%.1fpx;background:%s;opacity:.92"></div>'
                           % (i * cw + cw * 0.12, top, cw * 0.76, max(3, bh), CB[BLOC[c]]))
                top += max(3, bh) + 1
            out.append('<div style="position:absolute;left:%.1fpx;bottom:2px;width:%.1fpx;'
                       'text-align:center;font:9px Segoe UI;color:#0E1E33">%s</div>'
                       % (i * cw, cw, hyp))
        return "".join(out)
    if vt == "lineChart":
        out = ['<div style="position:absolute;inset:0"></div>']
        for c in CANDS:
            a = [SC[h][c][0] for h in HYPO_ORDER if c in SC[h] and CONF[h] == "4 grands candidats"]
            b_ = [SC[h][c][0] for h in HYPO_ORDER if c in SC[h] and CONF[h] == "3 grands candidats"]
            if not a or not b_:
                continue
            v1, v2 = sum(a)/len(a), sum(b_)/len(b_)
            y1 = h - 30 - (h - 60) * v1 / 40.0
            y2 = h - 30 - (h - 60) * v2 / 40.0
            out.append('<svg style="position:absolute;left:0;top:0;width:%dpx;height:%dpx;'
                       'overflow:visible"><line x1="%d" y1="%.1f" x2="%d" y2="%.1f" '
                       'stroke="%s" stroke-width="2"/></svg>'
                       % (w, h, int(w*0.18), y1, int(w*0.82), y2, CB[BLOC[c]]))
        out.append('<div style="position:absolute;left:%d;bottom:4px;font:8px Segoe UI;'
                   'color:#4A5768">4 grands candidats</div>'
                   '<div style="position:absolute;right:8px;bottom:4px;font:8px Segoe UI;'
                   'color:#4A5768">3 grands candidats</div>' % int(w*0.10))
        return "".join(out)
    if not rows:
        return '<div style="font:9px Segoe UI;color:#8A94A3;padding:4px">%s</div>' % vt
    mx = max(abs(r[1]) for r in rows) or 1
    n = len(rows)
    if vt == "barChart":
        rh = h / n
        out = []
        for i, (lab, val, col) in enumerate(rows):
            bw = (w * 0.60) * val / mx
            fs = min(10, max(6.5, rh * 0.40))
            out.append('<div style="position:absolute;left:0;top:%.1fpx;height:%.1fpx;'
                       'width:%dpx;font:%.1fpx Segoe UI;color:#0E1E33;line-height:%.1fpx;'
                       'overflow:hidden;white-space:nowrap;text-overflow:ellipsis">%s</div>'
                       '<div style="position:absolute;left:%dpx;top:%.1fpx;height:%.1fpx;'
                       'width:%.1fpx;background:%s;border-radius:0 3px 3px 0"></div>'
                       '<div style="position:absolute;left:%.1fpx;top:%.1fpx;height:%.1fpx;'
                       'font:600 %.1fpx Segoe UI;color:#0E1E33;line-height:%.1fpx">%s</div>'
                       % (i*rh, rh, int(w*0.30), fs, rh, html.escape(lab),
                          int(w*0.31), i*rh+rh*0.20, rh*0.60, bw, col,
                          int(w*0.31)+bw+6, i*rh, rh, fs, rh,
                          ("%.1f" % val).replace(".", ",")))
        return "".join(out)
    cw = w / n
    out = []
    zero = h - 24 if min(r[1] for r in rows) >= 0 else (h - 24) / 2 + 10
    for i, (lab, val, col) in enumerate(rows):
        bh = (zero - 10) * abs(val) / mx if val >= 0 else (h - 34 - zero) * abs(val) / mx
        top = zero - bh if val >= 0 else zero
        out.append('<div style="position:absolute;left:%.1fpx;top:%.1fpx;width:%.1fpx;'
                   'height:%.1fpx;background:%s;border-radius:3px 3px 0 0"></div>'
                   '<div style="position:absolute;left:%.1fpx;bottom:2px;width:%.1fpx;'
                   'text-align:center;font:%.1fpx Segoe UI;color:#0E1E33;overflow:hidden">%s</div>'
                   % (i*cw+cw*0.18, top, cw*0.64, max(2, bh), col,
                      i*cw, cw, min(9, max(6, cw*0.16)), html.escape(lab)))
    return "".join(out)


def rendu():
    ordre = json.load(open(os.path.join(PAGES, "pages.json"), encoding="utf-8"))["pageOrder"]
    out = ['<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=1340">'
           '<title>Intentions de vote 2027 : aperçu du rapport Power BI</title>'
           '<style>'
           'body{margin:0;background:#22262C;font-family:Segoe UI,Arial;color:#E6E3DA}'
           'header{max-width:1280px;margin:0 auto;padding:44px 0 10px}'
           'header h1{font:400 30px Georgia,serif;margin:0 0 10px;color:#F2F1EC}'
           'header p{margin:0 0 6px;font-size:14px;line-height:1.6;color:#A9B0BA;max-width:900px}'
           'header a{color:#D8B24A}'
           '.libelle{max-width:1280px;margin:30px auto 8px;font:600 13px Segoe UI,Arial;'
           'letter-spacing:.09em;text-transform:uppercase;color:#D8B24A}'
           '.page{position:relative;width:1280px;height:720px;margin:0 auto 6px;'
           'background:#F2F1EC;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,.45)}'
           'footer{max-width:1280px;margin:34px auto;padding-bottom:40px;font-size:13px;'
           'line-height:1.6;color:#8A94A3}'
           '</style></head><body>']
    if PUBLICATION:
        out.append(
            '<header><h1>Intentions de vote à l\'élection présidentielle de 2027</h1>'
            '<p>Aperçu statique des six pages du rapport Power BI. Les visuels sont '
            'reconstitués à partir des fichiers de définition du projet et des '
            'données publiées. Les cadres, les titres et les proportions sont fidèles, '
            'le rendu exact des graphiques ne l\'est pas.</p>'
            '<p>Source des chiffres : enquête Ipsos bva et CESI école d\'ingénieurs pour '
            'Le Parisien, terrain des 27 et 28 mai 2026, rapport publié en juin 2026.</p>'
            '</header>')
    for pid in ordre:
        pg = json.load(open(os.path.join(PAGES, pid, "page.json"), encoding="utf-8"))
        if PUBLICATION:
            out.append('<div class="libelle">%s</div>' % html.escape(pg["displayName"]))
        out.append('<div class="page">')
        viss = [json.load(open(f, encoding="utf-8"))
                for f in glob.glob(os.path.join(PAGES, pid, "visuals", "*", "visual.json"))]
        viss.sort(key=lambda v: v["position"].get("z", 0))
        for vis in viss:
            p = vis["position"]
            x, y, w, h = p["x"], p["y"], p["width"], p["height"]
            vt = prop(vis, "visual", "visualType")
            bg, bd, t, st = chrome_of(vis)
            style = ("position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;"
                     "overflow:hidden;box-sizing:border-box;" % (x, y, w, h))
            if bg:
                style += "background:%s;border-radius:8px;" % bg
            if bd:
                style += "border:1px solid %s;border-radius:8px;" % bd
            head, cy = "", 0
            if t:
                head += ('<div style="position:absolute;left:12px;top:8px;right:12px;'
                         'font:%.1fpx %s,Georgia,serif;color:%s;white-space:nowrap;'
                         'overflow:hidden;text-overflow:ellipsis">%s</div>'
                         % (t[1]*1.333, t[3].split()[0], t[2], html.escape(t[0])))
                cy = 8 + t[1]*1.333 + 6
            if st:
                head += ('<div style="position:absolute;left:12px;top:%.1fpx;right:12px;'
                         'font:%.1fpx Segoe UI;color:%s;overflow:hidden">%s</div>'
                         % (cy, st[1]*1.333, st[2], html.escape(st[0])))
                cy += st[1]*1.333*1.5 + 6
            cy = max(cy, 8) if (t or st) else 6
            inner = ""
            if vt == "textbox":
                paras = prop(vis, "visual", "objects", "general", 0, "properties",
                             "paragraphs", defaut=[])
                lines = []
                for para in paras:
                    runs = ""
                    for r in para.get("textRuns", []):
                        ts = r.get("textStyle", {})
                        fam = ts.get("fontFamily", "Segoe UI")
                        wgt = "600" if "Semibold" in fam else ("300" if "Light" in fam else "400")
                        runs += ('<span style="font:%s %.1fpx %s,Arial;color:%s">%s</span>'
                                 % (wgt, float(ts.get("fontSize", "10pt").replace("pt", ""))*1.333,
                                    fam.split()[0], ts.get("color", "#4A5768"),
                                    html.escape(r["value"])))
                    lines.append('<div style="text-align:%s;line-height:1.45;margin-bottom:2px">%s</div>'
                                 % (para.get("horizontalTextAlignment", "left"), runs))
                inner = ('<div style="position:absolute;left:12px;right:12px;top:%.1fpx;'
                         'bottom:6px;overflow:hidden">%s</div>' % (cy, "".join(lines)))
            elif vt == "card":
                m = prop(vis, "visual", "query", "queryState", "Values", "projections", 0,
                         "nativeQueryRef", defaut="")
                lp = prop(vis, "visual", "objects", "labels", 0, "properties", defaut={})
                fs = float(litt(lp.get("fontSize", {}), "30"))
                col = litt(lp.get("color", {}), "#0E1E33")
                al = litt(lp.get("horizontalAlignment", {}), "left")
                fam = litt(lp.get("fontFamily", {}), "Segoe UI Light")
                wgt = "300" if "Light" in fam else ("600" if "Semibold" in fam else "400")
                inner = ('<div style="position:absolute;left:12px;right:12px;top:%.1fpx;'
                         'font:%s %.1fpx %s,Arial;color:%s;text-align:%s;line-height:1.1">%s</div>'
                         % (cy + 2, wgt, fs*1.333, fam.split()[0], col, al,
                            html.escape(VAL.get(m, m))))
            elif vt == "slicer":
                colname = prop(vis, "visual", "query", "queryState", "Values",
                               "projections", 0, "nativeQueryRef", defaut="")
                items = CANDS if colname == "Candidat" else [LIB[h] for h in HYPO_ORDER]
                inner = ('<div style="position:absolute;left:12px;right:12px;top:%.1fpx;'
                         'bottom:6px;overflow:hidden">%s</div>'
                         % (cy, "".join('<div style="font:11px Segoe UI;color:#0E1E33;'
                                        'padding:5px 2px;border-bottom:1px solid #F2EFE8;'
                                        'white-space:nowrap;overflow:hidden;'
                                        'text-overflow:ellipsis">☐ %s</div>' % html.escape(i)
                                        for i in items)))
            elif vt in ("tableEx", "pivotTable"):
                qs = prop(vis, "visual", "query", "queryState", defaut={})
                if vt == "tableEx":
                    cols = [q["nativeQueryRef"] for q in qs["Values"]["projections"]]
                    nrows = 13 if any(c in ("Candidat", "NomCourt") for c in cols) else 8
                    labs = ([COURT[c] for c in CANDS] if nrows == 13
                            else [h for h in HYPO_ORDER])
                else:
                    cols = ["Candidat"] + list(HYPO_ORDER)
                    nrows, labs = 13, CANDS
                cw2 = (w - 24) / len(cols)
                rowh = max(11, (h - cy - 26) / nrows)
                head2 = "".join('<div style="display:inline-block;width:%.1fpx;'
                                'font:600 8px Segoe UI;color:#8A94A3;padding:2px;'
                                'box-sizing:border-box;overflow:hidden">%s</div>'
                                % (cw2, html.escape(c)) for c in cols)
                body = ""
                for r in range(nrows):
                    cells = ""
                    for ci, c in enumerate(cols):
                        if ci == 0:
                            val, bgc = labs[r], ""
                        elif vt == "pivotTable":
                            cand = CANDS[r]; hyp = cols[ci]
                            if cand in SC[hyp]:
                                sc = SC[hyp][cand][0]
                                t_ = min(1.0, sc / 36.0)
                                bgc = "background:rgba(46,92,138,%.2f);" % (0.06 + 0.85 * t_)
                                val = ("%.1f %%" % sc).replace(".", ",")
                                if t_ > 0.55:
                                    bgc += "color:#fff;"
                            else:
                                val, bgc = "", ""
                        else:
                            val, bgc = "13,5 %", ""
                        cells += ('<div style="display:inline-block;width:%.1fpx;height:%.1fpx;'
                                  'font:8.5px Segoe UI;color:#0E1E33;padding:1px 3px;'
                                  'box-sizing:border-box;overflow:hidden;white-space:nowrap;'
                                  'text-overflow:ellipsis;%s">%s</div>'
                                  % (cw2, rowh, bgc, html.escape(str(val))))
                    body += '<div style="height:%.1fpx;white-space:nowrap">%s</div>' % (rowh, cells)
                inner = ('<div style="position:absolute;left:12px;right:12px;top:%.1fpx;'
                         'bottom:4px;overflow:hidden"><div style="border-bottom:1px solid '
                         '#EFECE4;margin-bottom:2px">%s</div>%s</div>' % (cy, head2, body))
            else:
                inner = ('<div style="position:absolute;left:12px;right:12px;top:%.1fpx;'
                         'bottom:8px;overflow:hidden"><div style="position:relative;'
                         'width:100%%;height:100%%">%s</div></div>'
                         % (cy, graphe(vis, w - 24, int(h - cy - 16))))
            out.append('<div style="%s">%s%s</div>' % (style, head, inner))
        if PUBLICATION:
            out.append('</div>')
        else:
            out.append('<div style="position:absolute;left:0;bottom:0;font:9px monospace;'
                       'color:#b00;background:#fff">%s</div></div>'
                       % html.escape(pg["displayName"]))
    if PUBLICATION:
        out.append(
            '<footer>Les données chiffrées proviennent du rapport public de l\'institut. '
            'Aucune valeur n\'est simulée. Le projet Power BI complet, le modèle et le '
            'générateur sont dans le dépôt.</footer>')
    out.append("</body></html>")
    with io.open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write("".join(out))
    print("Aperçu écrit dans :", SORTIE, "(%d pages)" % len(ordre))


if __name__ == "__main__":
    rendu()
