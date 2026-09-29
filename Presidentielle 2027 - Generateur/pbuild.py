# -*- coding: utf-8 -*-
"""
Génère le projet Power BI au format .pbip « Presidentielle 2027 » à partir du
rapport Ipsos bva et CESI pour Le Parisien de juin 2026.

Usage :
    python pbuild.py "<dossier de destination>" "<thème de base>" "<racine Windows>"

Seul le premier argument est utile en général. Le dossier courant sert de
destination par défaut.
"""
import os, sys, json, shutil, uuid
import pbuild_core as K
from pbuild_core import nid
from pdata import CANDIDATS, SCORES, HYPO_ORDER, ecarts
from pbuild_model import ecrire_csv, ecrire_modele
import pbuild_pages as P

NOM = "Presidentielle 2027"

SEUIL_SERIE = 5.0   # meme seuil que la mesure « Score au classement (%) »


def _couleurs_theme():
    """Personnalités au-dessus du seuil d'abord, puis les autres."""
    ordonnes = sorted(CANDIDATS, key=lambda c: c[4])
    def maxi(nom):
        v = [SCORES[h][nom][0] for h in HYPO_ORDER if nom in SCORES[h]]
        return max(v) if v else 0.0
    grands = [c[5] for c in ordonnes if maxi(c[0]) >= SEUIL_SERIE]
    petits = [c[5] for c in ordonnes if maxi(c[0]) < SEUIL_SERIE]
    return grands + petits + ["#16324F", "#4A5768", "#8A94A3", "#B08A26"]


THEME = {
    "name": "SondageIpsos2027",
    # Ordre des couleurs du thème.
    #
    # La mise en forme conditionnelle par mesure colore correctement les visuels
    # SANS série, mais Power BI l'ignore dès qu'une série est présente : il
    # distribue alors les couleurs du thème dans l'ordre d'apparition des
    # séries. Les deux visuels à série, les colonnes de la page 02 et la pente
    # de la page 03, n'affichent que les personnalités dépassant 5 %. On place
    # donc celles-ci en tête du thème, dans leur ordre d'affichage : chacune
    # retombe ainsi sur la couleur de son parti sans aucun réglage visuel.
    "dataColors": _couleurs_theme(),
    "foreground": K.INK,
    "foregroundNeutralSecondary": K.INK_SOFT,
    "foregroundNeutralTertiary": K.MUTE,
    "background": "#FFFFFF",
    "backgroundLight": K.PAGE_BG,
    "backgroundNeutral": "#EDEAE2",
    "tableAccent": K.ACCENT,
    "good": "#2E7D32",
    "bad": "#8C1D18",
    "neutral": K.ACCENT,
    "maximum": K.INK,
    "center": "#7C8B9E",
    "minimum": "#DDE4EC",
    "hyperlink": "#1F6FB2",
    "textClasses": {
        "title":   {"fontFace": K.F_TITLE, "fontSize": 13, "color": K.INK},
        "header":  {"fontFace": K.F_BOLD,  "fontSize": 11, "color": K.INK},
        "label":   {"fontFace": K.F_REG,   "fontSize": 9,  "color": K.INK_SOFT},
        "callout": {"fontFace": K.F_LIGHT, "fontSize": 26, "color": K.INK},
    },
    "visualStyles": {
        "*": {"*": {
            "background": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}}],
            "border": [{"show": False}],
            "dropShadow": [{"show": False}],
        }}
    },
}

