# Choix de conception

Ce fichier documente les partis pris du rapport et les pièges rencontrés en
chemin. Il sert autant de mémoire technique que de justification des écarts avec
un rapport Power BI ordinaire.

---

## 1. Le rapport est généré, pas dessiné

Les sept pages, les soixante-sept visuels, le modèle et les fichiers CSV sont
produits par cinq modules Python. On ne déplace pas un visuel à la souris : on
change une coordonnée dans `pbuild_pages.py` et on regénère.

Ce que cela apporte :

- La mise en page obéit à une grille unique définie une seule fois
  (`pbuild_core.py`), donc les marges et les hauteurs sont identiques d'une page
  à l'autre au pixel près.
- Une correction de valeur se fait dans `pdata.py`, qui est la source unique de
  vérité, et se propage aux CSV, au modèle et aux commentaires des visuels.
- Le projet se relit dans une revue de code comme n'importe quel dépôt.

Le coût : il faut connaître le schéma JSON du format PBIR et la grammaire TMDL,
qui sont peu documentés et qui refusent silencieusement ce qu'ils ne
comprennent pas.

---

## 2. Les titres énoncent la conclusion

Un titre comme « Répartition des intentions de vote » décrit un graphique. Un
titre comme « Dans les huit hypothèses testées, le Rassemblement national arrive
en tête » énonce un résultat vérifiable.

Les six pages portent un titre affirmatif et le visuel placé en dessous fournit
la preuve. Le fil de progression en pied de page rappelle l'étape courante, ce
qui transforme une collection de pages en démonstration ordonnée.

---

## 3. Aucune zone de texte décorative

Première version : les titres, les filets et les cartouches étaient des zones de
texte posées sur les graphiques. Résultat, 194 visuels, des textes rognés et des
carrés dorés parasites.

La cause tient à une règle de Power BI : une zone de texte impose une hauteur
minimale et une marge interne que l'on ne peut pas réduire. Un filet de deux
pixels devient donc un bloc de vingt pixels.

Version retenue : les titres, sous-titres, arrière-plans, bordures et ombres
sont des propriétés natives du conteneur du visuel
(`visualContainerObjects`). Le nombre de visuels est tombé à soixante-sept, les
textes ne sont plus rognés, et le rapport se charge plus vite.

Il reste cinq à huit zones de texte par page, et elles portent toutes du
contenu réel : le fond du bandeau, le titre de page, le cartouche de droite,
les blocs de prose et le pied de page.

À noter : la propriété `border` n'accepte que `show`, `color` et `radius`.
Ajouter `weight` fait rejeter le fichier par le schéma, avec un message qui ne
nomme pas le visuel fautif.

---

## 4. La palette est politique, pas décorative

Chaque candidat porte la couleur de sa formation. Deux contraintes s'opposent :
respecter la couleur du parti, et garder treize couleurs distinguables.

Les couleurs ont été contrôlées deux à deux par écart perceptuel. Le cas limite
était Attal et Philippe, qui partaient à un écart de 6,6, en dessous du seuil de
lisibilité. Philippe a été déplacé vers un turquoise foncé, ce qui reste
défendable pour Horizons et rend les deux barres immédiatement séparables.

---

## 5. La couleur pilotée par mesure et sa limite

Les visuels sans série sont colorés par les mesures `Couleur du candidat` et
`Couleur du bloc`, en mise en forme conditionnelle. Le sélecteur générique sur
les points de données est indispensable, faute de quoi la règle est acceptée
mais ignorée.

La limite est nette : **dès qu'un visuel porte une série, Power BI ignore la
mise en forme conditionnelle** et distribue les couleurs du thème dans l'ordre
d'apparition des séries.

Pire : quand une règle conditionnelle est déclarée sur un visuel à série, Power
BI n'ignore pas seulement la règle, il abandonne aussi la palette du thème et
retombe sur sa palette par défaut. Le défaut ne se voit pas dans les fichiers de
définition, seulement à l'écran ou sur un export PDF du rapport.

Deux visuels sont concernés, les colonnes groupées de la page 02 et le graphique
de pente de la page 03. Ils n'affichent que les personnalités dépassant 5 %. La
parade tient en deux gestes :

1. Ne pas déclarer de règle conditionnelle sur ces deux visuels. Sans règle, la
   palette du thème s'applique normalement.
2. Ordonner le tableau `dataColors` du thème pour que ces neuf personnalités
   viennent en tête, dans leur ordre d'apparition. C'est ce que fait la fonction
   `_couleurs_theme` de `pbuild.py`.

Un graphique en ruban avait été essayé pour la page 02. Il a été abandonné : un
ruban trie ses séries par valeur, donc l'ordre d'apparition change d'une colonne
à l'autre et aucune préparation du thème ne tient.

---

## 6. Barres groupées plutôt que barres empilées

