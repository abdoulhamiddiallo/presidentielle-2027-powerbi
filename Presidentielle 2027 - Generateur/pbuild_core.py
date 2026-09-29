# -*- coding: utf-8 -*-
"""
Moteur de rendu PBIR, version 2.

Principe directeur : aucun élément décoratif en zone de texte.
Les titres, sous-titres, fonds et bordures sont ceux du conteneur de visuel,
natifs de Power BI, qui gèrent seuls leur marge interne. Plus de texte rogné,
plus de rectangle parasite. Les zones de texte ne portent que de la prose.
"""
import hashlib

# ---------------------------------------------------------------- canevas ---
W, H = 1280, 720
BAND_H = 84            # bandeau superieur
TOP = 96               # premiere ligne de contenu
BOT = 684              # derniere ligne de contenu
MARGE = 40
UTILE = W - 2 * MARGE  # 1200

# ------------------------------------------------------------------ encre ---
PAGE_BG  = "#F2F1EC"   # fond de page, lin
OUTSPACE = "#DEDCD3"
CARD     = "#FFFFFF"
INK      = "#0E1E33"   # encre principale
INK_SOFT = "#4A5768"   # encre secondaire
MUTE     = "#8A94A3"   # encre tertiaire
RULE     = "#E3E0D7"
ACCENT   = "#B08A26"   # or sobre
BAND     = "#0E1E33"

# Palette des blocs politiques, dans l'ordre de OrdreBloc, de 1 à 5.
# Contrôlée deux à deux : bande de luminosité, chroma et contraste d'au moins
# 3:1. Les paires rouge et rose, bleu et marine restent proches, contrainte
# sémantique des couleurs partisanes. D'où l'encodage secondaire systématique :
# chaque marque porte son libellé.
BLOC_COLORS = ["#B33A2E", "#D4577E", "#BE8420", "#2E7DB8", "#41539E"]

F_TITLE = "Georgia"
F_BOLD  = "Segoe UI Semibold"
F_REG   = "Segoe UI"
F_LIGHT = "Segoe UI Light"

SCHEMA_VIS  = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json"
SCHEMA_PAGE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"

_seq = [0]


def nid(seed=""):
    _seq[0] += 1
    return hashlib.md5(("p2027v2|%s|%d" % (seed, _seq[0])).encode()).hexdigest()[:20]


# ------------------------------------------------------- expressions PBIR ---
def lit(v):    return {"expr": {"Literal": {"Value": v}}}
def s(v):      return lit("'%s'" % v)
def b(v):      return lit("true" if v else "false")
def d(v):      return lit("%sD" % v)
def color(c):  return {"solid": {"color": {"expr": {"Literal": {"Value": "'%s'" % c}}}}}


def chrome(*, titre=None, sous_titre=None, carte=True, border=RULE, radius=8,
           ombre=False, t_size=12, t_color=INK, t_font=F_TITLE, st_size=8.5,
           st_color=MUTE, align="left", padding=None):
    """Conteneur natif : fond, bordure arrondie, titre et sous-titre gérés par
    Power BI (donc jamais rognés)."""
    o = {
        "background": ([{"properties": {"show": b(True), "color": color(CARD),
                                        "transparency": d(0)}}]
                       if carte else [{"properties": {"show": b(False)}}]),
        "border": ([{"properties": {"show": b(True), "color": color(border),
                                    "radius": d(radius)}}]
                   if border else [{"properties": {"show": b(False),
                                                   "radius": d(radius)}}]),
        "dropShadow": [{"properties": {"show": b(bool(ombre)), "color": color("#0E1E33"),
                                       "transparency": d(92), "shadowSpread": d(2),
                                       "shadowBlur": d(8), "angle": d(90),
                                       "shadowDistance": d(2), "preset": s("Custom")}}],
        "visualHeader": [{"properties": {"show": b(False)}}],
    }
    if titre:
        o["title"] = [{"properties": {
            "show": b(True), "text": s(titre), "fontSize": d(t_size),
            "fontColor": color(t_color), "fontFamily": s(t_font),
            "alignment": s(align), "titleWrap": b(False),
            "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
        }}]
    else:
        o["title"] = [{"properties": {"show": b(False)}}]
    if sous_titre:
        o["subTitle"] = [{"properties": {
            "show": b(True), "text": s(sous_titre), "fontSize": d(st_size),
            "fontColor": color(st_color), "fontFamily": s(F_REG),
            "alignment": s(align), "titleWrap": b(False)}}]
    else:
        o["subTitle"] = [{"properties": {"show": b(False)}}]
    if padding is not None:
        o["padding"] = [{"properties": {"top": d(padding), "bottom": d(padding),
                                        "left": d(padding), "right": d(padding)}}]
    return o


