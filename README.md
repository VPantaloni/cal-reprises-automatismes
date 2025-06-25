
# 🧠 *Calendrier de reprises* 
## Outil de planification des automatismes mathématiques en 6e

Cet outil (appli StreamLit) permet aux enseignants de cycle 3 de construire une **grille annuelle de réactivation des automatismes** en lien avec la courbe d’Ebbinghaus, à partir d’un fichier CSV listant les automatismes.

## Fichiers utiles
Fabrication d'une appli StreamLit qui appelle `app.py`

https://cal-reprises-automatismes-6e.streamlit.app/

* app.py 
Mise en forme générale
* selection_algo.py
algo de répartition des automatismes
* volet2.py
Mise en forme de la 2e page avec liste des textes des automatismes
* Auto-6e.csv
Fichier source appelé avec la liste des automatismes et codes (Deux colonnes)

#### Les autres fichiers sont des versions antérieures en backup.

### 🎨 Légende des thèmes par couleur et icones pour une vue compacte.

<div style="display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.9em">
  <div style="background:#ac2747; color:white; border-radius:5px; padding:4px">🔢 Nombres entiers et décimaux</div>
  <div style="background:#be5770; color:white; border-radius:5px; padding:4px">➗ Fractions</div> 
  <div style="background:#cc6c1d; color:white; border-radius:5px; padding:4px">📏 Longueurs</div>
  <div style="background:#d27c36; color:white; border-radius:5px; padding:4px">🔷 Aires</div>
  <div style="background:#dd9d68; color:white; border-radius:5px; padding:4px">⌚ Temps</div>
  <div style="background:#16a34a; color:white; border-radius:5px; padding:4px">📐 Configurations planes</div>
  <div style="background:#44b56e; color:white; border-radius:5px; padding:4px">🧊 Espace</div>
  <div style="background:#1975d1; color:white; border-radius:5px; padding:4px">📊 Données</div>
  <div style="background:#3384d6; color:white; border-radius:5px; padding:4px">🎲 Probabilités</div>
  <div style="background:#8a38d2; color:white; border-radius:5px; padding:4px">∝ Proportionnalité</div>
</div>