REPORT_JSON = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
    "themeCollection": {
        "baseTheme": {
            "name": "CY26SU07",
            "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"},
            "type": "SharedResources",
        },
        "customTheme": {
            "name": "SondageIpsos2027",
            "reportVersionAtImport": {"visual": "2.11.0", "report": "3.4.0", "page": "2.3.1"},
            "type": "RegisteredResources",
        },
    },
    "objects": {
        "section": [{"properties": {"verticalAlignment": {
            "expr": {"Literal": {"Value": "'Top'"}}}}}],
        "outspacePane": [{"properties": {"expanded": {
            "expr": {"Literal": {"Value": "false"}}}}}],
    },
    "resourcePackages": [
        {"name": "SharedResources", "type": "SharedResources",
         "items": [{"name": "CY26SU07", "path": "BaseThemes/CY26SU07.json", "type": "BaseTheme"}]},
        {"name": "RegisteredResources", "type": "RegisteredResources",
         "items": [{"name": "SondageIpsos2027", "path": "SondageIpsos2027.json",
                    "type": "CustomTheme"}]},
    ],
    "settings": {
        "useStylableVisualContainerHeader": True,
        "exportDataMode": "AllowSummarized",
        "defaultDrillFilterOtherVisuals": True,
        "allowChangeFilterTypes": True,
        "useEnhancedTooltips": True,
        "useDefaultAggregateDisplayName": True,
    },
}


def controler_tmdl(racine):
    """Garde-fou : un nom TMDL délimité par une apostrophe simple ne peut pas en
    contenir une. C'est l'erreur InvalidLineType renvoyée à l'ouverture."""
    import glob as _g, re as _re
    decl = _re.compile(r"^\t*(measure|column|table|partition|hierarchy) '")
    valide = _re.compile(r"^\t*(measure|column|table|partition|hierarchy) '[^']+'( =.*)?$")
    erreurs = []
    for f in _g.glob(os.path.join(racine, "definition", "**", "*.tmdl"), recursive=True):
        for i, ligne in enumerate(open(f, encoding="utf-8"), start=1):
            l = ligne.rstrip("\n")
            if decl.match(l) and not valide.match(l):
                erreurs.append("%s:%d  %s" % (os.path.basename(f), i, l.strip()[:80]))
    if erreurs:
        raise SystemExit("Noms TMDL invalides (apostrophe droite) :\n  " + "\n  ".join(erreurs))
    return True


def _ecarter_orphelins(racine, d, attendus):
    """Écarte les pages et visuels laissés par une génération précédente. Le
    dossier peut être monté sans droit de suppression : on déplace alors le
    reste dans un dossier de rebut."""
    import glob as _g, shutil as _sh
    rebut = os.path.join(os.path.dirname(racine), "_rebut Presidentielle 2027")
    ecartes = 0

    def _jeter(chemin):
        nonlocal ecartes
        try:
            _sh.rmtree(chemin)
        except OSError:
            os.makedirs(rebut, exist_ok=True)
            cible = os.path.join(rebut, os.path.basename(chemin))
            i = 1
            while os.path.exists(cible):
                cible = os.path.join(rebut, "%s_%d" % (os.path.basename(chemin), i))
                i += 1
            try:
                _sh.move(chemin, cible)
            except OSError:
                return
        ecartes += 1

    for pdir in _g.glob(os.path.join(d, "pages", "*")):
        if not os.path.isdir(pdir):
            continue
        pid = os.path.basename(pdir)
        if pid not in attendus:
            _jeter(pdir)
            continue
        for vdir in _g.glob(os.path.join(pdir, "visuals", "*")):
            if os.path.isdir(vdir) and os.path.basename(vdir) not in attendus[pid]:
                _jeter(vdir)
    if ecartes:
        print("  - %d élément(s) obsolète(s) écarté(s)" % ecartes)