def visual(vtype, x, y, w, h, z, *, objects=None, query=None, container=None,
           extra=None, seed=""):
    v = {"visualType": vtype}
    if query:
        v["query"] = query
    if objects:
        v["objects"] = objects
    v["visualContainerObjects"] = container if container is not None else chrome(carte=False,
                                                                                border=None)
    if extra:
        v.update(extra)
    return {
        "$schema": SCHEMA_VIS,
        "name": nid("%s|%s|%s|%s" % (vtype, seed, x, y)),
        "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z},
        "visual": v,
    }


# ------------------------------------------------------------ prose seule ---
def texte(x, y, w, h, paragraphes, z=5, *, align="left", container=None):
    """paragraphes : liste de listes de tuples (texte, taille en points, couleur,
    police). Réserve la hauteur largement : Power BI ajoute sa propre marge."""
    paras = []
    for para in paragraphes:
        if isinstance(para, tuple):
            para = [para]
        runs = []
        for item in para:
            val, size, col, font = (list(item) + [None] * 4)[:4]
            runs.append({"value": val, "textStyle": {
                "fontFamily": font or F_REG,
                "fontSize": "%spt" % (size if size is not None else 10),
                "color": col or INK_SOFT}})
        paras.append({"textRuns": runs, "horizontalTextAlignment": align})
    return visual("textbox", x, y, w, h, z,
                  objects={"general": [{"properties": {"paragraphs": paras}}]},
                  container=container if container is not None
                  else chrome(carte=False, border=None), seed=str(paragraphes)[:40])


