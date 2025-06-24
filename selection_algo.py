from collections import defaultdict
import random


def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel,
                        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):
    if not semaines_precedentes:
        return True
    ecart = semaine_actuelle - max(semaines_precedentes)
    if est_rappel:
        return ecart >= min_espacement_rappel
    if len(semaines_precedentes) == 1:
        return espacement_min2 <= ecart <= espacement_max2
    elif len(semaines_precedentes) == 2:
        return espacement_min3 <= ecart <= espacement_max3
    return False


import random

def selectionner_automatismes_theme(
    data, semaine, theme, auto_weeks, used_codes,
    min_espacement_rappel, espacement_min2, espacement_max2,
    espacement_min3, espacement_max3, themes_passes
):
    """
    Place uniquement deux automatismes du thème courant en positions 0 et 3.
    Retourne une liste de 6 avec None partout sauf aux indices 0 et 3.
    """
    selection = [None] * 6
    codes_selectionnes = set()

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        if not semaines_precedentes:
            return True
        ecart = semaine - max(semaines_precedentes)
        if est_rappel:
            return ecart >= min_espacement_rappel
        if len(semaines_precedentes) == 1:
            return espacement_min2 <= ecart <= espacement_max2
        if len(semaines_precedentes) == 2:
            return espacement_min3 <= ecart <= espacement_max3
        return False

    candidats = data[data['Code'].str.startswith(theme)].sort_values('Num')
    valides = [row['Code'] for _, row in candidats.iterrows()
               if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3]

    if len(valides) == 1:
        selection[0] = valides[0]
        selection[3] = valides[0]  # cas d'un seul automatisme répété deux fois
        codes_selectionnes.add(valides[0])
    elif len(valides) >= 2:
        selection[0] = valides[0]
        selection[3] = valides[1]
        codes_selectionnes.update([valides[0], valides[1]])
    # sinon on laisse None aux positions 0 et 3 si pas d'autos valides

    return selection, codes_selectionnes


def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2,
    espacement_min3, espacement_max3, themes_passes
):
    """
    Appelle d'abord selectionner_automatismes_theme pour placer les 2 autos du thème courant,
    puis complète les 4 cases restantes par des autos d'autres thèmes (2 thèmes max),
    en respectant contraintes et priorités,
    sans jamais déplacer les autos en position 0 et 3.
    """

    # Étape 1 : placer auto1 et auto2 du thème courant
    selection, codes_selectionnes = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes,
        min_espacement_rappel, espacement_min2, espacement_max2,
        espacement_min3, espacement_max3, themes_passes
    )

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        if not semaines_precedentes:
            return True
        ecart = semaine - max(semaines_precedentes)
        if est_rappel:
            return ecart >= min_espacement_rappel
        if len(semaines_precedentes) == 1:
            return espacement_min2 <= ecart <= espacement_max2
        if len(semaines_precedentes) == 2:
            return espacement_min3 <= ecart <= espacement_max3
        return False

    # Étape 2 : trouver 2 autres thèmes pour compléter (hors thème courant)
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)

    themes_choisis = []
    for t in autres_themes:
        candidats = data[data['Code'].str.startswith(t)].sort_values('Num')
        valides = [row['Code'] for _, row in candidats.iterrows()
                   if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3 and row['Code'] not in codes_selectionnes]
        if len(valides) >= 2:
            themes_choisis.append((t, valides[:2]))
        elif len(valides) == 1:
            themes_choisis.append((t, valides[:1]))
        if len(themes_choisis) == 2:
            break

    # Si moins de 2 thèmes, on complète avec les thèmes restants
    if len(themes_choisis) < 2:
        for t in autres_themes:
            if any(t == tc for tc, _ in themes_choisis):
                continue
            candidats = data[data['Code'].str.startswith(t)].sort_values('Num')
            valides = [row['Code'] for _, row in candidats.iterrows()
                       if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3 and row['Code'] not in codes_selectionnes]
            if valides:
                themes_choisis.append((t, valides[:2]))
            if len(themes_choisis) >= 2:
                break

    # Étape 3 : remplir les positions libres (1, 2, 4, 5) en alternant autos des deux thèmes choisis
    positions_libres = [i for i, v in enumerate(selection) if v is None]

    autos_placement = []
    for i in range(2):  # max 2 autos par thème choisi
        for t, autos in themes_choisis:
            if i < len(autos):
                autos_placement.append(autos[i])

    for pos, code in zip(positions_libres, autos_placement):
        selection[pos] = code
        codes_selectionnes.add(code)

    # Étape 4 : compléter les éventuels None restants avec autos peu vus (<3 fois)
    candidats_restants = data[
        data['Code'].apply(lambda c: peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes)
    ]
    for _, row in candidats_restants.iterrows():
        for i in range(6):
            if selection[i] is None:
                selection[i] = row['Code']
                codes_selectionnes.add(row['Code'])
                break

    # Étape 5 : en dernier recours, remplir les None (si jamais il y en a) avec n'importe quel auto non sélectionné
    for i in range(6):
        if selection[i] is None:
            for c in data['Code']:
                if c not in codes_selectionnes:
                    selection[i] = c
                    codes_selectionnes.add(c)
                    break

    return selection
