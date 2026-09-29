# Les mesures DAX

Les 41 mesures du rapport vivent dans la table `Mesures`, qui ne contient aucune
donnée. Elles sont rangées en 8 dossiers d'affichage.

Ce fichier est un miroir de
`Presidentielle 2027.SemanticModel/definition/tables/Mesures.tmdl` : en cas de
divergence, c'est le fichier TMDL qui fait foi.

## 01 Intentions de vote

### `Score (%)`

Intention de vote en % des exprimés. Somme des scores du contexte courant,
moyennée sur les hypothèses sélectionnées : exacte pour une hypothèse, moyenne
des scénarios sinon.

```dax
Score (%) =
DIVIDE ( AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )
```

Format d'affichage : `0.0%`

### `Score max (%)`

Meilleur score obtenu parmi les hypothèses sélectionnées.

```dax
Score max (%) =
DIVIDE ( MAXX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )
```

Format d'affichage : `0.0%`

### `Score min (%)`

Score le plus bas parmi les hypothèses sélectionnées.

```dax
Score min (%) =
DIVIDE ( MINX ( VALUES ( Hypotheses[Code] ), CALCULATE ( SUM ( Intentions[Score] ) ) ), 100 )
```

Format d'affichage : `0.0%`

### `Amplitude (pts)`

Écart entre le meilleur et le moins bon score, en points : sensibilité à la configuration d'offre.

```dax
Amplitude (pts) =
VAR _max = [Score max (%)]
VAR _min = [Score min (%)]
RETURN IF ( NOT ISBLANK ( _max ), ( _max - _min ) * 100 )
```

Format d'affichage : `0.0`

### `Meilleur score mesuré (%)`

Score le plus élevé observé, tous candidats et toutes hypothèses sélectionnées confondus.

```dax
Meilleur score mesuré (%) =
DIVIDE ( MAXX ( ALLSELECTED ( Intentions ), Intentions[Score] ), 100 )
```

Format d'affichage : `0.0%`

### `Score au classement (%)`

Score restreint aux personnalités dépassant 5 % dans au moins une hypothèse :
allège les visuels de flux, où treize séries deviennent illisibles.

```dax
Score au classement (%) =
VAR _maxCandidat = CALCULATE ( [Score max (%)], ALL ( Hypotheses ) )
RETURN IF ( _maxCandidat >= 0.05, [Score (%)] )
```

Format d'affichage : `0.0%`

## 02 Précision statistique

### `Marge d’erreur (pts)`

Demi-intervalle de confiance à 95 % publié par Ipsos, en points.

```dax
Marge d’erreur (pts) =
AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( AVERAGE ( Intentions[Marge] ) ) )
```

Format d'affichage : `0.0`

### `Borne basse (%)`

Borne inférieure de l'intervalle de confiance à 95 %.

```dax
Borne basse (%) =
IF ( NOT ISBLANK ( [Score (%)] ), [Score (%)] - DIVIDE ( [Marge d’erreur (pts)], 100 ) )
```

Format d'affichage : `0.0%`

### `Borne haute (%)`

Borne supérieure de l'intervalle de confiance à 95 %.

```dax
Borne haute (%) =
IF ( NOT ISBLANK ( [Score (%)] ), [Score (%)] + DIVIDE ( [Marge d’erreur (pts)], 100 ) )
```

Format d'affichage : `0.0%`

### `Base exprimés`

Nombre de personnes ayant exprimé une intention de vote.

```dax
Base exprimés =
AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( MAX ( Hypotheses[Base] ) ) )
```

Format d'affichage : `#,0`

### `Sans intention exprimée (%)`

Part des personnes certaines d'aller voter n'ayant exprimé aucune intention.

```dax
Sans intention exprimée (%) =
DIVIDE ( AVERAGEX ( VALUES ( Hypotheses[Code] ), CALCULATE ( MAX (
Hypotheses[SansReponse] ) ) ), 100 )
```

Format d'affichage : `0.0%`

## 03 Cadrage

### `Nb hypothèses`

Nombre d'hypothèses de premier tour retenues dans le contexte.

```dax
Nb hypothèses =
DISTINCTCOUNT ( Hypotheses[Code] )
```

Format d'affichage : `0`

### `Nb candidats testés`

Nombre de personnalités présentes dans les hypothèses sélectionnées.

```dax
Nb candidats testés =
DISTINCTCOUNT ( Intentions[Candidat] )
```