def hauteur_texte(paragraphes, largeur):
    """Estimation haute de la hauteur nécessaire, marge interne comprise."""
    total = 20
    for para in paragraphes:
        if isinstance(para, tuple):
            para = [para]
        txt = "".join(p[0] for p in para)
        pt = max((p[1] or 10) for p in para)
        cpl = max(8, int((largeur - 24) / (pt * 0.52)))
        lignes = max(1, -(-len(txt) // cpl))
        total += lignes * pt * 1.80 + 4
    return int(total)


# ------------------------------------------------------ requetes de visuel ---
def f_measure(t, n):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": t}}, "Property": n}}


def f_column(t, n):
    return {"Column": {"Expression": {"SourceRef": {"Entity": t}}, "Property": n}}


def proj(field, t, n, active=None):
    p = {"field": field, "queryRef": "%s.%s" % (t, n), "nativeQueryRef": n}
    if active is not None:
        p["active"] = active
    return p


def qm(t, n, active=None):  return proj(f_measure(t, n), t, n, active)
def qc(t, n, active=None):  return proj(f_column(t, n), t, n, active)


def query(state, sort=None):
    q = {"queryState": state}
    if sort:
        q["sortDefinition"] = {"sort": sort}
    return q


def tri_mesure(t, n, sens="Descending"):
    return [{"field": f_measure(t, n), "direction": sens}]


def tri_colonne(t, n, sens="Ascending"):
    return [{"field": f_column(t, n), "direction": sens}]


# ------------------------------------------------------- blocs graphiques ---
def axe(show=True, *, titre=False, grille=False, size=9.5, col=INK_SOFT,
        font=F_REG, marge=None, extra=None, invert=False):
    p = {"show": b(show), "showAxisTitle": b(titre), "gridlineShow": b(grille),
         "fontSize": d(size), "labelColor": color(col), "fontFamily": s(font),
         "concatenateLabels": b(False)}
    if invert:
        p["invertAxis"] = b(True)
    if grille:
        p["gridlineColor"] = color("#EDEAE2")
        p["gridlineThickness"] = d(1)
        p["gridlineStyle"] = s("solid")
    if marge is not None:
        p["maxMarginFactor"] = d(marge)
    if extra:
        p.update(extra)
    return [{"properties": p}]


def legende(show=True, pos="TopCenter", size=9, col=INK_SOFT):
    return [{"properties": {"show": b(show), "position": s(pos), "fontSize": d(size),
                            "labelColor": color(col), "fontFamily": s(F_REG),
                            "showTitle": b(False)}}]


def etiquettes(show=True, *, size=9.5, col=INK, font=F_BOLD, precision=1,
               position=None, fond=False):
    if not show:
        return [{"properties": {"show": b(False)}}]
    p = {"show": b(True), "fontSize": d(size), "color": color(col),
         "fontFamily": s(font), "labelDisplayUnits": d(0),
         "labelPrecision": d(precision),
         "backgroundTransparency": d(20 if fond else 100),
         "enableBackground": b(bool(fond))}
    if fond:
        p["backgroundColor"] = color("#FFFFFF")
    if position:
        p["labelPosition"] = s(position)
    return [{"properties": p}]


_scroll = []


def alertes_scroll():
    return _scroll


def _verifie_place(vtype, w, h, n_cat, leg, titre):
    """Ne refuse rien, mais signale tout risque de barre de défilement."""
    if not n_cat:
        return
    utile = h - 52 - (30 if leg else 0) - 12
    if vtype in ("barChart", "clusteredBarChart"):
        par_cat = utile / n_cat
        mini = 30
        sens = "px par barre"
    else:
        par_cat = (w - 24) / n_cat
        mini = 30
        sens = "px par colonne"
    if par_cat < mini:
        _scroll.append("%s « %s » : %.0f %s (minimum %d) : defilement probable"
                       % (vtype, titre or "?", par_cat, sens, mini))


def _cart(vtype, x, y, w, h, z, *, cat, vals, table_cat, table_val="Mesures",
          serie=None, table_serie="Candidats", fill=None, tri=None,
          axe_cat=True, cat_size=9.5, axe_val=False, grille=False,
          lbl=True, lbl_size=9.5, lbl_pos="InsideEnd", precision=1,
          leg=False, leg_pos="TopCenter", leg_size=9, marge_cat=None,
          titre=None, sous_titre=None, carte=True, seed="", objets_sup=None,
          n_cat=None, tooltip_page=None, couleur_mesure=None,
          axe_val_inverse=False, marqueurs=False, lbl_fond=False):
    _verifie_place(vtype, w, h, n_cat, leg, titre)
    vals = vals if isinstance(vals, (list, tuple)) else [vals]
    state = {"Category": {"projections": [qc(table_cat, cat, active=True)]},
             "Y": {"projections": [qm(table_val, m) for m in vals]}}
    if serie:
        state["Series"] = {"projections": [qc(table_serie, serie)]}
    objs = {
        "categoryAxis": axe(axe_cat, size=cat_size, col=INK, font=F_BOLD,
                            marge=marge_cat),
        "valueAxis": axe(axe_val, grille=grille, size=9, col=MUTE,
                         invert=axe_val_inverse),
        "legend": legende(leg, leg_pos, size=leg_size),
        "labels": etiquettes(lbl, size=lbl_size, precision=precision, position=lbl_pos,
                             fond=lbl_fond),
    }
    if marqueurs:
        objs["lineStyles"] = [{"properties": {"showMarker": b(True),
                                              "markerSize": d(7),
                                              "strokeWidth": d(3),
                                              "lineStyle": s("solid")}}]
    if couleur_mesure:
        objs["dataPoint"] = [{
            "properties": {"fill": {"solid": {"color": {
                "expr": f_measure("Mesures", couleur_mesure)}}}},
            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 0}}]},
        }]
    elif fill and not serie and len(vals) == 1:
        objs["dataPoint"] = [{"properties": {"fill": color(fill)}}]
    if tooltip_page:
        objs["tooltip"] = [{"properties": {"type": s("Canvas"),
                                           "section": s(tooltip_page)}}]
    if objets_sup:
        objs.update(objets_sup)
    return visual(vtype, x, y, w, h, z, objects=objs, query=query(state, tri),
                  container=chrome(titre=titre, sous_titre=sous_titre, carte=carte),
                  seed=seed or cat + str(vals))


