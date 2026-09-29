# -*- coding: utf-8 -*-
"""Écriture des données nettoyées au format CSV et du modèle sémantique TMDL."""
import os, re, csv, uuid
from pdata import (CANDIDATS, HYPOTHESES, SCORES, HYPO_ORDER,
                   ACCENTS, PARTI_ACC, BLOC_ACC, NOM_COURT, COULEUR_BLOC,
                   ORDRE_CONFIG)

def lt():
    return str(uuid.uuid4())

# ---------------------------------------------------------------- CSV -------
def ecrire_csv(dossier):
    os.makedirs(dossier, exist_ok=True)

    p1 = os.path.join(dossier, "Candidats.csv")
    with open(p1, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Candidat", "NomCourt", "Parti", "Bloc", "OrdreBloc", "Ordre",
                    "Couleur", "CouleurBloc"])
        for nom, parti, bloc, ob, o, coul in CANDIDATS:
            w.writerow([ACCENTS[nom], NOM_COURT[nom], PARTI_ACC[parti], BLOC_ACC[bloc],
                        ob, o, coul, COULEUR_BLOC[bloc]])

    p2 = os.path.join(dossier, "Hypotheses.csv")
    with open(p2, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Code", "Hypothese", "Intitule", "Base", "SansReponse",
                    "NbCandidats", "FinalisteRN", "CandidatGauche", "Configuration",
                    "OrdreConfig", "Ordre"])
        for i, (code, court, long_, base, nsp, _n) in enumerate(HYPOTHESES, start=1):
            nb = len(SCORES[code])
            rn = "Jordan Bardella" if "Jordan Bardella" in SCORES[code] else "Marine Le Pen"
            gauche = ("Raphaël Glucksmann" if "Raphael Glucksmann" in SCORES[code]
                      else "François Hollande")
            conf = "4 grands candidats" if nb == 11 else "3 grands candidats"
            w.writerow([code, court, long_, base, nsp, nb, rn, gauche, conf,
                        ORDRE_CONFIG[conf], i])

    p3 = os.path.join(dossier, "Intentions.csv")
    with open(p3, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Code", "Candidat", "Score", "Marge"])
        for code in HYPO_ORDER:
            for nom, _p, _b, _ob, _o, _c in CANDIDATS:
                if nom in SCORES[code]:
                    sc, mg = SCORES[code][nom]
                    w.writerow([code, ACCENTS[nom], ("%g" % sc), ("%g" % mg)])
    return p1, p2, p3


# --------------------------------------------------------------- TMDL -------
def _nom_tmdl(name):
    """Un nom qui n'est pas un identifiant simple doit etre delimite."""
    return name if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name) else "'%s'" % name


def _col(name, dtype, fmt=None, hidden=False, sort_by=None, desc=None,
         summarize="none", source=None):
    L = []
    if desc:
        L.append("\t/// " + desc)
    L.append("\tcolumn %s" % _nom_tmdl(name))
    L.append("\t\tdataType: %s" % dtype)
    if hidden:
        L.append("\t\tisHidden")
    if fmt:
        L.append("\t\tformatString: %s" % fmt)
    L.append("\t\tlineageTag: %s" % lt())
    L.append("\t\tsummarizeBy: %s" % summarize)
    if sort_by:
        L.append("\t\tsortByColumn: %s" % _nom_tmdl(sort_by))
    L.append("\t\tsourceColumn: %s" % (source or name))
    L.append("")
    L.append("\t\tannotation SummarizationSetBy = User")
    L.append("")
    return "\n".join(L)


