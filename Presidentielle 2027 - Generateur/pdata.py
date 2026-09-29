# -*- coding: utf-8 -*-
"""
Données extraites du rapport Ipsos bva et CESI pour Le Parisien,
« Intentions de vote à l'élection présidentielle de 2027 », juin 2026.

Terrain : 27 et 28 mai 2026.
Échantillon : 1 500 inscrits sur les listes électorales.
Source : pages 5 à 13 du rapport publié, récapitulatif et huit planches
d'hypothèses.

Ce fichier est la source unique de vérité du projet : les fichiers CSV, le
modèle sémantique et les commentaires des visuels en découlent tous.
"""

# ---------------------------------------------------------------------------
# Dimension CANDIDATS
# ordre = ordre de présentation du rapport, de la gauche vers la droite
# ---------------------------------------------------------------------------
CANDIDATS = [
    # candidat, parti, bloc, ordre du bloc, ordre du candidat, couleur du parti
    ("Nathalie Arthaud",      "Lutte ouvriere",      "Gauche radicale",        1,  1, "#9E2B22"),
    ("Jean-Luc Melenchon",    "La France insoumise", "Gauche radicale",        1,  2, "#CC2936"),
    ("Fabien Roussel",        "Parti communiste",    "Gauche radicale",        1,  3, "#D9694F"),
    ("Marine Tondelier",      "Les Ecologistes",     "Gauche et ecologistes",  2,  4, "#2E7D32"),
    ("Raphael Glucksmann",    "Place publique",      "Gauche et ecologistes",  2,  5, "#E8637C"),
    ("Francois Hollande",     "Parti socialiste",    "Gauche et ecologistes",  2,  6, "#C25E7A"),
    ("Gabriel Attal",         "Renaissance",         "Centre",                 3,  7, "#D98B1F"),
    ("Edouard Philippe",      "Horizons",            "Centre",                 3,  8, "#0E7C6B"),
    ("Bruno Retailleau",      "Les Republicains",    "Droite",                 4,  9, "#3E93D6"),
    ("Nicolas Dupont-Aignan", "Debout la France",    "Droite",                 4, 10, "#6FB0DE"),
    ("Jordan Bardella",       "Rassemblement national", "Extreme droite",      5, 11, "#35529A"),
    ("Marine Le Pen",         "Rassemblement national", "Extreme droite",      5, 12, "#4463B0"),
    ("Eric Zemmour",          "Reconquete",          "Extreme droite",         5, 13, "#8C4A1E"),
]

# Libellés affichés, accents compris : le CSV est écrit en UTF-8 avec BOM
ACCENTS = {
    "Nathalie Arthaud": "Nathalie Arthaud",
    "Jean-Luc Melenchon": "Jean-Luc Mélenchon",
    "Fabien Roussel": "Fabien Roussel",
    "Marine Tondelier": "Marine Tondelier",
    "Raphael Glucksmann": "Raphaël Glucksmann",
    "Francois Hollande": "François Hollande",
    "Gabriel Attal": "Gabriel Attal",
    "Edouard Philippe": "Édouard Philippe",
    "Bruno Retailleau": "Bruno Retailleau",
    "Nicolas Dupont-Aignan": "Nicolas Dupont-Aignan",
    "Jordan Bardella": "Jordan Bardella",
    "Marine Le Pen": "Marine Le Pen",
    "Eric Zemmour": "Éric Zemmour",
}
NOM_COURT = {
    "Nathalie Arthaud": "Arthaud",
    "Jean-Luc Melenchon": "Mélenchon",
    "Fabien Roussel": "Roussel",
    "Marine Tondelier": "Tondelier",
    "Raphael Glucksmann": "Glucksmann",
    "Francois Hollande": "Hollande",
    "Gabriel Attal": "Attal",
    "Edouard Philippe": "Philippe",
    "Bruno Retailleau": "Retailleau",
    "Nicolas Dupont-Aignan": "Dupont-Aignan",
    "Jordan Bardella": "Bardella",
    "Marine Le Pen": "Le Pen",
    "Eric Zemmour": "Zemmour",
}
PARTI_ACC = {
    "Lutte ouvriere": "Lutte ouvrière",
    "La France insoumise": "La France insoumise",
    "Parti communiste": "Parti communiste",
    "Les Ecologistes": "Les Écologistes",
    "Place publique": "Place publique",
    "Parti socialiste": "Parti socialiste",
    "Renaissance": "Renaissance",
    "Horizons": "Horizons",
    "Les Republicains": "Les Républicains",
    "Debout la France": "Debout la France",
    "Rassemblement national": "Rassemblement national",
    "Reconquete": "Reconquête",
}
COULEUR_BLOC = {
    "Gauche radicale":       "#B33A2E",
    "Gauche et ecologistes": "#D4577E",
    "Centre":                "#D98B1F",
    "Droite":                "#3E93D6",
    "Extreme droite":        "#35529A",
}
ORDRE_CONFIG = {"4 grands candidats": 1, "3 grands candidats": 2}
BLOC_ACC = {
    "Gauche radicale": "Gauche radicale",
    "Gauche et ecologistes": "Gauche et écologistes",
    "Centre": "Centre",
    "Droite": "Droite",
    "Extreme droite": "Extrême droite",
}

