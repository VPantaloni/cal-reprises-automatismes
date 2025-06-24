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
        selection_theme[1] = auto2

    return selection_theme

def selectionner_automatismes_34(data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
                                 min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                                 themes_passes):
    selection = [None] * 6

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    autres_themes = [t for t in sorted(set(data['Code'].str[0])) if t != theme]
    random.shuffle(autres_themes)
    candidats = []
    for t in autres_themes:
        auto_candidats = [c for c in data[data['Code'].str.startswith(t)]['Code']
                          if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]
        if len(auto_candidats) >= 2:
            candidats.extend(auto_candidats[:2])
            break

    if len(candidats) >= 2:
        selection[1], selection[4] = candidats[:2]

    return selection

def selectionner_automatismes_theme_56(data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
                                       min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                                       themes_passes):
    selection = [None] * 6

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    autres_themes = [t for t in sorted(set(data['Code'].str[0])) if t != theme]
    random.shuffle(autres_themes)
    candidats = []
    for t in autres_themes:
        auto_candidats = [c for c in data[data['Code'].str.startswith(t)]['Code']
                          if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]
        if len(auto_candidats) >= 2:
            candidats.extend(auto_candidats[:2])
            break

    if len(candidats) >= 2:
        selection[2], selection[5] = candidats[:2]

    return selection

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
                               min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                               themes_passes):

    base = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes,
        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
        themes_passes
    )
    codes_selectionnes = set([c for c in base if c])

    compl1 = selectionner_automatismes_34(
        data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
        themes_passes
    )
    codes_selectionnes.update([c for c in compl1 if c])

    compl2 = selectionner_automatismes_theme_56(
        data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
        themes_passes
    )
    codes_selectionnes.update([c for c in compl2 if c])

    # Fusion finale
    selection_finale = [None] * 6
    for i in range(6):
        for src in [base, compl1, compl2]:
            if src[i]:
                selection_finale[i] = src[i]
                break

    return selection_finale