Format d'affichage : `0`

### `Rang`

Rang du candidat dans le contexte, du score le plus élevé au plus faible.

```dax
Rang =
IF ( NOT ISBLANK ( [Score (%)] ),
    RANKX ( ALL ( Candidats[Candidat] ), [Score (%)],, DESC, DENSE ) )
```

Format d'affichage : `0`

### `Hypothèses en tête`

Nombre d'hypothèses dans lesquelles le candidat arrive en première position.

```dax
Hypothèses en tête =
COUNTROWS ( FILTER ( VALUES ( Hypotheses[Code] ), CALCULATE ( [Rang] ) = 1 ) ) + 0
```

Format d'affichage : `0`

### `Rang au classement`

Rang du candidat dans l'hypothèse, restreint aux personnalités dépassant 5 % :
sert d'axe au graphique de rangs.

```dax
Rang au classement =
IF ( NOT ISBLANK ( [Score au classement (%)] ), [Rang] )
```

Format d'affichage : `0`

## 04 Écarts

### `Score du 1er (%)`

Score du candidat arrivé en tête.

```dax
Score du 1er (%) =
VAR _t = ADDCOLUMNS ( ALLSELECTED ( Candidats[Candidat] ), "@s", [Score (%)] )
RETURN MAXX ( _t, [@s] )
```

Format d'affichage : `0.0%`

### `Score du 2e (%)`

Meilleur score hors candidat de tête.

```dax
Score du 2e (%) =
VAR _t = ADDCOLUMNS ( ALLSELECTED ( Candidats[Candidat] ), "@s", [Score (%)] )
VAR _top = MAXX ( _t, [@s] )
RETURN MAXX ( FILTER ( _t, [@s] < _top ), [@s] )
```

Format d'affichage : `0.0%`

### `Écart 1er / 2e (pts)`

Avance du candidat de tête sur son premier poursuivant, en points.

```dax
Écart 1er / 2e (pts) =
( [Score du 1er (%)] - [Score du 2e (%)] ) * 100
```

Format d'affichage : `0.0`

### `Écart au 1er (pts)`

Retard du candidat sur celui arrivé en tête, en points.

```dax
Écart au 1er (pts) =
IF ( NOT ISBLANK ( [Score (%)] ), ( [Score (%)] - [Score du 1er (%)] ) * 100 )
```

Format d'affichage : `0.0`

### `Écart minimal 1er / 2e (pts)`

Avance la plus faible du candidat de tête sur son poursuivant, toutes hypothèses confondues.

```dax
Écart minimal 1er / 2e (pts) =
VAR _t = ADDCOLUMNS ( VALUES ( Hypotheses[Code] ), "@e",
    CALCULATE ( [Écart 1er / 2e (pts)] ) )
RETURN MINX ( _t, [@e] )
```

Format d'affichage : `0.0`

### `Effet de l’offre resserrée (pts)`

Gain ou perte du candidat lorsque l'offre passe de quatre à trois grands candidats.

```dax
Effet de l’offre resserrée (pts) =
VAR _trois = CALCULATE ( [Score (%)], ALL ( Hypotheses ),
    Hypotheses[Configuration] = "3 grands candidats" )
VAR _quatre = CALCULATE ( [Score (%)], ALL ( Hypotheses ),
    Hypotheses[Configuration] = "4 grands candidats" )
RETURN IF ( NOT ISBLANK ( _trois ) && NOT ISBLANK ( _quatre ),
    ( _trois - _quatre ) * 100 )
```

Format d'affichage : `+0.0;-0.0;0.0`

## 05 Blocs politiques

### `Total extrême droite (%)`

Total des candidats d'extrême droite présents dans l'hypothèse.

```dax
Total extrême droite (%) =
CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Bloc] = "Extrême droite" )
```

Format d'affichage : `0.0%`

### `Total gauche (%)`

Total des candidats de gauche et écologistes.

```dax
Total gauche (%) =
CALCULATE ( [Score (%)], ALL ( Candidats ),
    Candidats[Bloc] IN { "Gauche radicale", "Gauche et écologistes" } )
```

Format d'affichage : `0.0%`

### `Total centre et droite (%)`

Total du centre et de la droite républicaine.

```dax
Total centre et droite (%) =
CALCULATE ( [Score (%)], ALL ( Candidats ),
    Candidats[Bloc] IN { "Centre", "Droite" } )
```

Format d'affichage : `0.0%`

