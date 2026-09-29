# -*- coding: utf-8 -*-
"""
Les six pages du rapport, plus une page d'info-bulle.

Chaque titre de page est une affirmation, pas un sujet : la suite des six
titres se lit comme une démonstration, et le fil de progression en pied de
page rappelle où l'on en est.
"""
from pbuild_core import *

M, C, Hy = "Mesures", "Candidats", "Hypotheses"
TT = "infobulle2027candidat"
ENTETE = 52
_alertes = []


def bloc_prose(x, y, w, h, paragraphes, z=5, *, titre=None, sous_titre=None,
               carte=True):
    besoin = hauteur_texte(paragraphes, w) + (ENTETE if titre else 12)
    if besoin > h:
        _alertes.append("prose x=%d y=%d : besoin %d px, disponible %d px (%s)"
                        % (x, y, besoin, h, (titre or str(paragraphes)[:40])))
    return texte(x, y, w, h, paragraphes, z,
                 container=chrome(titre=titre, sous_titre=sous_titre, carte=carte,
                                  border=RULE if carte else None))


def puce(titre, corps):
    return [("▍ ", 9.5, ACCENT, F_BOLD), (titre + " : ", 9.5, INK, F_BOLD),
            (corps, 9, INK_SOFT, F_REG)]


VIDE = [(" ", 5, MUTE, F_REG)]


# ============================================================== PAGE 01 =====
def p01_constat():
    v = bandeau("Dans les huit hypothèses testées, le Rassemblement national arrive en tête",
                "Aucune configuration d'offre ne remet en cause la première place : "
                "l'avance sur le deuxième ne descend jamais sous 16,5 points",
                "01 · LE CONSTAT")

    kpi = [("Score du 1er (%)", "Candidat en tête", "Moyenne des huit hypothèses"),
           ("Meilleur score mesuré (%)", "Meilleur score mesuré",
            "J. Bardella, hypothèse H7"),
           ("Total extrême droite (%)", "Total extrême droite",
            "Trois candidats cumulés"),
           ("Écart minimal 1er / 2e (pts)", "Avance minimale sur le 2e",
            "En points, hypothèse la plus serrée")]
    v.append(carte_kpi(MARGE, 96, 390, 118, 10, kpi[0][0], kpi[0][1], kpi[0][2], size=36))
    for i, (mes, lab, sub) in enumerate(kpi[1:]):
        v.append(carte_kpi(446 + i * (254 + 16), 96, 254, 118, 11 + i, mes, lab, sub,
                           size=27))

    v.append(barres(MARGE, 230, 640, 454, 30,
                    cat="Candidat", vals="Score (%)", table_cat=C,
                    couleur_mesure="Couleur du candidat",
                    tri=tri_mesure(M, "Score (%)"), n_cat=13, tooltip_page=TT,
                    lbl_size=10.5, lbl_pos="OutsideEnd", cat_size=10,
                    leg=False, marge_cat=30,
                    titre="Le classement moyen des treize personnalités testées",
                    sous_titre="En % des suffrages exprimés, couleur du parti, "
                               "J. Bardella et M. Le Pen ne sont jamais testés ensemble"))

    v.append(barres(696, 230, 544, 202, 32,
                    cat="Bloc", vals="Score (%)", table_cat=C,
                    couleur_mesure="Couleur du bloc",
                    tri=tri_mesure(M, "Score (%)"), n_cat=5,
                    lbl_size=11, lbl_pos="OutsideEnd", cat_size=10.5, marge_cat=32,
                    titre="Le bloc d'extrême droite pèse près de 38 %",
                    sous_titre="Total de chaque bloc, du plus lourd au plus léger"))

    v.append(bloc_prose(696, 442, 544, 242, [
        puce("Le RN en tête partout",
             "Bardella s'établit entre 33,5 % et 36 %, Le Pen entre 31 % et 32 %. "
             "L'avance sur le deuxième ne descend jamais sous 16,5 points."),
        VIDE,
        puce("Le second rang dépend de l'offre",
             "Philippe passe de 13 % à 19 % et Attal de 8,5 % à 17,5 % selon que "
             "l'autre candidat du bloc central est présent ou non."),
        VIDE,
        puce("La gauche reste fragmentée",
             "Ses cinq candidats se partagent 29,5 à 35 points ; Mélenchon en capte "
             "13 à 13,5 à lui seul."),
        VIDE,
        puce("Une réserve de 7 à 11 %",
             "C'est la part des certains d'aller voter sans intention exprimée. "
             "Elle croît quand l'offre se resserre."),
    ], z=34, titre="Ce qu'il faut retenir"))

    v += pied(0, "Résultats en % des exprimés.")
    return page("01 · Le constat", v)