def barres(*a, **k):    return _cart("clusteredBarChart", *a, **k)
def barres_empilees(*a, **k): return _cart("barChart", *a, **k)
def colonnes(*a, **k):  return _cart("columnChart", *a, **k)
def colonnes_groupees(*a, **k): return _cart("clusteredColumnChart", *a, **k)
def lignes(*a, **k):    return _cart("lineChart", *a, **k)
def ruban(*a, **k):     return _cart("ribbonChart", *a, **k)


def nuage(x, y, w, h, z, *, detail, mx, my, table_detail="Candidats",
          table_val="Mesures", serie=None, titre=None, sous_titre=None,
          taille_marque=6, lbl=True, x_titre=None, y_titre=None,
          couleur_mesure=None):
    """Nuage de points : niveau en abscisse, sensibilité à l'offre en ordonnée."""
    state = {
        "Category": {"projections": [qc(table_detail, detail, active=True)]},
        "X": {"projections": [qm(table_val, mx)]},
        "Y": {"projections": [qm(table_val, my)]},
    }
    if serie:
        state["Series"] = {"projections": [qc(table_detail, serie)]}
    objs = {
        "categoryAxis": axe(True, titre=bool(x_titre), grille=True, size=9, col=MUTE,
                            extra={"axisTitle": s(x_titre)} if x_titre else None),
        "valueAxis": axe(True, titre=bool(y_titre), grille=True, size=9, col=MUTE,
                         extra={"axisTitle": s(y_titre)} if y_titre else None),
        "legend": legende(bool(serie), "TopCenter"),
        "categoryLabels": [{"properties": {"show": b(lbl), "fontSize": d(8.5),
                                           "color": color(INK), "fontFamily": s(F_REG)}}],
        "bubbles": [{"properties": {"bubbleSize": d(taille_marque)}}],
        "fillPoint": [{"properties": {"show": b(True)}}],
    }
    if couleur_mesure:
        objs["dataPoint"] = [{
            "properties": {"fill": {"solid": {"color": {
                "expr": f_measure("Mesures", couleur_mesure)}}}},
            "selector": {"data": [{"dataViewWildcard": {"matchingOption": 0}}]},
        }]
    return visual("scatterChart", x, y, w, h, z, objects=objs, query=query(state),
                  container=chrome(titre=titre, sous_titre=sous_titre), seed=detail + mx)


def carte_kpi(x, y, w, h, z, mesure, libelle, precision_sub=None, *,
              table="Mesures", size=34, col=INK, accent=ACCENT):
    """Carte : le libellé est le titre natif, la précision le sous-titre natif.
    Un seul objet, donc rien ne peut se désaligner."""
    objs = {
        "labels": [{"properties": {"fontSize": d(size), "color": color(col),
                                   "fontFamily": s(F_LIGHT),
                                   "horizontalAlignment": s("left")}}],
        "categoryLabels": [{"properties": {"show": b(False)}}],
        "wordWrap": [{"properties": {"show": b(False)}}],
    }
    cont = chrome(titre=libelle.upper(), sous_titre=precision_sub,
                  t_size=8.5, t_color=MUTE, t_font=F_BOLD,
                  st_size=8.5, st_color=INK_SOFT, ombre=True)
    return visual("card", x, y, w, h, z, objects=objs,
                  query=query({"Values": {"projections": [qm(table, mesure)]}}),
                  container=cont, seed=mesure)


def carte_texte(x, y, w, h, z, mesure, *, table="Mesures", size=12, col=INK,
                font=F_BOLD, align="left", titre=None, sous_titre=None, carte=False):
    objs = {
        "labels": [{"properties": {"fontSize": d(size), "color": color(col),
                                   "fontFamily": s(font),
                                   "horizontalAlignment": s(align)}}],
        "categoryLabels": [{"properties": {"show": b(False)}}],
        "wordWrap": [{"properties": {"show": b(True)}}],
    }
    return visual("card", x, y, w, h, z, objects=objs,
                  query=query({"Values": {"projections": [qm(table, mesure)]}}),
                  container=chrome(titre=titre, sous_titre=sous_titre, carte=carte,
                                   border=RULE if carte else None),
                  seed=mesure)