def _partition_csv(table, fichier, types):
    tt = ", ".join('{"%s", %s}' % (c, t) for c, t in types)
    return (
        "\tpartition %s = m\n"
        "\t\tmode: import\n"
        "\t\tsource =\n"
        "\t\t\t\tlet\n"
        '\t\t\t\t    Source = Csv.Document(File.Contents(CheminDonnees & "%s"), [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n'
        '\t\t\t\t    Entetes = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
        '\t\t\t\t    Types = Table.TransformColumnTypes(Entetes, {%s}, "en-US")\n'
        "\t\t\t\tin\n"
        "\t\t\t\t    Types\n"
        "\n"
        "\tannotation PBI_ResultType = Table\n"
    ) % (table, fichier, tt)


def table_candidats(chemin):
    L = ["/// Référentiel des 13 personnalités testées : parti, bloc politique et",
         "/// ordre de présentation retenu par Ipsos (de la gauche vers la droite).",
         "table Candidats", "\tlineageTag: %s" % lt(), ""]
    L.append(_col("Candidat", "string", desc="Nom de la personnalité testée.",
                  sort_by="Ordre"))
    L.append(_col("Nom court", "string", sort_by="Ordre", source="NomCourt",
                  desc="Nom de famille seul, pour les axes de graphiques étroits."))
    L.append(_col("Parti", "string", desc="Formation politique de rattachement."))
    L.append(_col("Bloc", "string", sort_by="OrdreBloc",
                  desc="Regroupement analytique en cinq blocs politiques."))
    L.append(_col("OrdreBloc", "int64", fmt="0", hidden=True))
    L.append(_col("Ordre", "int64", fmt="0", hidden=True))
    L.append(_col("Couleur", "string", hidden=True,
                  desc="Code couleur du parti, utilisable en mise en forme conditionnelle."))
    L.append(_col("CouleurBloc", "string", hidden=True,
                  desc="Code couleur du bloc politique d'appartenance."))
    L.append(_partition_csv("Candidats", chemin,
                            [("Candidat", "type text"), ("NomCourt", "type text"),
                             ("Parti", "type text"),
                             ("Bloc", "type text"), ("OrdreBloc", "Int64.Type"),
                             ("Ordre", "Int64.Type"), ("Couleur", "type text"),
                             ("CouleurBloc", "type text")]))
    return "\n".join(L)


def table_hypotheses(chemin):
    L = ["/// Les 8 hypothèses de premier tour testées dans l'enquête. Chaque hypothèse",
         "/// a sa propre base de répondants (personnes certaines d'aller voter et ayant",
         "/// exprimé une intention) et son propre taux de non-réponse.",
         "table Hypotheses", "\tlineageTag: %s" % lt(), ""]
    L.append(_col("Code", "string", desc="Identifiant court de l'hypothèse (H1 à H8).",
                  sort_by="Ordre"))
    L.append(_col("Hypothèse", "string", sort_by="Ordre", source="Hypothese",
                  desc="Libellé court : les grands candidats de l'hypothèse."))
    L.append(_col("Intitulé", "string", source="Intitule",
                  desc="Intitulé complet tel qu'imprimé dans le rapport Ipsos."))
    L.append(_col("Base exprimée", "int64", fmt="#,0", summarize="none", source="Base",
                  desc="Nombre de personnes exprimant une intention de vote."))
    L.append(_col("Sans réponse (%)", "double", fmt="0.0", source="SansReponse",
                  desc="Part des personnes certaines d'aller voter sans intention exprimée."))
    L.append(_col("Nb candidats", "int64", fmt="0", source="NbCandidats",
                  desc="Nombre de candidats présents dans l'hypothèse."))
    L.append(_col("Finaliste RN", "string", source="FinalisteRN",
                  desc="Candidat du Rassemblement national testé."))
    L.append(_col("Candidat de gauche", "string", source="CandidatGauche",
                  desc="Candidat social-démocrate testé."))
    L.append(_col("Configuration", "string", sort_by="OrdreConfig",
                  desc="Configuration d'offre : quatre ou trois grands candidats face au RN."))
    L.append(_col("OrdreConfig", "int64", fmt="0", hidden=True))
    L.append(_col("Ordre", "int64", fmt="0", hidden=True))
    L.append(_partition_csv("Hypotheses", chemin,
                            [("Code", "type text"), ("Hypothese", "type text"),
                             ("Intitule", "type text"), ("Base", "Int64.Type"),
                             ("SansReponse", "type number"), ("NbCandidats", "Int64.Type"),
                             ("FinalisteRN", "type text"), ("CandidatGauche", "type text"),
                             ("Configuration", "type text"),
                             ("OrdreConfig", "Int64.Type"), ("Ordre", "Int64.Type")]))
    return "\n".join(L)