# ============================================================== PAGE 02 =====
def p02_stabilite():
    v = bandeau("La tête du classement ne bouge jamais ; tout le reste se recompose",
                "Les mêmes neuf personnalités dans les huit configurations : la première "
                "place ne change jamais de camp, la deuxième change de titulaire",
                "02 · LA STABILITÉ")

    v.append(colonnes_groupees(MARGE, 96, UTILE, 296, 30,
                               cat="Code", vals="Score au classement (%)", table_cat=Hy,
                               serie="Candidat", table_serie=C,
                               couleur_mesure="Couleur du candidat",
                               tri=tri_colonne(Hy, "Ordre"), n_cat=8,
                               axe_val=True, grille=True, lbl=False, cat_size=10,
                               leg=True, leg_pos="Bottom", leg_size=8.5,
                               titre="Le même bloc en tête, un peloton qui se réordonne",
                               sous_titre="Score de chaque personnalité dans les huit "
                                          "hypothèses, limité à celles dépassant 5 % dans "
                                          "au moins une hypothèse"))

    v.append(matrice(MARGE, 402, 744, 282, 32,
                     lignes_=[(C, "Candidat")], colonnes_=[(Hy, "Code")],
                     valeurs=["Score (%)"], tri=tri_colonne(C, "Ordre"),
                     size=8.5, padding_ligne=0, tooltip_page=TT,
                     titre="Les quatre-vingt-quatre scores publiés",
                     sous_titre="Une cellule vide signale un candidat absent de "
                                "l'hypothèse ; chaque colonne totalise 100 %"))

    v.append(bloc_prose(800, 402, 440, 282, [
        puce("Une tête immobile",
             "Le candidat du Rassemblement national occupe la première place dans les "
             "huit hypothèses, sans exception."),
        VIDE,
        puce("Un deuxième rang disputé",
             "Mélenchon, Philippe puis Attal s'y succèdent selon l'hypothèse "
             "retenue."),
        VIDE,
        puce("Un socle de gauche stable",
             "Mélenchon, Arthaud, Roussel et Tondelier varient de moins d'un point "
             "d'une configuration à l'autre."),
        VIDE,
        puce("Une lecture par colonne",
             "Chaque colonne totalise 100 %, donc les scores d'une hypothèse ne se "
             "comparent qu'entre eux."),
    ], z=34, titre="Lecture du classement"))

    v += pied(1, "Une hypothèse = une question posée séparément.")
    return page("02 · La stabilité du classement", v)


# ============================================================== PAGE 03 =====
def p03_offre():
    v = bandeau("Ce qui fait varier les scores, c'est l'offre, pas l'électorat",
                "Retirer un des deux candidats du bloc central déplace jusqu'à neuf "
                "points ; le socle du Rassemblement national ne bouge que de 2,5",
                "03 · L'EFFET DE L'OFFRE")

    v.append(lignes(MARGE, 96, 596, 300, 30,
                    cat="Configuration", vals="Score au classement (%)", table_cat=Hy,
                    serie="Candidat", table_serie=C,
                    couleur_mesure="Couleur du candidat",
                    axe_val=True, grille=True, lbl=False, cat_size=9.5, marqueurs=True,
                    leg=True, leg_pos="Bottom", leg_size=8.5,
                    titre="Une candidature de moins, et le bloc central se redistribue",
                    sous_titre="Score en configuration à quatre grands candidats, puis à "
                               "trois, personnalités au-dessus de 5 %"))

    v.append(nuage(652, 96, 588, 300, 32,
                   detail="Candidat", mx="Score (%)", my="Amplitude (pts)",
                   table_detail=C, couleur_mesure="Couleur du candidat",
                   titre="Un score élevé n'est pas un score solide",
                   sous_titre="Score moyen en abscisse, amplitude entre hypothèses en "
                              "ordonnée",
                   x_titre="Score moyen (%)", y_titre="Amplitude (points)"))

    v.append(colonnes(MARGE, 412, 596, 272, 34,
                      cat="NomCourt", vals="Effet de l’offre resserrée (pts)", table_cat=C,
                      tri=tri_mesure(M, "Effet de l’offre resserrée (pts)"),
                      couleur_mesure="Couleur du candidat",
                      lbl_size=9, cat_size=8.5, precision=1,
                      n_cat=13, tooltip_page=TT,
                      titre="Attal et Philippe captent l'essentiel du report",
                      sous_titre="Écart de score entre les hypothèses à trois grands "
                                 "candidats et celles à quatre, en points"))

    v.append(tableau(652, 412, 588, 272, 36, [
        (C, "Candidat", False),
        (M, "Score (%)", True),
        (M, "Amplitude (pts)", True),
        (M, "Hypothèses en tête", True),
    ], tri=tri_mesure(M, "Score (%)"), size=8, entete=8, padding_ligne=0,
        titre="Niveau, dispersion et premières places",
        sous_titre="Treize personnalités, classées par score moyen décroissant"))

    v += pied(2, "Candidats absents non comptés.")
    return page("03 · L'effet de l'offre", v)