def jw(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def ecrire_rapport(racine, nom, base_theme_src=None):
    d = os.path.join(racine, "definition")
    os.makedirs(os.path.join(d, "pages"), exist_ok=True)
    os.makedirs(os.path.join(racine, "StaticResources", "RegisteredResources"), exist_ok=True)
    os.makedirs(os.path.join(racine, "StaticResources", "SharedResources", "BaseThemes"),
                exist_ok=True)

    jw(os.path.join(racine, ".platform"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Report", "displayName": nom},
        "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
    })
    jw(os.path.join(racine, "definition.pbir"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {"byPath": {"path": "../%s.SemanticModel" % nom}},
    })
    jw(os.path.join(d, "version.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0",
    })
    jw(os.path.join(d, "report.json"), REPORT_JSON)
    jw(os.path.join(racine, "StaticResources", "RegisteredResources",
                    "SondageIpsos2027.json"), THEME)

    if base_theme_src and os.path.isfile(base_theme_src):
        shutil.copy(base_theme_src,
                    os.path.join(racine, "StaticResources", "SharedResources",
                                 "BaseThemes", os.path.basename(base_theme_src)))

    ordre, attendus = [], {}
    for fn in P.PAGES:
        pg, visuals = fn()
        pid = pg["name"]
        if "pageBinding" not in pg:      # les pages d'info-bulle restent hors sommaire
            ordre.append(pid)
        jw(os.path.join(d, "pages", pid, "page.json"), pg)
        attendus[pid] = {v["name"] for v in visuals}
        for vis in visuals:
            jw(os.path.join(d, "pages", pid, "visuals", vis["name"], "visual.json"), vis)

    _ecarter_orphelins(racine, d, attendus)

    if K.alertes_scroll():
        print("ATTENTION : risque de barre de défilement :")
        for a in K.alertes_scroll():
            print("   ", a)

    if hasattr(P, "alertes") and P.alertes():
        print("ATTENTION : prose trop longue pour son cadre :")
        for a in P.alertes():
            print("   ", a)

    jw(os.path.join(d, "pages", "pages.json"), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": ordre,
        "activePageName": ordre[0],
    })
    return ordre


def main(dest, base_theme_src=None, win_dest=None):
    """dest           : où écrire physiquement les fichiers.
       base_theme_src : thème de base à recopier dans les ressources du rapport.
       win_dest       : chemin tel que Power BI Desktop le verra sous Windows.
                        Il alimente la valeur par défaut du paramètre
                        CheminDonnees. Par défaut, dest est repris tel quel."""
    mauvaises = ecarts()
    if mauvaises:
        raise SystemExit(
            "Les hypothèses suivantes ne totalisent pas 100 % :\n  "
            + "\n  ".join("%s = %s %%" % (h, t) for h, t, _n in mauvaises))

    dest = os.path.abspath(dest)
    dossier_data = os.path.join(dest, "%s - Donnees" % NOM)
    rep_model = os.path.join(dest, "%s.SemanticModel" % NOM)
    rep_report = os.path.join(dest, "%s.Report" % NOM)

    for p in (rep_model, rep_report):
        if os.path.isdir(p):
            try:
                shutil.rmtree(p)
            except OSError:
                pass  # dossier sans droit de suppression : on ecrase fichier par fichier

    chemins = ecrire_csv(dossier_data)
    if win_dest:
        base = win_dest.rstrip("\\/") + "\\%s - Donnees\\" % NOM
        chemins = tuple(base + os.path.basename(c) for c in chemins)
    ecrire_modele(rep_model, NOM, chemins)
    controler_tmdl(rep_model)
    ordre = ecrire_rapport(rep_report, NOM, base_theme_src)

    jw(os.path.join(dest, "%s.pbip" % NOM), {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [{"report": {"path": "%s.Report" % NOM}}],
        "settings": {"enableAutoRecovery": True},
    })

    nv = sum(len(os.listdir(os.path.join(rep_report, "definition", "pages", p, "visuals")))
             for p in ordre)
    print("Projet écrit dans :", dest)
    print("  - données      :", dossier_data)
    print("  - modèle       :", rep_model)
    print("  - rapport      :", rep_report, "(%d pages, %d visuels)" % (len(ordre), nv))


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "."
    theme = sys.argv[2] if len(sys.argv) > 2 else None
    win = sys.argv[3] if len(sys.argv) > 3 else None
    main(dest, theme, win)
