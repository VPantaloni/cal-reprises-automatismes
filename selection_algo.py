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

    def choisir_2_auto_valide(theme_prefix):
        candidats = data[data['Code'].str.startswith(theme_prefix)].sort_values('Num')
        valides = [row['Code'] for _, row in candidats.iterrows()
                   if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3 and row['Code'] not in codes_selectionnes]
        return valides

    auto1, auto2 = None, None
    if theme:
        theme_autos = choisir_2_auto_valide(theme)
        if len(theme_autos) >= 2:
            auto1, auto2 = theme_autos[:2]
        elif len(theme_autos) == 1:
            auto1 = auto2 = theme_autos[0]
        if auto1:
            codes_selectionnes.add(auto1)
        if auto2:
            codes_selectionnes.add(auto2)

    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    groupes = []

    for t in autres_themes:
        valides = choisir_2_auto_valide(t)
        if len(valides) >= 2:
            groupes.append(valides[:2])
        elif len(valides) == 1:
            groupes.append([valides[0]])
        if sum(len(g) for g in groupes) >= 4:
            break

    if sum(len(g) for g in groupes) < 4:
        for t in autres_themes:
            valides = choisir_2_auto_valide(t)
            for v in valides:
                if v not in codes_selectionnes:
                    groupes.append([v])
                    if sum(len(g) for g in groupes) >= 4:
                        break
            if sum(len(g) for g in groupes) >= 4:
                break

    ordered = [None] * 6
    if auto1:
        ordered[0] = auto1
    if auto2:
        if auto2 != auto1:
            ordered[3] = auto2
        else:
            ordered[3] = auto1  # cas du thème avec un seul automatisme, répété 2 fois

    placement_index = [i for i in range(6) if ordered[i] is None]
    p = 0
    for g in groupes:
        for code in g:
            if p < len(placement_index):
                ordered[placement_index[p]] = code
                codes_selectionnes.add(code)
                p += 1

    # Compléter les cases restantes avec des automatismes peu vus (< 3 fois)
    candidats_restants = data[data['Code'].apply(lambda c: peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes)]
    for _, row in candidats_restants.iterrows():
        for i in range(6):
            if ordered[i] is None:
                ordered[i] = row['Code']
                codes_selectionnes.add(row['Code'])
                break

    return ordered