# ============================================================== PAGE 04 =====
def p04_profils():
    v = bandeau("Aucune personnalité du bloc central ne résiste au changement d'offre",
                "Sélectionnez un nom : son score, sa dispersion autour de sa moyenne et "
                "son intervalle de confiance se recalculent hypothèse par hypothèse",
                "04 · LES PROFILS")

    v.append(segment(MARGE, 96, 232, 588, 20, C, "Candidat",
                     titre="Candidat", sous_titre="Sélection unique conseillée",
                     tri=tri_colonne(C, "Ordre"), size=10))

    v.append(carte_texte(288, 96, 380, 118, 30, "Candidat de référence",
                         size=15, col=INK, font=F_TITLE, carte=True,
                         titre="PERSONNALITÉ RETENUE",
                         sous_titre="Sans sélection, la page montre le candidat arrivé en tête"))

    kw, gap, x0 = 176, 14, 682
    for i, (mes, lab, sub) in enumerate([
            ("Profil · score (%)", "Score moyen", "Sur la sélection"),
            ("Profil · amplitude (pts)", "Amplitude", "Écart haut / bas"),
            ("Profil · premières places", "Premières places", "Sur huit hypothèses")]):
        v.append(carte_kpi(x0 + i * (kw + gap), 96, kw, 118, 31 + i, mes, lab, sub,
                           size=26))

    v.append(barres(288, 230, 476, 454, 40,
                    cat="Hypothese", vals="Profil · score (%)", table_cat=Hy,
                    n_cat=8, tooltip_page=TT, couleur_mesure="Profil · couleur",
                    tri=tri_colonne(Hy, "Ordre"),
                    lbl_size=10, lbl_pos="OutsideEnd", cat_size=9, marge_cat=44,
                    titre="Son niveau, hypothèse par hypothèse",
                    sous_titre="En % des suffrages exprimés"))

    v.append(colonnes(776, 230, 464, 224, 41,
                      cat="Code", vals="Profil · écart à sa moyenne (pts)", table_cat=Hy,
                      n_cat=8, couleur_mesure="Profil · couleur",
                      tri=tri_colonne(Hy, "Ordre"),
                      lbl_size=9, cat_size=9, precision=1,
                      titre="Où il sur-performe, où il décroche",
                      sous_titre="Écart entre le score de l'hypothèse et sa propre "
                                 "moyenne, en points"))

    v.append(tableau(776, 462, 464, 222, 42, [
        (Hy, "Code", False),
        (M, "Profil · score (%)", True),
        (M, "Profil · borne basse (%)", True),
        (M, "Profil · borne haute (%)", True),
    ], tri=tri_colonne(Hy, "Ordre"), size=9, entete=8, padding_ligne=1,
        titre="Son intervalle de confiance à 95 %",
        sous_titre="Bornes publiées par Ipsos"))

    v += pied(3, "Rang calculé sur la sélection.")
    return page("04 · Les profils", v)