# ---------------------------------------------------------------------------
# Dimension HYPOTHESES, les huit configurations d'offre testées
# code, libellé court, intitulé complet, base exprimée, part sans réponse, ordre
# ---------------------------------------------------------------------------
HYPOTHESES = [
    ("H1", "H1 · Glucksmann, Attal, Philippe, Bardella",
     "Hypothèse : R. Glucksmann, G. Attal, E. Philippe et J. Bardella", 1079, 7, 6),
    ("H2", "H2 · Glucksmann, Attal, Philippe, Le Pen",
     "Hypothèse : R. Glucksmann, G. Attal, E. Philippe et M. Le Pen", 1073, 7, 7),
    ("H3", "H3 · Hollande, Attal, Philippe, Bardella",
     "Hypothèse : F. Hollande, G. Attal, E. Philippe et J. Bardella", 1060, 9, 8),
    ("H4", "H4 · Hollande, Attal, Philippe, Le Pen",
     "Hypothèse : F. Hollande, G. Attal, E. Philippe et M. Le Pen", 1065, 8, 9),
    ("H5", "H5 · Glucksmann, Attal, Bardella",
     "Hypothèse : R. Glucksmann, G. Attal et J. Bardella", 1050, 9, 10),
    ("H6", "H6 · Glucksmann, Philippe, Bardella",
     "Hypothèse : R. Glucksmann, E. Philippe et J. Bardella", 1057, 9, 11),
    ("H7", "H7 · Hollande, Attal, Bardella",
     "Hypothèse : F. Hollande, G. Attal et J. Bardella", 1037, 11, 12),
    ("H8", "H8 · Hollande, Philippe, Bardella",
     "Hypothèse : F. Hollande, E. Philippe et J. Bardella", 1041, 11, 13),
]
# Le nombre de candidats est recalculé plus bas à partir des scores réels.