def table_intentions(chemin):
    L = ["/// Table de faits : un enregistrement par couple (hypothèse, candidat).",
         "/// 84 lignes issues des pages 6 à 13 du rapport Ipsos.",
         "table Intentions", "\tlineageTag: %s" % lt(), ""]
    L.append(_col("Code", "string", hidden=True))
    L.append(_col("Candidat", "string", hidden=True))
    L.append(_col("Score", "double", fmt="0.0", hidden=True,
                  desc="Intention de vote en % des suffrages exprimés."))
    L.append(_col("Marge", "double", fmt="0.0", hidden=True,
                  desc="Demi-amplitude de l'intervalle de confiance à 95 %, en points."))
    L.append(_partition_csv("Intentions", chemin,
                            [("Code", "type text"), ("Candidat", "type text"),
                             ("Score", "type number"), ("Marge", "type number")]))
    return "\n".join(L)


# Les mesures de niveau sont exprimées en fraction (0,335) et formatées en %.
# Les mesures d'écart sont exprimées en points de pourcentage.
MESURES = [
    ("Score (%)",
     "DIVIDE ( AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )",
     "0.0 %", "01 Intentions de vote",
     "Intention de vote en % des exprimés. Somme des scores du contexte courant, moyennée "
     "sur les hypothèses sélectionnées : exacte pour une hypothèse, moyenne des scénarios sinon."),
    ("Score max (%)",
     "DIVIDE ( MAXX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )",
     "0.0 %", "01 Intentions de vote",
     "Meilleur score obtenu parmi les hypothèses sélectionnées."),
    ("Score min (%)",
     "DIVIDE ( MINX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )",
     "0.0 %", "01 Intentions de vote",
     "Score le plus bas parmi les hypothèses sélectionnées."),
    ("Amplitude (pts)",
     "VAR _max = [Score max (%)]\nVAR _min = [Score min (%)]\n"
     "RETURN IF ( NOT ISBLANK ( _max ), ( _max - _min ) * 100 )",
     "0.0", "01 Intentions de vote",
     "Écart entre le meilleur et le moins bon score, en points : sensibilité à la configuration d'offre."),
    ("Meilleur score mesuré (%)",
     "DIVIDE ( MAXX ( ALLSELECTED ( Intentions ), Intentions[Score] ), 100 )",
     "0.0 %", "01 Intentions de vote",
     "Score le plus élevé observé, tous candidats et toutes hypothèses sélectionnées confondus."),
    ("Marge d’erreur (pts)",
     "AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( AVERAGE ( Intentions[Marge] ) ) )",
     "0.0", "02 Précision statistique",
     "Demi-intervalle de confiance à 95 % publié par Ipsos, en points."),
    ("Borne basse (%)",
     "IF ( NOT ISBLANK ( [Score (%)] ), [Score (%)] - DIVIDE ( [Marge d’erreur (pts)], 100 ) )",
     "0.0 %", "02 Précision statistique",
     "Borne inférieure de l'intervalle de confiance à 95 %."),
    ("Borne haute (%)",
     "IF ( NOT ISBLANK ( [Score (%)] ), [Score (%)] + DIVIDE ( [Marge d’erreur (pts)], 100 ) )",
     "0.0 %", "02 Précision statistique",
     "Borne supérieure de l'intervalle de confiance à 95 %."),
    ("Base moyenne",
     "AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( MAX ( Hypotheses[Base exprimée] ) ) )",
     "#,0", "02 Précision statistique",
     "Nombre de personnes ayant exprimé une intention de vote."),
    ("Sans intention exprimée (%)",
     "DIVIDE ( AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( MAX ( Hypotheses[Sans réponse (%)] ) ) ), 100 )",
     "0.0 %", "02 Précision statistique",
     "Part des personnes certaines d'aller voter n'ayant exprimé aucune intention."),
    ("Nb hypothèses",
     "DISTINCTCOUNT ( Hypotheses[Code] )", "0", "03 Cadrage",
     "Nombre d'hypothèses de premier tour retenues dans le contexte."),
    ("Nb candidats testés",
     "DISTINCTCOUNT ( Intentions[Candidat] )", "0", "03 Cadrage",
     "Nombre de personnalités présentes dans les hypothèses sélectionnées."),
    ("Rang",
     "IF ( NOT ISBLANK ( [Score (%)] ),\n"
     "    RANKX ( ALL ( Candidats[Candidat] ), [Score (%)],, DESC, DENSE ) )",
     "0", "03 Cadrage",
     "Rang du candidat dans le contexte, du score le plus élevé au plus faible."),
    ("Score du 1er (%)",
     "VAR _t = ADDCOLUMNS ( ALLSELECTED ( Candidats[Candidat] ), \"@s\", [Score (%)] )\n"
     "RETURN MAXX ( _t, [@s] )",
     "0.0 %", "04 Écarts", "Score du candidat arrivé en tête."),
    ("Score du 2e (%)",
     "VAR _t = ADDCOLUMNS ( ALLSELECTED ( Candidats[Candidat] ), \"@s\", [Score (%)] )\n"
     "VAR _top = MAXX ( _t, [@s] )\n"
     "RETURN MAXX ( FILTER ( _t, [@s] < _top ), [@s] )",
     "0.0 %", "04 Écarts", "Meilleur score hors candidat de tête."),
    ("Écart 1er / 2e (pts)",
     "( [Score du 1er (%)] - [Score du 2e (%)] ) * 100", "0.0", "04 Écarts",
     "Avance du candidat de tête sur son premier poursuivant, en points."),
    ("Écart au 1er (pts)",
     "IF ( NOT ISBLANK ( [Score (%)] ), ( [Score (%)] - [Score du 1er (%)] ) * 100 )",
     "0.0", "04 Écarts", "Retard du candidat sur celui arrivé en tête, en points."),
    ("Total extrême droite (%)",
     "CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Bloc] = \"Extrême droite\" )",
     "0.0 %", "05 Blocs politiques",
     "Total des candidats d'extrême droite présents dans l'hypothèse."),
    ("Total gauche (%)",
     "CALCULATE ( [Score (%)], ALL ( Candidats ),\n"
     "    Candidats[Bloc] IN { \"Gauche radicale\", \"Gauche et écologistes\" } )",
     "0.0 %", "05 Blocs politiques",
     "Total des candidats de gauche et écologistes."),
    ("Total centre et droite (%)",
     "CALCULATE ( [Score (%)], ALL ( Candidats ),\n"
     "    Candidats[Bloc] IN { \"Centre\", \"Droite\" } )",
     "0.0 %", "05 Blocs politiques",
     "Total du centre et de la droite républicaine."),
    ("Poids dans le bloc (%)",
     "DIVIDE ( [Score (%)], CALCULATE ( [Score (%)], ALLEXCEPT ( Candidats, Candidats[Bloc] ) ) )",
     "0.0 %", "05 Blocs politiques", "Part du candidat dans le total de son bloc."),
    ("Écart minimal 1er / 2e (pts)",
     "VAR _t = ADDCOLUMNS ( VALUES ( Hypotheses[Code] ), \"@e\",\n"
     "    CALCULATE ( [Écart 1er / 2e (pts)] ) )\n"
     "RETURN MINX ( _t, [@e] )",
     "0.0", "04 Écarts",
     "Avance la plus faible du candidat de tête sur son poursuivant, toutes hypothèses confondues."),
    ("Effet de l’offre resserrée (pts)",
     "VAR _trois = CALCULATE ( [Score (%)], ALL ( Hypotheses ),\n"
     "    Hypotheses[Configuration] = \"3 grands candidats\" )\n"
     "VAR _quatre = CALCULATE ( [Score (%)], ALL ( Hypotheses ),\n"
     "    Hypotheses[Configuration] = \"4 grands candidats\" )\n"
     "RETURN IF ( NOT ISBLANK ( _trois ) && NOT ISBLANK ( _quatre ),\n"
     "    ( _trois - _quatre ) * 100 )",
     "+0.0;-0.0;0.0", "04 Écarts",
     "Gain ou perte du candidat lorsque l'offre passe de quatre à trois grands candidats."),
    ("Hypothèses en tête",
     "COUNTROWS ( FILTER ( VALUES ( Hypotheses[Code] ), CALCULATE ( [Rang] ) = 1 ) ) + 0",
     "0", "03 Cadrage",
     "Nombre d'hypothèses dans lesquelles le candidat arrive en première position."),
    ("Candidat de référence",
     "IF ( HASONEVALUE ( Candidats[Candidat] ), SELECTEDVALUE ( Candidats[Candidat] ),\n"
     "    \"Jordan Bardella\" )",
     None, "08 Page profil",
     "Le candidat retenu, ou celui arrivé en tête si aucune sélection n'est faite."),
    ("Profil · score (%)",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0.0 %", "08 Page profil", "Score du candidat de référence."),
    ("Profil · amplitude (pts)",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Amplitude (pts)], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0.0", "08 Page profil", "Amplitude du candidat de référence."),
    ("Profil · premières places",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Hypothèses en tête], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0", "08 Page profil", "Premières places du candidat de référence."),
    ("Profil · écart au 1er (pts)",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Écart au 1er (pts)], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0.0", "08 Page profil", "Distance au candidat de tête, en points."),
    ("Profil · borne basse (%)",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Borne basse (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0.0 %", "08 Page profil", "Borne inférieure pour le candidat de référence."),
    ("Profil · borne haute (%)",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( [Borne haute (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )",
     "0.0 %", "08 Page profil", "Borne supérieure pour le candidat de référence."),
    ("Profil · écart à sa moyenne (pts)",
     "VAR _ref = [Candidat de référence]\n"
     "VAR _sc = CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )\n"
     "VAR _moy = CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref,\n"
     "    ALL ( Hypotheses ) )\n"
     "RETURN IF ( NOT ISBLANK ( _sc ), ( _sc - _moy ) * 100 )",
     "+0.0;-0.0;0.0", "08 Page profil",
     "Écart entre le score de l'hypothèse et la moyenne du candidat : montre où il "
     "sur-performe et où il décroche, y compris pour le candidat de tête."),
    ("Profil · couleur",
     "VAR _ref = [Candidat de référence]\n"
     "RETURN CALCULATE ( SELECTEDVALUE ( Candidats[Couleur] ), ALL ( Candidats ),\n"
     "    Candidats[Candidat] = _ref )",
     None, "08 Page profil", "Couleur de parti du candidat de référence."),
    ("Couleur du candidat",
     "SELECTEDVALUE ( Candidats[Couleur], \"#16324F\" )",
     None, "07 Mise en forme",
     "Code couleur du parti. Se branche sur « Format par > Valeur de champ » pour que "
     "chaque marque prenne la couleur de sa formation, quel que soit l'ordre de tri du visuel."),
    ("Score au classement (%)",
     "VAR _maxCandidat = CALCULATE ( [Score max (%)], ALL ( Hypotheses ) )\n"
     "RETURN IF ( _maxCandidat >= 0.05, [Score (%)] )",
     "0.0 %", "01 Intentions de vote",
     "Score restreint aux personnalités dépassant 5 % dans au moins une hypothèse : "
     "allège les visuels de flux, où treize séries deviennent illisibles."),
    ("Couleur du bloc",
     "SELECTEDVALUE ( Candidats[CouleurBloc], \"#16324F\" )",
     None, "07 Mise en forme",
     "Code couleur du bloc politique, pour les visuels agrégés par bloc."),
    ("Rang au classement",
     "IF ( NOT ISBLANK ( [Score au classement (%)] ), [Rang] )",
     "0", "03 Cadrage",
     "Rang du candidat dans l'hypothèse, restreint aux personnalités dépassant 5 % : "
     "sert d'axe au graphique de rangs."),
    ("Hypothèse sélectionnée",
     "SELECTEDVALUE ( Hypotheses[Intitulé],\n"
     "    \"Moyenne des \" & [Nb hypothèses] & \" hypothèses testées\" )",
     None, "06 Titres dynamiques", "Titre dynamique reprenant l'intitulé Ipsos."),
    ("Candidat sélectionné",
     "SELECTEDVALUE ( Candidats[Candidat], \"Ensemble des candidats testés\" )",
     None, "06 Titres dynamiques", "Titre dynamique de la page profil."),
    ("Note de lecture",
     "VAR _n = [Nb hypothèses]\n"
     "VAR _base = FORMAT ( [Base moyenne], \"#,0\", \"fr-FR\" )\n"
     "VAR _nsp = FORMAT ( [Sans intention exprimée (%)] * 100, \"0\", \"fr-FR\" )\n"
     "RETURN\n"
     "    IF ( _n = 1,\n"
     "        \"Base : \" & _base & \" personnes exprimées, \" & _nsp\n"
     "            & \" % des certains d’aller voter n’ont exprimé aucune intention\",\n"
     "        _n & \" hypothèses agrégées, base moyenne de \" & _base & \" personnes exprimées\" )",
     None, "06 Titres dynamiques", "Note de lecture affichée sous les visuels."),
    ("Étiquette avance",
     "VAR _e = [Écart 1er / 2e (pts)]\n"
     "RETURN IF ( ISBLANK ( _e ), \"n. d.\", \"+\" & FORMAT ( _e, \"0.0\", \"fr-FR\" ) )",
     None, "06 Titres dynamiques", "Avance du premier, formatée pour une carte."),
]


def table_mesures():
    L = ["/// Conteneur de mesures. Toute la logique d'analyse du sondage est ici.",
         "table Mesures", "\tlineageTag: %s" % lt(), ""]
    for nom, dax, fmt, folder, desc in MESURES:
        L.append("\t/// " + desc)
        if "\n" in dax:
            L.append("\tmeasure '%s' =" % nom)
            for ligne in dax.split("\n"):
                L.append("\t\t\t" + ligne)
        else:
            L.append("\tmeasure '%s' = %s" % (nom, dax))
        if fmt:
            L.append("\t\tformatString: %s" % fmt)
        L.append("\t\tdisplayFolder: %s" % folder)
        L.append("\t\tlineageTag: %s" % lt())
        L.append("")
    L.append("\tcolumn Filigrane")
    L.append("\t\tdataType: string")
    L.append("\t\tisHidden")
    L.append("\t\tlineageTag: %s" % lt())
    L.append("\t\tsummarizeBy: none")
    L.append("\t\tisNameInferred")
    L.append("\t\tsourceColumn: [Filigrane]")
    L.append("")
    L.append("\t\tannotation SummarizationSetBy = Automatic")
    L.append("")
    L.append("\tpartition Mesures = calculated")
    L.append("\t\tmode: import")
    L.append("\t\tsource = ROW ( \"Filigrane\", \"Ipsos bva pour Le Parisien\" )")
    L.append("")
    return "\n".join(L)


MODEL_TMDL = """model Model
\tculture: fr-FR
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: fr-FR
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation PBI_QueryOrder = ["CheminDonnees","Candidats","Hypotheses","Intentions"]

annotation PBI_ProTooling = ["DevMode"]

ref expression CheminDonnees

ref table Candidats
ref table Hypotheses
ref table Intentions
ref table Mesures

ref cultureInfo fr-FR
"""

EXPRESSIONS_TMDL = """/// Dossier contenant les trois fichiers CSV du projet.
/// Modifiez cette valeur pour pointer vers votre copie locale du dossier
/// « Presidentielle 2027 - Donnees », separateur final compris.
expression CheminDonnees = "{chemin}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
\tlineageTag: {lt}

\tannotation PBI_NavigationStepName = Navigation

\tannotation PBI_ResultType = Text

"""


RELATIONS_TMDL = """relationship {r1}
\tfromColumn: Intentions.Candidat
\ttoColumn: Candidats.Candidat

relationship {r2}
\tfromColumn: Intentions.Code
\ttoColumn: Hypotheses.Code
"""

CULTURE_TMDL = """cultureInfo fr-FR

\tlinguisticMetadata =
\t\t\t{
\t\t\t  "Version": "1.0.0",
\t\t\t  "Language": "fr-FR"
\t\t\t}

\t\tcontentType: json
"""


def ecrire_modele(racine, nom, chemins_csv):
    """racine : le dossier <Nom>.SemanticModel à écrire."""
    p_cand, p_hypo, p_int = chemins_csv
    sep = "\\" if "\\" in p_cand else "/"
    dossier = p_cand.rsplit(sep, 1)[0] + sep
    n_cand, n_hypo, n_int = (p.rsplit(sep, 1)[1] for p in (p_cand, p_hypo, p_int))
    d = os.path.join(racine, "definition")
    os.makedirs(os.path.join(d, "tables"), exist_ok=True)
    os.makedirs(os.path.join(d, "cultures"), exist_ok=True)
    os.makedirs(os.path.join(racine, ".pbi"), exist_ok=True)

    def W(p, c):
        with open(p, "w", encoding="utf-8") as f:
            f.write(c)

    W(os.path.join(racine, ".platform"),
      '{\n  "$schema": "https://developer.microsoft.com/json-schemas/fabric/'
      'gitIntegration/platformProperties/2.0.0/schema.json",\n'
      '  "metadata": {\n    "type": "SemanticModel",\n    "displayName": "%s"\n  },\n'
      '  "config": {\n    "version": "2.0",\n    "logicalId": "%s"\n  }\n}\n' % (nom, lt()))
    W(os.path.join(racine, "definition.pbism"),
      '{\n  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/'
      'semanticModel/definitionProperties/1.0.0/schema.json",\n'
      '  "version": "4.2",\n  "settings": {}\n}\n')
    W(os.path.join(d, "database.tmdl"), "database\n\tcompatibilityLevel: 1606\n\n")
    W(os.path.join(d, "model.tmdl"), MODEL_TMDL)
    W(os.path.join(d, "expressions.tmdl"),
      EXPRESSIONS_TMDL.format(chemin=dossier, lt=lt()))
    W(os.path.join(d, "relationships.tmdl"), RELATIONS_TMDL.format(r1=lt(), r2=lt()))
    W(os.path.join(d, "cultures", "fr-FR.tmdl"), CULTURE_TMDL)
    W(os.path.join(d, "tables", "Candidats.tmdl"), table_candidats(n_cand))
    W(os.path.join(d, "tables", "Hypotheses.tmdl"), table_hypotheses(n_hypo))
    W(os.path.join(d, "tables", "Intentions.tmdl"), table_intentions(n_int))
    W(os.path.join(d, "tables", "Mesures.tmdl"), table_mesures())