# ============================================================== PAGE 05 =====
def p05_conclusions():
    v = bandeau("Ce que cette enquête établit, et ce qu'elle ne dit pas",
                "Trois constats tiennent la marge d'erreur ; quatre questions restent "
                "hors du champ de l'enquête",
                "05 · LES CONCLUSIONS")

    v.append(bloc_prose(MARGE, 96, 592, 290, [
        puce("Le rapport de force de tête est solide",
             "L'avance minimale du candidat RN sur son poursuivant est de 16,5 points, "
             "près de trois fois la somme des deux marges d'erreur. Ce constat ne dépend "
             "d'aucune hypothèse particulière."),
        VIDE,
        puce("La cannibalisation du bloc central est mesurée",
             "Attal gagne 9 points et Philippe 6 quand l'autre disparaît de l'offre, "
             "alors que le total du bloc perd environ 5 points."),
        VIDE,
        puce("La fragmentation de la gauche est structurelle",
             "Cinq candidats, aucun au-dessus de 14 %, un total qui varie peu, donc la "
             "dispersion ne tient pas à la configuration testée."),
    ], z=20, titre="Ce que l'enquête établit",
        sous_titre="Constats qui résistent aux marges d'erreur publiées"))

    v.append(bloc_prose(MARGE, 396, 592, 288, [
        puce("Aucune hypothèse de second tour",
             "L'enquête s'arrête au premier tour. Rien ici ne permet d'anticiper un "
             "report de voix ni une issue finale."),
        VIDE,
        puce("Aucun croisement sociodémographique",
             "Ni âge, ni profession, ni proximité partisane, les écarts internes à "
             "chaque électorat restent invisibles."),
        VIDE,
        puce("Aucune dynamique dans le temps",
             "Vague isolée, sans comparaison avec les mesures précédentes. On lit un "
             "niveau, jamais une tendance."),
        VIDE,
        puce("Onze mois d'écart",
             "Terrain de mai 2026 pour une échéance d'avril 2027, avant déclarations "
             "de candidature et avant campagne."),
    ], z=21, titre="Ce que l'enquête ne dit pas",
        sous_titre="Limites à énoncer avant toute question de la salle"))

    v.append(tableau(664, 96, 576, 290, 22, [
        (Hy, "Code", False),
        (M, "Score du 1er (%)", True),
        (M, "Score du 2e (%)", True),
        (M, "Écart 1er / 2e (pts)", True),
    ], tri=tri_colonne(Hy, "Ordre"), size=9.5, entete=8.5, padding_ligne=2,
        titre="L'écart de tête, hypothèse par hypothèse",
        sous_titre="Il ne descend jamais sous 16,5 points"))

    v.append(bloc_prose(664, 396, 576, 288, [
        puce("La candidature unique au centre",
             "Le report est réel mais incomplet, le bloc central perd environ 5 points "
             "en passant de deux candidats à un. Une candidature unique ne récupère pas "
             "l'addition des deux."),
        VIDE,
        puce("La réserve des indécis",
             "De 7 à 11 % des personnes certaines d'aller voter n'expriment aucune "
             "intention, et cette part croît quand l'offre se resserre."),
        VIDE,
        puce("La comparabilité Bardella / Le Pen",
             "Les deux ne sont jamais testés ensemble, et l'écart entre leurs moyennes ne "
             "mesure pas une préférence, mais deux jeux de questions différents."),
    ], z=23, titre="Trois questions pour la suite",
        sous_titre="Ce que le commanditaire voudra creuser"))

    v += pied(4, "À confronter aux marges d'erreur.")
    return page("05 · Les conclusions", v)