# ---------------------------------------------------------------------------
# Faits : score (%) et marge d'erreur (points), par hypothèse et par candidat
# ---------------------------------------------------------------------------
SCORES = {
    "H1": {  # page 6 - base 1079
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.0, 2.0),
        "Fabien Roussel": (3.0, 1.0), "Marine Tondelier": (4.0, 1.2),
        "Raphael Glucksmann": (11.0, 1.9), "Gabriel Attal": (8.5, 1.7),
        "Edouard Philippe": (13.0, 2.0), "Bruno Retailleau": (7.5, 1.6),
        "Nicolas Dupont-Aignan": (1.5, 0.7), "Jordan Bardella": (33.5, 2.8),
        "Eric Zemmour": (4.0, 1.2),
    },
    "H2": {  # page 7 - base 1073
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.0, 2.0),
        "Fabien Roussel": (3.0, 1.0), "Marine Tondelier": (4.0, 1.2),
        "Raphael Glucksmann": (11.0, 1.9), "Gabriel Attal": (8.5, 1.7),
        "Edouard Philippe": (14.0, 2.1), "Bruno Retailleau": (8.5, 1.7),
        "Nicolas Dupont-Aignan": (1.5, 0.7), "Marine Le Pen": (31.0, 2.8),
        "Eric Zemmour": (4.5, 1.2),
    },
    "H3": {  # page 8 - base 1060
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.5, 2.1),
        "Fabien Roussel": (4.0, 1.2), "Marine Tondelier": (4.0, 1.2),
        "Francois Hollande": (7.0, 1.5), "Gabriel Attal": (9.5, 1.8),
        "Edouard Philippe": (13.5, 2.1), "Bruno Retailleau": (8.0, 1.6),
        "Nicolas Dupont-Aignan": (1.5, 0.7), "Jordan Bardella": (34.0, 2.9),
        "Eric Zemmour": (4.0, 1.2),
    },
    "H4": {  # page 9 - base 1065
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.5, 2.1),
        "Fabien Roussel": (4.0, 1.2), "Marine Tondelier": (4.0, 1.2),
        "Francois Hollande": (7.0, 1.5), "Gabriel Attal": (9.5, 1.8),
        "Edouard Philippe": (14.5, 2.1), "Bruno Retailleau": (8.5, 1.7),
        "Nicolas Dupont-Aignan": (1.5, 0.7), "Marine Le Pen": (32.0, 2.8),
        "Eric Zemmour": (4.5, 1.2),
    },
    "H5": {  # page 10 - base 1050
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.0, 2.0),
        "Fabien Roussel": (3.0, 1.0), "Marine Tondelier": (4.0, 1.2),
        "Raphael Glucksmann": (14.0, 2.1), "Gabriel Attal": (14.5, 2.1),
        "Bruno Retailleau": (10.0, 1.8), "Nicolas Dupont-Aignan": (1.5, 0.7),
        "Jordan Bardella": (35.0, 2.9), "Eric Zemmour": (4.0, 1.2),
    },
    "H6": {  # page 11 - base 1057
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.0, 2.0),
        "Fabien Roussel": (3.0, 1.0), "Marine Tondelier": (4.0, 1.2),
        "Raphael Glucksmann": (13.0, 2.0), "Edouard Philippe": (17.5, 2.3),
        "Bruno Retailleau": (9.0, 1.7), "Nicolas Dupont-Aignan": (1.5, 0.7),
        "Jordan Bardella": (34.0, 2.9), "Eric Zemmour": (4.0, 1.2),
    },
    "H7": {  # page 12 - base 1037
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.5, 2.1),
        "Fabien Roussel": (3.5, 1.1), "Marine Tondelier": (5.0, 1.3),
        "Francois Hollande": (8.0, 1.7), "Gabriel Attal": (17.5, 2.3),
        "Bruno Retailleau": (10.0, 1.8), "Nicolas Dupont-Aignan": (1.5, 0.7),
        "Jordan Bardella": (36.0, 2.9), "Eric Zemmour": (4.0, 1.2),
    },
    "H8": {  # page 13 - base 1041
        "Nathalie Arthaud": (1.0, 0.6), "Jean-Luc Melenchon": (13.5, 2.1),
        "Fabien Roussel": (4.0, 1.2), "Marine Tondelier": (5.0, 1.3),
        "Francois Hollande": (7.5, 1.6), "Edouard Philippe": (19.0, 2.4),
        "Bruno Retailleau": (9.0, 1.7), "Nicolas Dupont-Aignan": (1.5, 0.7),
        "Jordan Bardella": (35.5, 2.9), "Eric Zemmour": (4.0, 1.2),
    },
}

HYPO_ORDER = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"]


def controle():
    """Vérifie que chaque hypothèse totalise 100 % des suffrages exprimés."""
    lignes = []
    for h in HYPO_ORDER:
        total = round(sum(v[0] for v in SCORES[h].values()), 2)
        lignes.append((h, total, len(SCORES[h])))
    return lignes


def ecarts():
    """Renvoie les hypothèses dont le total s'écarte de 100 %."""
    return [(h, t, n) for h, t, n in controle() if abs(t - 100.0) > 1e-9]


if __name__ == "__main__":
    import sys
    for h, total, n in controle():
        drapeau = "OK " if abs(total - 100.0) < 1e-9 else "!! "
        print(drapeau, h, "total =", total, "| candidats =", n)
    sys.exit(1 if ecarts() else 0)