### `Poids dans le bloc (%)`

Part du candidat dans le total de son bloc.

```dax
Poids dans le bloc (%) =
DIVIDE ( [Score (%)], CALCULATE ( [Score (%)], ALLEXCEPT ( Candidats, Candidats[Bloc] ) ) )
```

Format d'affichage : `0.0%`

## 06 Titres dynamiques

### `Hypothèse sélectionnée`

Titre dynamique reprenant l'intitulé Ipsos.

```dax
Hypothèse sélectionnée =
SELECTEDVALUE ( Hypotheses[Intitule],
    "Moyenne des " & [Nb hypothèses] & " hypothèses testées" )
```

### `Candidat sélectionné`

Titre dynamique de la page profil.

```dax
Candidat sélectionné =
SELECTEDVALUE ( Candidats[Candidat], "Ensemble des candidats testés" )
```

### `Note de lecture`

Note de lecture affichée sous les visuels.

```dax
Note de lecture =
VAR _n = [Nb hypothèses]
VAR _base = FORMAT ( [Base exprimés], "#,0", "fr-FR" )
VAR _nsp = FORMAT ( [Sans intention exprimée (%)] * 100, "0", "fr-FR" )
RETURN
    IF ( _n = 1,
        "Base : " & _base & " personnes exprimées, " & _nsp
            & " % des certains d’aller voter n’ont exprimé aucune intention",
        _n & " hypothèses agrégées, base moyenne de " & _base & " personnes exprimées" )
```

### `Étiquette avance`

Avance du premier, formatée pour une carte.

```dax
Étiquette avance =
VAR _e = [Écart 1er / 2e (pts)]
RETURN IF ( ISBLANK ( _e ), "n. d.", "+" & FORMAT ( _e, "0.0", "fr-FR" ) )
```

## 07 Mise en forme

### `Couleur du candidat`

Code couleur du parti. Se branche sur « Format par > Valeur de champ » pour
que chaque marque prenne la couleur de sa formation, quel que soit l'ordre de
tri du visuel.

```dax
Couleur du candidat =
SELECTEDVALUE ( Candidats[Couleur], "#16324F" )
```

### `Couleur du bloc`

Code couleur du bloc politique, pour les visuels agrégés par bloc.

```dax
Couleur du bloc =
SELECTEDVALUE ( Candidats[CouleurBloc], "#16324F" )
```

## 08 Page profil

### `Candidat de référence`

Le candidat retenu, ou celui arrivé en tête si aucune sélection n'est faite.

```dax
Candidat de référence =
IF ( HASONEVALUE ( Candidats[Candidat] ), SELECTEDVALUE ( Candidats[Candidat] ),
    "Jordan Bardella" )
```

### `Profil · score (%)`

Score du candidat de référence.

```dax
Profil · score (%) =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0.0%`

### `Profil · amplitude (pts)`

Amplitude du candidat de référence.

```dax
Profil · amplitude (pts) =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Amplitude (pts)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0.0`

### `Profil · premières places`

Premières places du candidat de référence.

```dax
Profil · premières places =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Hypothèses en tête], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0`

### `Profil · écart au 1er (pts)`

Distance au candidat de tête, en points.

```dax
Profil · écart au 1er (pts) =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Écart au 1er (pts)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0.0`

### `Profil · borne basse (%)`

Borne inférieure pour le candidat de référence.

```dax
Profil · borne basse (%) =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Borne basse (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0.0%`

### `Profil · borne haute (%)`

Borne supérieure pour le candidat de référence.

```dax
Profil · borne haute (%) =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Borne haute (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Format d'affichage : `0.0%`

### `Profil · écart à sa moyenne (pts)`

Écart entre le score de l'hypothèse et la moyenne du candidat : montre où il
sur-performe et où il décroche, y compris pour le candidat de tête.

```dax
Profil · écart à sa moyenne (pts) =
VAR _ref = [Candidat de référence]
VAR _sc = CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )
VAR _moy = CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref,
    ALL ( Hypotheses ) )
RETURN IF ( NOT ISBLANK ( _sc ), ( _sc - _moy ) * 100 )
```

Format d'affichage : `+0.0;-0.0;0.0`

### `Profil · couleur`

Couleur de parti du candidat de référence.

```dax
Profil · couleur =
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( SELECTEDVALUE ( Candidats[Couleur] ), ALL ( Candidats ),
    Candidats[Candidat] = _ref )
```
