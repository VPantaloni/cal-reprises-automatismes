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

    def priorité(code):
        row = data[data['Code'] == code].iloc[0]
        est_rappel = row['Rappel']
        nb = used_codes[code]
        if est_rappel:
            if semaine < 17:
                return (0, nb)
            else:
                return (2, nb)
        else:
            return (1, nb)

    # Étape 1 : choisir auto1 et auto2 (thème courant)
    auto_theme = []
    if theme:
        theme_autos = data[data['Code'].str.startswith(theme)].sort_values('Num')
        for _, row in theme_autos.iterrows():
            code = row['Code']
            est_rappel = row['Rappel']
            semaines_precedentes = auto_weeks.get(code, [])
            if respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):
                auto_theme.append((code, used_codes[code]))

        auto_theme = sorted(auto_theme, key=lambda x: x[1])[:2]
        if len(auto_theme) > 0:
            selection_finale[0] = auto_theme[0][0]
            codes_selectionnes.add(auto_theme[0][0])
        if len(auto_theme) > 1:
            selection_finale[3] = auto_theme[1][0]
            codes_selectionnes.add(auto_theme[1][0])

    # Étape 2 : choisir 2 autres thèmes différents
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    themes_choisis = []
    for t in autres_themes:
        autos = data[data['Code'].str.startswith(t)].sort_values('Num')
        valides = []
        for _, row in autos.iterrows():
            code = row['Code']
            if code in codes_selectionnes:
                continue
            if not peut_etre_place(code):
                continue
            if used_codes[code] >= 3:
                continue
            valides.append(code)
        if len(valides) >= 2:
            themes_choisis.append((t, valides[:2]))
        if len(themes_choisis) == 2:
            break

    # Étape 3 : les placer dans la grille
    pos = 0
    for codes in [auto_theme[:1], auto_theme[1:2]] + [t[1] for t in themes_choisis]:
        for code in codes:
            while selection_finale[pos] is not None:
                pos += 1
            if pos < 6:
                selection_finale[pos] = code
                codes_selectionnes.add(code)

    return selection_finale
