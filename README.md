
# 🧠 *Calendrier de reprises* 
## Outil de planification des automatismes mathématiques en 6e

Cet outil (appli StreamLit) permet aux enseignants de cycle 3 de construire une **grille annuelle de réactivation des automatismes** en lien avec la courbe d’Ebbinghaus, à partir d’un fichier CSV listant les automatismes.

## Fichiers utiles
Fabrication d'une appli StreamLit qui appelle `app.py`

https://cal-reprises-automatismes-6e.streamlit.app/

Tutoriel utilisateur ici :
https://codimd.apps.education.fr/s/xd2gxRA1m

* app.py 
Mise en forme générale
* selection_q1q2.py
algo de répartition des automatismes des deux premières lignes
* selection_q3.py
algo de répartition des automatismes de la 3e ligne
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

---

## 📌 Principes de fonctionnement

- 35 semaines, réparties en 7 colonnes × 5 lignes.
- Pour chaque semaine, on choisit le **thème** principal travaillé cette semaine à l’aide d’un bouton.
- Une fois le thème choisi, l’outil sélectionne **9 automatismes** à revoir cette semaine.
- L'algorithme procède en deux temps :
1. Une première passe remplit les automatismes des deux premières lignes qui sont du thème courant et du thème futur (semaine+2). Il sont choisis préférentiellement dans l'ordre du programme.
2. Un calcul des occurences de chaque automatisme déjà placés dans les deux premières lignes permet d'identifier les automatismes qui doivent être placés en ligne 3 afin d'équilibrer le nombre de reprises (5 ou 6 reprises par automatismes sur l'année, sauf exception).
3. Les automatismes sont placés en ligne 3 en veillant à ne porter que sur des thèmes déjà travaillés ou des rappels des années antérieures (↩).


---

