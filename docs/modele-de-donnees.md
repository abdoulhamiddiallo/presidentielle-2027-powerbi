# Le modèle de données

Schéma en étoile classique : une table de faits au centre, deux dimensions
autour, une table de mesures sans données. Aucune relation bidirectionnelle,
aucune colonne calculée, aucune table calculée. Tout le calcul est dans les
mesures.

```text
                 Candidats                Hypotheses
              (13 lignes, dim.)        (8 lignes, dim.)
                      |                        |
                      | 1                      | 1
                      |                        |
                      *                        *
                 Intentions[Candidat]   Intentions[Code]
                            \            /
                             Intentions
                          (84 lignes, faits)

                    Mesures  (table de calcul, 0 colonne)
```

---

## Table `Candidats`

Référentiel des treize personnalités testées. Une ligne par personnalité.

| Colonne | Type | Visible | Tri | Rôle |
|---|---|---|---|---|
| `Candidat` | texte | oui | par `Ordre` | Nom complet, clé de la relation |
| `NomCourt` | texte | oui | par `Ordre` | Nom de famille seul, pour les axes étroits |
| `Parti` | texte | oui | naturel | Formation politique de rattachement |
| `Bloc` | texte | oui | par `OrdreBloc` | Regroupement en cinq blocs |
| `OrdreBloc` | entier | non | naturel | Rang du bloc, de la gauche vers la droite |
| `Ordre` | entier | non | naturel | Rang du candidat, de la gauche vers la droite |
| `Couleur` | texte | non | naturel | Code hexadécimal du parti |
| `CouleurBloc` | texte | non | naturel | Code hexadécimal du bloc |

Les cinq blocs sont : gauche radicale, gauche et écologistes, centre, droite,
extrême droite.

Le tri par `Ordre` est un choix de fond. Un axe alphabétique placerait Arthaud
avant Zemmour et détruirait la lecture politique. L'ordre retenu reproduit celui
du rapport publié, de la gauche vers la droite.

Les deux colonnes de couleur permettent de colorer un visuel par une mesure
plutôt que point par point. Le rapport utilise pour cela `Couleur du candidat`
et `Couleur du bloc`, appliquées en mise en forme conditionnelle avec un
sélecteur générique sur les points de données.

---

## Table `Hypotheses`

Les huit configurations d'offre testées. Une ligne par hypothèse.

| Colonne | Type | Visible | Tri | Rôle |
|---|---|---|---|---|
| `Code` | texte | oui | par `Ordre` | Identifiant court, H1 à H8, clé de la relation |
| `Hypothese` | texte | oui | par `Ordre` | Libellé court listant les grands candidats |
| `Intitule` | texte | oui | naturel | Intitulé complet tel qu'imprimé dans le rapport |
| `Base` | entier | oui | naturel | Nombre de personnes exprimant une intention |
| `SansReponse` | décimal | oui | naturel | Part des certains d'aller voter sans intention exprimée |
| `NbCandidats` | entier | oui | naturel | Nombre de candidats présents dans l'hypothèse |
| `FinalisteRN` | texte | oui | naturel | Candidat du Rassemblement national testé |
| `CandidatGauche` | texte | oui | naturel | Candidat social-démocrate testé |
| `Configuration` | texte | oui | par `OrdreConfig` | Quatre ou trois grands candidats face au RN |
| `OrdreConfig` | entier | non | naturel | Rang de la configuration |
| `Ordre` | entier | non | naturel | Rang de l'hypothèse, H1 à H8 |

`Configuration` est la colonne qui porte la démonstration de la page 03. Elle
oppose les quatre hypothèses où Attal et Philippe sont présents ensemble aux
quatre hypothèses où une seule des deux personnalités reste en lice.

`Base` et `SansReponse` alimentent la page 06. Elles rappellent que la base
exprimée varie de 1 037 à 1 079 personnes et que la part sans intention exprimée
monte de 7 à 11 % quand l'offre se resserre.

---

## Table `Intentions`

Table de faits. Une ligne par couple candidat et hypothèse, soit quatre-vingt-
quatre lignes. Toutes les colonnes sont masquées : on n'interroge jamais cette
table directement, seulement par les mesures.

| Colonne | Type | Rôle |
|---|---|---|
| `Code` | texte | Clé vers `Hypotheses` |
| `Candidat` | texte | Clé vers `Candidats` |
| `Score` | décimal | Intention de vote en % des suffrages exprimés |
| `Marge` | décimal | Demi-amplitude de l'intervalle de confiance à 95 %, en points |

Le tableau n'est pas complet au sens cartésien : treize candidats fois huit
hypothèses feraient cent quatre lignes. Il en manque vingt parce qu'un candidat
absent d'une hypothèse n'y a pas de score. Cette absence est porteuse de sens et
le rapport la montre comme telle : une cellule vide dans la matrice de la page
02 signale un candidat non testé, pas un score nul.

---

## Table `Mesures`

Table de calcul sans aucune colonne, créée uniquement pour héberger les
quarante et une mesures. Elle apparaît en tête du volet de données grâce au
préfixe numérique de ses dossiers d'affichage.

Ce découpage a un intérêt pratique : les mesures ne sont attachées à aucune
table de données, donc renommer ou restructurer `Intentions` ne déplace aucune
mesure.

Le détail des mesures figure dans [`mesures-dax.md`](mesures-dax.md).

---

## Relations

| De | Vers | Cardinalité | Direction du filtre | Active |
|---|---|---|---|---|
| `Intentions[Candidat]` | `Candidats[Candidat]` | plusieurs vers un | simple | oui |
| `Intentions[Code]` | `Hypotheses[Code]` | plusieurs vers un | simple | oui |

Les deux dimensions filtrent la table de faits, jamais l'inverse. C'est ce qui
permet à la mesure `Score (%)` de moyenner proprement sur les hypothèses du
contexte : `VALUES ( Hypotheses[Code] )` renvoie exactement les hypothèses
visibles après filtrage.

---

## Alimentation

Les trois tables sont chargées en mode import depuis trois fichiers CSV, encodés
en UTF-8 avec BOM et séparés par des points-virgules. Le dossier qui les contient
est porté par le paramètre Power Query `CheminDonnees`, défini dans
`Presidentielle 2027.SemanticModel/definition/expressions.tmdl`.

Chaque partition suit la même forme :

```text
let
    Source = Csv.Document(
        File.Contents(CheminDonnees & "Candidats.csv"),
        [Delimiter=";", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Entetes = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Entetes, { ... }, "en-US")
in
    Types
```

Le typage utilise la culture `en-US` parce que les fichiers CSV écrivent les
décimales avec un point. Le modèle, lui, est en culture `fr-FR` : les nombres
s'affichent avec une virgule dans le rapport.

Les fichiers CSV ne sont pas la source primaire. Ils sont produits par
`pbuild_model.py` à partir de `pdata.py`, qui contient les valeurs extraites du
rapport publié. Pour corriger une valeur, on modifie `pdata.py` et on regénère.
