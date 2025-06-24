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


def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
    themes_passes
):
    selection_finale = [None] * 6
    codes_selectionnes = set()

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    # Étape 1 : choisir auto1 et auto2 (thème courant)
    auto1, auto2 = None, None
    if theme:
        theme_autos = data[data['Code'].str.startswith(theme)].sort_values('Num')
        candidats = [row['Code'] for _, row in theme_autos.iterrows()
                     if respecte_espacement(auto_weeks.get(row['Code'], []), semaine, row['Rappel'],
                                            min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)
                     and used_codes[row['Code']] < 3]
        if len(candidats) >= 2:
            auto1, auto2 = candidats[:2]
            codes_selectionnes.update([auto1, auto2])

    # Étape 2 : choisir 2 autres thèmes différents
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    autres_groupes = []
    for t in autres_themes:
        autos = data[data['Code'].str.startswith(t)].sort_values('Num')
        valides = [row['Code'] for _, row in autos.iterrows()
                   if row['Code'] not in codes_selectionnes
                   and peut_etre_place(row['Code'])
                   and used_codes[row['Code']] < 3]
        if len(valides) >= 2:
            autres_groupes.append(valides[:2])
        if len(autres_groupes) == 2:
            break

    # Placement : A1, B1, C1, A2, B2, C2
    index_map = [0, 1, 2, 3, 4, 5]
    codes_to_place = []
    if auto1 and auto2:
        codes_to_place = [auto1]
        if autres_groupes:
            codes_to_place.append(autres_groupes[0][0])
        if len(autres_groupes) > 1:
            codes_to_place.append(autres_groupes[1][0])
        codes_to_place.append(auto2)
        if autres_groupes:
            codes_to_place.append(autres_groupes[0][1])
        if len(autres_groupes) > 1:
            codes_to_place.append(autres_groupes[1][1])

    for idx, code in zip(index_map, codes_to_place):
        selection_finale[idx] = code
        codes_selectionnes.add(code)

    return selection_finale