Le type `barChart` est empilé. Il n'autorise que les positions d'étiquette
internes, ce qui écrase les chiffres sur les barres courtes.

Le type `clusteredBarChart` accepte `OutsideEnd`. Les treize pourcentages du
classement de la page 01 sortent donc à droite de leur barre, en couleur de
parti, lisibles même sur les scores à 1 %.

---

## 7. Deux pièges DAX

**`RANKX` et `ALLSELECTED`.** Dans un visuel à série, `ALLSELECTED (
Candidats[Candidat] )` ne voit que le membre courant de la série : le rang
calculé vaut 1 partout. Il faut `ALL ( Candidats[Candidat] )`.

**Une mesure dans un prédicat `CALCULATE`.** `CALCULATE ( [Score (%)], ALL (
Candidats ), Candidats[Candidat] = [Candidat de référence] )` est refusé par le
moteur, avec le message peu parlant « un ou plusieurs champs présentent un
problème ». La forme correcte passe par une variable :

```dax
VAR _ref = [Candidat de référence]
RETURN CALCULATE ( [Score (%)], ALL ( Candidats ), Candidats[Candidat] = _ref )
```

Les huit mesures `Profil · ...` de la page 04 suivent toutes cette forme.

---

## 8. Les garde-fous du générateur

Trois contrôles s'exécutent à chaque génération et échouent bruyamment.

**Barre de défilement.** Un graphique à barres a besoin d'au moins vingt pixels
par catégorie, un graphique à colonnes d'au moins vingt-six. En dessous, Power
BI ajoute une barre de défilement et ampute le visuel. Le contrôle compare la
hauteur disponible au nombre de catégories et signale le visuel par son titre.

**Prose trop longue.** Un estimateur calcule le nombre de caractères par ligne à
partir de la largeur du cadre et de la taille de police, puis la hauteur totale
du bloc. Si le texte dépasse son cadre, la génération le signale avant que
quiconque ouvre le rapport.

Les seuils des deux premiers contrôles ont été recalés sur un export PDF du
rapport : l'estimation théorique était trop optimiste, et trois visuels
affichaient une barre de défilement alors que la génération ne signalait rien.
Le minimum est passé à trente pixels par catégorie, et l'interligne estimé de
1,62 à 1,80 fois la taille de police.

**Apostrophes dans les noms TMDL.** Un nom délimité par des apostrophes simples
ne peut pas contenir d'apostrophe droite : `measure 'Marge d'erreur (pts)'` fait
échouer le chargement du modèle avec une erreur `InvalidLineType` qui ne désigne
pas la ligne fautive. Les noms concernés utilisent l'apostrophe typographique, et
une expression régulière vérifie chaque ligne de déclaration avant l'écriture.

---

## 9. Le nettoyage des visuels orphelins

Le format PBIR range chaque visuel dans son propre dossier. Régénérer un rapport
avec moins de visuels qu'avant laisse donc des dossiers orphelins, que Power BI
charge quand même.

Le générateur compare la liste attendue à ce qui est sur le disque et déplace
les restes dans un dossier de rebut. Il les déplace au lieu de les supprimer,
parce que l'environnement de génération peut ne pas avoir le droit d'effacer
dans le dossier cible.

---

## 10. La page d'info-bulle

Une septième page de 320 x 240 pixels porte `pageBinding` de type `Tooltip` et
la visibilité `HiddenInViewMode`. Elle est exclue de l'ordre des pages, donc
invisible dans la barre d'onglets, et s'affiche au survol des graphiques du
classement.

Elle montre le score moyen, l'amplitude, le nombre de premières places et le
profil par hypothèse du candidat survolé. C'est le seul endroit du rapport où un
détail candidat par candidat apparaît sans quitter la page courante.

---

## 11. Ce que la relecture d'un export a corrigé

Les fichiers de définition peuvent être parfaitement valides et le rendu être
mauvais. Un export PDF des six pages a révélé six défauts invisibles autrement :

- les séries des pages 02 et 03 affichaient la palette par défaut de Power BI au
  lieu des couleurs de parti, pour la raison expliquée en section 5 ;
- trois visuels portaient une barre de défilement et coupaient du contenu, dont
  le dernier candidat d'un classement à treize lignes ;
- la légende du graphique de pente tronquait les noms et débordait ;
- le graphique des effets de l'offre n'affichait que trois étiquettes sur treize,
  parce qu'un graphique à colonnes empilées n'accepte que des étiquettes
  intérieures ;
- quatre en-têtes de colonnes sortaient en notation technique, du type
  `SansReponse` ou `FinalisteRN` ;
- les pourcentages s'affichaient collés au signe, contrairement à l'usage
  typographique français.

Chacun de ces points a été corrigé dans le générateur, pas dans les fichiers
produits : la correction survit à la prochaine génération.