def segment(x, y, w, h, z, table, colonne, *, titre=None, sous_titre=None,
            unique=False, size=10, tri=None, orientation=None):
    objs = {
        "general": [{"properties": {"outlineColor": color(RULE), "outlineWeight": d(0)}}],
        "selection": [{"properties": {"singleSelect": b(unique),
                                      "strictSingleSelect": b(unique),
                                      "selectAllCheckboxEnabled": b(not unique)}}],
        "items": [{"properties": {"fontColor": color(INK), "fontSize": d(size),
                                  "fontFamily": s(F_REG), "background": color(CARD),
                                  "outline": s("None")}}],
        "header": [{"properties": {"show": b(False)}}],
    }
    if orientation:
        objs["general"][0]["properties"]["orientation"] = s(orientation)
    return visual("slicer", x, y, w, h, z, objects=objs,
                  query=query({"Values": {"projections": [qc(table, colonne, active=True)]}},
                              tri),
                  container=chrome(titre=titre, sous_titre=sous_titre), seed=colonne)


def tableau(x, y, w, h, z, colonnes_, *, tri=None, titre=None, sous_titre=None,
            size=9.5, entete=8.5, padding_ligne=4, seed=""):
    projs = [qm(t, n) if m else qc(t, n) for t, n, m in colonnes_]
    objs = {
        "grid": [{"properties": {"gridVertical": b(False), "gridHorizontal": b(True),
                                 "gridHorizontalColor": color("#EFECE4"),
                                 "gridHorizontalWeight": d(1),
                                 "outlineColor": color("#EFECE4"), "outlineWeight": d(0),
                                 "rowPadding": d(padding_ligne)}}],
        "columnHeaders": [{"properties": {"fontColor": color(MUTE), "fontSize": d(entete),
                                          "fontFamily": s(F_BOLD), "backColor": color(CARD),
                                          "outline": s("BottomOnly"), "wordWrap": b(True),
                                          "autoSizeColumnWidth": b(True)}}],
        "values": [{"properties": {"fontColor": color(INK), "fontSize": d(size),
                                   "fontFamily": s(F_REG), "backColor": color(CARD),
                                   "backColorSecondary": color("#FAF9F5"),
                                   "outline": s("None"), "wordWrap": b(False)}}],
        "total": [{"properties": {"totals": b(False)}}],
    }
    return visual("tableEx", x, y, w, h, z, objects=objs,
                  query=query({"Values": {"projections": projs}}, tri),
                  container=chrome(titre=titre, sous_titre=sous_titre),
                  seed=seed or str(colonnes_)[:40])


def matrice(x, y, w, h, z, lignes_, colonnes_, valeurs, *, tri=None, titre=None,
            sous_titre=None, size=9.5, padding_ligne=2, heatmap=None,
            tooltip_page=None):
    """heatmap = (mesure, couleur minimale, couleur maximale) pour la mise en
    forme conditionnelle du fond des cellules."""
    vprops = {"fontColor": color(INK), "fontSize": d(size), "fontFamily": s(F_REG),
              "backColor": color(CARD), "backColorSecondary": color(CARD),
              "outline": s("None")}
    if heatmap:
        mes, cmin, cmax = heatmap
        gradient = {"linearGradient2": {
            "min": {"color": {"Literal": {"Value": "'%s'" % cmin}}},
            "max": {"color": {"Literal": {"Value": "'%s'" % cmax}}},
        }}
        regle = {"FillRule": {
            "Input": f_measure("Mesures", mes),
            "FillRule": gradient,
        }}
        vprops["backColor"] = {"solid": {"color": {"expr": regle}}}
        heat_selector = {"data": [{"dataViewWildcard": {"matchingOption": 0}}]}
    objs = {
        "grid": [{"properties": {"gridVertical": b(False), "gridHorizontal": b(False),
                                 "outlineColor": color("#EFECE4"), "outlineWeight": d(0),
                                 "rowPadding": d(padding_ligne)}}],
        "columnHeaders": [{"properties": {"fontColor": color(MUTE), "fontSize": d(8.5),
                                          "fontFamily": s(F_BOLD), "backColor": color(CARD),
                                          "outline": s("BottomOnly"), "wordWrap": b(True),
                                          "autoSizeColumnWidth": b(True),
                                          "alignment": s("Center")}}],
        "rowHeaders": [{"properties": {"fontColor": color(INK), "fontSize": d(size),
                                       "fontFamily": s(F_REG), "backColor": color(CARD),
                                       "outline": s("None"), "stepped": b(False)}}],
        "values": ([{"properties": vprops, "selector": heat_selector}]
                   if heatmap else [{"properties": vprops}]),
        "subTotals": [{"properties": {"rowSubtotals": b(False),
                                      "columnSubtotals": b(False)}}],
        "total": [{"properties": {"totals": b(False)}}],
    }
    if tooltip_page:
        objs["tooltip"] = [{"properties": {"type": s("Canvas"),
                                           "section": s(tooltip_page)}}]
    state = {"Rows": {"projections": [qc(*r) for r in lignes_]},
             "Columns": {"projections": [qc(*c) for c in colonnes_]},
             "Values": {"projections": [qm("Mesures", v) for v in valeurs]}}
    return visual("pivotTable", x, y, w, h, z, objects=objs, query=query(state, tri),
                  container=chrome(titre=titre, sous_titre=sous_titre), seed=str(valeurs))


