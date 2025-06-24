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


def selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes,
                                   min_espacement_rappel, espacement_min2, espacement_max2,
                                   espacement_min3, espacement_max3, themes_passes):
    """
    Sélectionne strictement deux automatismes du thème courant, en respectant espacement et contraintes.
    Retourne une liste de taille 6 avec les deux autos en position 0 et 3, et None ailleurs.
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
        # Respecter les contraintes d'espacement
        ecart_ok = False
        if not semaines_precedentes:
            ecart_ok = True
        else:
            ecart = semaine - max(semaines_precedentes)
            if est_rappel:
                ecart_ok = ecart >= min_espacement_rappel
            else:
                if len(semaines_precedentes) == 1:
                    ecart_ok = espacement_min2 <= ecart <= espacement_max2
                elif len(semaines_precedentes) == 2:
                    ecart_ok = espacement_min3 <= ecart <= espacement_max3
                else:
                    ecart_ok = False
        return ecart_ok

    # Trouver automatismes valides du thème
    candidats = data[data['Code'].str.startswith(theme)].sort_values('Num')
    valides = [row['Code'] for _, row in candidats.iterrows()
               if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3]

    # Cas du thème avec un seul auto, on le place deux fois
    if len(valides) == 1:
        selection[0] = valides[0]
        selection[3] = valides[0]
        codes_selectionnes.add(valides[0])
    elif len(valides) >= 2:
        selection[0] = valides[0]
        selection[3] = valides[1]
        codes_selectionnes.update([valides[0], valides[1]])
    else:
        # Pas d'auto valide pour ce thème
        pass

    return selection, codes_selectionnes


def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
    themes_passes
):
    """
    Sélectionne 6 automatismes pour la semaine, dont 2 du thème courant (positions 0 et 3),
    puis complète avec 4 autres automatismes alternant entre deux autres thèmes,
    avec complétions supplémentaires si nécessaire.
    """

    # 1. Sélection stricte des 2 automatismes du thème courant
    selection, codes_selectionnes = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes,
        min_espacement_rappel, espacement_min2, espacement_max2,
        espacement_min3, espacement_max3, themes_passes
    )

    # 2. Trouver autres thèmes disponibles (différents du thème courant)
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        # Respecter les contraintes d'espacement
        ecart_ok = False
        if not semaines_precedentes:
            ecart_ok = True
        else:
            ecart = semaine - max(semaines_precedentes)
            if est_rappel:
                ecart_ok = ecart >= min_espacement_rappel
            else:
                if len(semaines_precedentes) == 1:
                    ecart_ok = espacement_min2 <= ecart <= espacement_max2
                elif len(semaines_precedentes) == 2:
                    ecart_ok = espacement_min3 <= ecart <= espacement_max3
                else:
                    ecart_ok = False
        return ecart_ok

    # 3. Choisir 2 autres thèmes différents qui ont des automatismes valides
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

    # Si on n'a pas trouvé 2 thèmes avec automatismes valides, on complète avec autres thèmes et automatismes
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

    # 4. Placement alterné des automatismes dans les indices restants (1,2,4,5)
    positions_libres = [i for i, val in enumerate(selection) if val is None]
    # Préparer liste d'autos B1, C1, B2, C2 (ou moins si pas dispo)
    autos_placement = []
    for i in range(2):  # max 2 autos par thème choisi
        for t, autos in themes_choisis:
            if i < len(autos):
                autos_placement.append(autos[i])

    # Placer dans les positions libres, en respectant l'ordre alterné
    for pos, code in zip(positions_libres, autos_placement):
        selection[pos] = code
        codes_selectionnes.add(code)

    # 5. Compléter les cases vides restantes avec automatismes peu vus (<3 fois)
    candidats_restants = data[
        data['Code'].apply(lambda c: peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes)
    ]
    for _, row in candidats_restants.iterrows():
        for i in range(6):
            if selection[i] is None:
                selection[i] = row['Code']
                codes_selectionnes.add(row['Code'])
                break

    # 6. Au cas où il resterait encore des None, remplir avec n'importe quel auto pour éviter trous
    for i in range(6):
        if selection[i] is None:
            # Trouver un auto au hasard dans data
            for c in data['Code']:
                if c not in codes_selectionnes:
                    selection[i] = c
                    codes_selectionnes.add(c)
                    break

    return selection