### Vue 1 - par semaine : Quels automatismes travailler ?
![](https://minio.apps.education.fr/codimd-prod/uploads/73b879dd9cda4adb9b99f77b1.png)
### Vue 2 - Par automatisme : dates des reprises ?
![](https://minio.apps.education.fr/codimd-prod/uploads/73b879dd9cda4adb9b99f77b2.png)


---

## 📌 Principes de fonctionnement

- 32 semaines, réparties en 8 colonnes × 4 lignes.
- Pour chaque semaine, on choisit le **thème** principal travaillé cette semaine à l’aide d’un bouton.
- Une fois le thème choisi, l’outil sélectionne **6 automatismes** à revoir cette semaine.
- L’algorithme :
  - privilégie l'espacement des reprises, en lien avec la courbe d’Ebbinghaus,
  - respecte l’ordre logique des notions au sein de chaque thème,
  - garantit que tous les automatismes soient vus **au moins 3 fois** (ou 2 si c’est un rappel ↩ des années antérieures),
  - diversifie les thèmes chaque semaine (au moins 3).

---

## 🧭 Interface utilisateur

- **❓ Choix du thème** : bouton par semaine, icônes thématiques à sélectionner.
- **Automatismes affichés** : 6 par semaine, organisés en 2 colonnes.
- **Survol** : affiche l’objectif complet.
- **Lecture par automatisme** : liste en bas avec le code, le texte, et les semaines où il est placé.
- **Réinitialiser** : supprime tous les choix.
- **Remplir aléatoirement** : propose un thème différent chaque semaine (sans doublon).
- **Téléchargement Excel** : export de la grille + liste par automatisme.

---



---

## 📤 Export

- L’export Excel contient deux feuilles :
  - **Grille** : Semaine, Thème, Auto1 à Auto6
  - **Lecture par automatisme** : Code, Objectif, Semaine(s)



---

## 🗂 Personnalisation : changer le fichier CSV

Fichier `Objectifs-6e-CM2-Auto-4.csv` au format UTF8 `;` avec les colonnes suivantes :

- `Code`,  `Automatisme`

### Contenu du fichier csv :

| Code | Description |
|------|-------------|
| 🔢↩1 | Savoir effectuer un calcul contenant des parenthèses. |
| 🔢↩2 | Multiplier un nombre décimal par 10, 100 ou 1 000 |
| 🔢↩3 | Résoudre des problèmes additifs en une ou plusieurs étapes (CM2). |
| 🔢🛠1 | L'élève restitue de manière automatique les résultats suivants, relatifs aux relations entre 1/1000, 1/100, 1/10 et 1 : 1 = 10/10 = 100/100 = 1000/1000 ; 1/10 = 10/100 = 100/1000 ; 1/100 = 10/1000 ; 1 = 10 x 1/10 = 100 x 1/100 ; 1/10 = 10 x 1/100. |
| 🔢🛠2 | L’élève restitue de manière automatique les équivalences d’écriture suivantes : 1/10=0,1; 1/100=0,01; 1/1000=0,001. |
| 🔢🛠3 | L’élève passe de manière automatique d’une écriture sous forme de fraction décimale ou de somme de fractions décimales à une écriture décimale, et inversement. |
| 🔢🛠4 | L’élève applique de manière automatique la procédure de multiplication d’un nombre décimal par 1, par 10, par 100 ou par 1 000, en lien avec la numération. |
| 🔢🛠5 | L'élève applique de manière automatique la procédure de division d'un nombre décimal par 1, par 10, par 100 ou par 1000. |
| ➗↩1 | Savoir interpréter, représenter, écrire et lire des fractions |
| ➗↩2 | Interpréter, représenter, écrire et lire des fractions. |
| ➗↩3 | Écrire une fraction supérieure à 1 comme la somme d’un entier et d’une fraction inférieure à 1 (CM2). |
| ➗↩4 | Écrire la somme d’un entier et d’une fraction inférieure à 1 comme une unique fraction (CM2). |
| ➗↩5 | Encadrer une fraction entre deux nombres entiers consécutifs (CM2). |
| ➗🛠1 | L'élève sait reconnaître une fraction sur des représentations variées. |
| ➗🛠2 | L'élève connaît des relations entre 1/4, 1/2, 3/4 et 1, et complète de manière automatique des « égalités à trous » du type : 1/2 + 1/2 = ... ; 1/4 + 1/4 = ... ; 1 - 1/4 = ... ; 1/2 + 1/4 = ... ; 1 - 1/2 = ... ; 3/4 + 1/4 = ... ; 1/2 - 1/4 = ... ; 3/4 - 1/4 = .... |
| ➗🛠3 | L'élève sait passer de manière automatique d'une écriture fractionnaire à une écriture décimale, et inversement, dans les cas suivants : 1/4 = 0,25 ; 1/2 = 0,5 ; 3/4 = 0,75 ; 3/2 = 1,5 ; 3/2 = 2 ; 3/2 = 2,5. |
| ➗🛠4 | Les notions de diviseur et de multiple et les tables de multiplication sont réactivées en vue de leur utilisation dans le calcul sur les fractions (simplification, addition et soustraction). |
| ➗🛠5 | L'élève sait calculer 2/3 de 12 œufs, 3/4 de 10 m. |
| 📏🛠1 | L'élève connaît les significations des préfixes allant du kilo- au milli-, ainsi que les relations entre le mètre, ses multiples et ses sous-multiples, et fait le lien avec les unités de numération du système décimal. |
| 📏🛠2 | L'élève connaît les relations entre deux unités successives du système décimal, par exemple : 1 dm = 10 cm et 1 cm = 1/10 dm = 0,1 dm. |
| 📏🛠3 | L'élève sait convertir en mètre une longueur donnée dans une autre unité, multiple ou sous-multiple du mètre. Inversement, l'élève sait convertir dans une unité donnée une longueur exprimée en mètre. |
| 📏🛠4 | L'élève sait utiliser le compas comme outil de report de longueurs. |
| 📏🛠5 | Il sait que le périmètre d'une figure plane est la longueur de son contour. L'élève sait calculer le périmètre d'un carré et d'un rectangle. |
| 🔷↩1 | Comparer les aires de différentes figures planes (CM2). |
| 🔷↩2 | Déterminer des aires (CM2). |
| 🔷🛠1 | L'élève sait comparer des aires sans avoir recours à la mesure, par superposition ou par découpage et recollement de surfaces. |
| 🔷🛠2 | L'élève sait que 1 cm est l'aire d'un carré de 1 cm de côté, que 1 m est l'aire d'un carré de 1 m de côté, que 1 dm est l'aire d'un carré de 1 dm de côté. |
| 🔷🛠3 | Dans des cas simples, l'élève sait déterminer l'aire d'une surface en s'appuyant sur un quadrillage composé de carreaux dont les côtés mesurent 1 cm. |
| 🔷🛠4 | L'élève sait que : 1 m = 1 m x 1 m = 10 dm x 10 dm = 10 x 10 dm = 100 dm ; 1 dm = 1 dm x 1 dm = 10 cm x 10 cm = 10 x 10 cm = 100 cm. |
| 🔷🛠5 | L'élève mémorise que 1 cm est égal à un centième de 1 dm, qu'il écrit 1 cm = 1/100 dm ou 1 cm = 0,01 dm. |
| 🔷🛠6 | L'élève mémorise que 1 dm est égal à un centième de 1 m, qu'il écrit 1 dm = 1/100 m ou 1 dm = 0,01 m. |
| ⌚🛠1 | L'élève lit l'heure sur un cadran à aiguilles ou sur un affichage digital (heures, minutes et secondes). |
| ⌚🛠2 | L'élève place les aiguilles pour qu'une horloge indique une heure donnée. |
| ⌚🛠3 | L'élève connaît les unités de mesure de durées jour, heure, minute et seconde et les relations qui les lient. |
| ⌚🛠4 | L'élève sait combien de jours il y a dans une année (bissextile ou non), combien d'années il y a dans un siècle, et dans un millénaire. |
| ⌚🛠5 | L'élève sait qu'une demi-heure c'est 30 minutes, qu'un quart d'heure c'est 15 minutes, que trois quarts d'heure c'est 45 minutes. |
| 📐↩1 | Utiliser le vocabulaire géométrique approprié dans le contexte d’apprentissage des notions correspondantes (CM2). |
| 📐↩2 | Utiliser les outils géométriques usuels : règle, règle graduée, équerre et compas (CM2). |
| 📐↩3 | Connaître les notations et les codes usuels utilisés en géométrie (CM2). |
| 📐↩4 | Reconnaître et utiliser la notion de perpendicularité (CM2). |
| 📐↩5 | Reconnaître et utiliser la notion de parallélisme (CM2) |
| 📐↩6 | Construire une figure géométrique composée de segments, de droites, de polygones usuels et de cercles. |
| 📐↩7 | Reconnaître et nommer les figures suivantes en s’appuyant sur leur définition : triangle, triangle rectangle, triangle isocèle, triangle équilatéral, quadrilatère, carré, rectangle, losange, trapèze, trapèze rectangle, pentagone et hexagone (CM2). |
| 📐↩8 | Connaître les propriétés de parallélisme des côtés opposés, des égalités de longueurs et d’angles pour les figures usuelles : triangle rectangle, triangle isocèle, triangle équilatéral, carré, rectangle, losange, trapèze et trapèze rectangle (CM2). |
| 🧊↩1 | Nommer un cube, une boule, un pavé, un cône, une pyramide, un cylindre ou un prisme droit (CM2). |
| 🧊↩2 | Décrire un cube, un pavé, une pyramide ou un prisme droit en faisant référence à des propriétés et en utilisant le vocabulaire approprié (CM2). |
| 🧊🛠1 | L'élève identifie dans un ensemble de solides lesquels sont des pyramides, des boules, des cubes, des cylindres, des pavés, des cônes ou des prismes droits. |
| 📊🛠1 | L'élève sait lire un tableau, un diagramme en barres, un diagramme circulaire ou une courbe dans des cas adaptés à une lecture immédiate. |
| 🎲↩1 | Comprendre et utiliser le vocabulaire approprié : « impossible », « possible », « certain », « probable », « peu probable », « une chance sur deux » |
| 🎲↩2 | Identifier des expériences aléatoires. |
| 🎲↩3 | Identifier toutes les issues possibles lors d’une expérience aléatoire simple (CM2). |
| 🎲↩4 | Identifier toutes les issues réalisant un évènement dans une expérience aléatoire simple (CM2). |
| 🎲↩5 | Dans une situation d’équiprobabilité, lors d’une expérience aléatoire simple, exprimer la probabilité d’un évènement sous la forme « a chances sur b » (CM2). |
| 🎲↩6 | Comparer des probabilités dans des cas simples (CM2). |
| 🎲↩7 | Comprendre la notion d’indépendance lors de la répétition de la même expérience aléatoire (CM2). |
| 🎲↩8 | Dans des situations d’équiprobabilité, recenser toutes les issues possibles d’une expérience aléatoire en deux étapes dans un tableau ou dans un arbre afin de déterminer des probabilités (CM2). |
| ∝🛠1 | L'élève sait repérer des relations multiplicatives simples entre des nombres (double, quadruple, moitié, tiers, quart). |
| ∝🛠2 | Il associe de manière automatique les expressions du type : « 4 fois plus grand, 4 fois plus petit, 5 fois plus, 5 fois moins » à une multiplication ou à une division. |