# ============================================================== PAGE 06 =====
def p06_methode():
    v = bandeau("Une enquête par quotas, à lire avec ses marges d'erreur",
                "Fiche technique complète et cadre d'interprétation des écarts mesurés",
                "06 · LA MÉTHODE")

    v.append(bloc_prose(MARGE, 96, 380, 290, [
        puce("Échantillon",
             "1 500 personnes inscrites sur les listes électorales, représentatives de "
             "la population française de 18 ans et plus."),
        VIDE,
        puce("Terrain",
             "27 et 28 mai 2026, échantillon interrogé en ligne via l'Access panel Ipsos."),
        VIDE,
        puce("Représentativité",
             "Méthode des quotas appliquée au sexe, à l'âge, à la profession et à la "
             "zone géographique."),
        VIDE,
        puce("Commanditaire",
             "Ipsos bva et CESI école d'ingénieurs pour Le Parisien."),
    ], z=20, titre="Fiche méthodologique",
        sous_titre="Norme ISO 20252 : études de marché, sociales et d'opinion"))

    v.append(bloc_prose(MARGE, 396, 380, 288, [
        puce("Ce n'est pas une prévision",
             "Une intention de vote mesure un rapport de force à la date du terrain, "
             "pas un résultat à onze mois de l'échéance."),
        VIDE,
        puce("Les petits écarts n'en sont pas",
             "Un écart inférieur à la somme des marges d'erreur des deux candidats "
             "comparés n'est pas significatif."),
        VIDE,
        puce("Sondage par quotas",
             "L'intervalle de confiance n'est rigoureusement calculable que pour les "
             "sondages aléatoires, on le considère proche ici."),
    ], z=21, titre="Précautions de lecture"))

    v.append(tableau(432, 96, 400, 290, 22, [
        (Hy, "Code", False),
        (Hy, "Base", False),
        (Hy, "SansReponse", False),
        (Hy, "NbCandidats", False),
    ], tri=tri_colonne(Hy, "Ordre"), size=9.5, entete=8.5, padding_ligne=2,
        titre="Base et non-réponse",
        sous_titre="Personnes exprimées et part sans intention déclarée"))

    v.append(tableau(432, 396, 400, 288, 23, [
        (Hy, "Code", False),
        (Hy, "Configuration", False),
        (Hy, "FinalisteRN", False),
        (Hy, "CandidatGauche", False),
    ], tri=tri_colonne(Hy, "Ordre"), size=8.5, entete=8, padding_ligne=4,
        titre="Ce que teste chaque hypothèse",
        sous_titre="Configuration d'offre et candidats pivots"))

    v.append(barres(844, 96, 396, 340, 24,
                    cat="Candidat", vals="Marge d’erreur (pts)", table_cat=C, n_cat=13,
                    tri=tri_mesure(M, "Marge d’erreur (pts)"),
                    couleur_mesure="Couleur du candidat",
                    lbl_size=8.5, cat_size=8.5, marge_cat=36,
                    titre="La marge croît avec le score",
                    sous_titre="Demi-intervalle de confiance à 95 %, en points"))

    v.append(bloc_prose(844, 446, 396, 238, [
        [("Sur une base de 1 079 personnes, un score mesuré à 20 % signifie qu'il y a "
          "95 chances sur 100 pour que la valeur réelle se situe entre ", 9, INK_SOFT, F_REG),
         ("17,6 % et 22,4 %", 9, INK, F_BOLD),
         (", soit plus ou moins 2,4 points.", 9, INK_SOFT, F_REG)],
        VIDE,
        [("Plus le score mesuré est proche de 50 %, plus l'intervalle est large ; plus "
          "la base est petite, plus il s'élargit également.", 9, INK_SOFT, F_REG)],
    ], z=25, titre="Comment lire un intervalle"))

    v += pied(5, "Rapport publié en juin 2026.")
    return page("06 · La méthode", v)


# ========================================================== INFO-BULLE ======
def p07_infobulle():
    v = [carte_texte(10, 8, 300, 34, 10, "Candidat sélectionné", size=12, col=INK,
                     font=F_BOLD, carte=False)]
    for i, (mes, lab) in enumerate([("Score (%)", "SCORE MOYEN"),
                                    ("Amplitude (pts)", "AMPLITUDE"),
                                    ("Hypothèses en tête", "1res PLACES")]):
        v.append(carte_kpi(10 + i * 100, 46, 96, 74, 11 + i, mes, lab, size=18))
    v.append(colonnes(10, 126, 300, 106, 20,
                      cat="Code", vals="Score (%)", table_cat=Hy, n_cat=8,
                      tri=tri_colonne(Hy, "Ordre"),
                      couleur_mesure="Couleur du candidat",
                      lbl=False, cat_size=7.5, carte=True,
                      titre="Score par hypothèse"))
    return page("Info-bulle · profil candidat", v, infobulle=True,
                largeur=320, hauteur=240, nom_interne=TT)


PAGES = [p01_constat, p02_stabilite, p03_offre, p04_profils, p05_conclusions,
         p06_methode, p07_infobulle]


def alertes():
    return _alertes