# --------------------------------------------------------------- ossature ---
def bandeau(titre, chapeau, onglet):
    """Bandeau supérieur : deux zones de texte largement dimensionnées, posées
    sur un fond de page sombre géré par la page elle-même."""
    fond = visual("textbox", 0, 0, W, BAND_H, 0,
                  objects={"general": [{"properties": {"paragraphs": [
                      {"textRuns": [{"value": " ", "textStyle": {"fontSize": "8pt"}}]}]}}]},
                  container={
                      "background": [{"properties": {"show": b(True), "color": color(BAND),
                                                     "transparency": d(0)}}],
                      "border": [{"properties": {"show": b(False)}}],
                      "dropShadow": [{"properties": {"show": b(False)}}],
                      "visualHeader": [{"properties": {"show": b(False)}}],
                      "title": [{"properties": {"show": b(False)}}],
                      "subTitle": [{"properties": {"show": b(False)}}],
                  }, seed="bandeau")
    gauche = texte(MARGE, 10, 860, 66, [
        [(titre, 16, "#FFFFFF", F_TITLE)],
        [(chapeau, 9, "#94A6BE", F_REG)],
    ], z=2)
    droite = texte(W - 400, 12, 360, 62, [
        [(onglet, 8.5, "#7F93AD", F_BOLD)],
        [("Ipsos bva · CESI · Le Parisien", 10, ACCENT, F_BOLD)],
    ], z=2, align="right")
    return [fond, gauche, droite]


ETAPES = ["01 Constat", "02 Stabilité", "03 Offre", "04 Profils",
          "05 Conclusions", "06 Méthode"]


def pied(etape_courante, note=""):
    """Fil de progression : la démonstration se lit d'un bout à l'autre."""
    fil = []
    for i, e in enumerate(ETAPES):
        actuel = (i == etape_courante)
        fil.append((e, 7.5, ACCENT if actuel else MUTE,
                    F_BOLD if actuel else F_REG))
        if i < len(ETAPES) - 1:
            fil.append(("   ▸   ", 7.5, "#C9C4B8", F_REG))
    return [
        texte(MARGE, 690, 620, 30, [fil], z=2),
        texte(680, 690, 560, 30,
              [[("Ipsos bva · CESI pour Le Parisien, terrain des 27 et 28 mai 2026. "
                 + note, 7.5, MUTE, F_REG)]], z=2, align="right"),
    ]


def page(nom_affiche, visuels, *, fond=PAGE_BG, infobulle=False, largeur=W,
         hauteur=H, nom_interne=None):
    pid = nom_interne or nid("page|" + nom_affiche)
    pg = {
        "$schema": SCHEMA_PAGE,
        "name": pid,
        "displayName": nom_affiche,
        "displayOption": "FitToPage",
        "height": hauteur, "width": largeur,
        "objects": {
            "background": [{"properties": {"color": color(fond), "transparency": d(0)}}],
            "outspace": [{"properties": {"color": color(OUTSPACE), "transparency": d(0)}}],
        },
    }
    if infobulle:
        pg["pageBinding"] = {"name": pid + "_tt", "type": "Tooltip", "parameters": []}
        pg["visibility"] = "HiddenInViewMode"
    return pg, visuels
