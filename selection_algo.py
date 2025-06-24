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
                                     min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                                     themes_passes):
    selection_theme = [None] * 6

    themes_avec_rappel = set(data[data['Rappel'] == True]['Code'].str[0].unique())

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel:
            if theme_code not in themes_passes:
                if theme_code in themes_avec_rappel:
                    return False
        return respecte_espacement(
            semaines_precedentes, semaine, est_rappel,
            min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3
        )

    theme_autos = [c for c in data[data['Code'].str.startswith(theme)]['Code']
                   if peut_etre_place(c) and used_codes[c] < 3]

    if len(theme_autos) >= 2:
        auto1, auto2 = theme_autos[:2]
    elif len(theme_autos) == 1:
        auto1 = auto2 = theme_autos[0]
    else:
        auto1 = auto2 = None

    if auto1:
        selection_theme[0] = auto1
    if auto2:
        selection_theme[3] = auto2

    return selection_theme

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
                               min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                               themes_passes):

    selection_finale = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes,
        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
        themes_passes
    )

    codes_selectionnes = set([code for code in selection_finale if code])

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    # Choix complémentaires stricts par thème
    autres_themes = [t for t in sorted(set(data['Code'].str[0])) if t != theme]
    candidats = []
    for t in autres_themes:
        auto_candidats = [c for c in data[data['Code'].str.startswith(t)]['Code']
                          if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]
        if len(auto_candidats) >= 2:
            candidats.extend(auto_candidats[:2])
        elif len(auto_candidats) == 1:
            candidats.append(auto_candidats[0])
        if len(candidats) >= 4:
            break

    # Placement alternatif en A1 B1 C1 A2 B2 C2 → index [0, 1, 2, 3, 4, 5] donc thème courant déjà en 0 et 3
    placement_indices = [1, 2, 4, 5]
    for idx, code in zip(placement_indices, candidats):
        if selection_finale[idx] is None:
            selection_finale[idx] = code
            codes_selectionnes.add(code)

    # Complément ultime
    for _, row in data.iterrows():
        code = row['Code']
        if code in codes_selectionnes or used_codes[code] >= 3:
            continue
        if not peut_etre_place(code):
            continue
        for j in range(6):
            if selection_finale[j] is None:
                selection_finale[j] = code
                codes_selectionnes.add(code)
                break
        if None not in selection_finale:
            break

    return selection_finale
