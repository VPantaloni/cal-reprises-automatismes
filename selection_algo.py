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
                                     themes_passes, nb_automatismes):
    selection_theme = [None] * nb_automatismes

    themes_avec_rappel = set(data[data['Rappel'] == True]['Code'].str[0].unique())

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes and theme_code in themes_avec_rappel:
            return False
        return respecte_espacement(
            semaines_precedentes, semaine, est_rappel,
            min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3
        )

    theme_autos = [c for c in data[data['Code'].str.startswith(theme)]['Code']
                   if peut_etre_place(c) and used_codes[c] < 3]

    indices_theme = [0, nb_automatismes - 3, nb_automatismes - 1]
    top3 = theme_autos[:3]
    for idx, code in zip(indices_theme, top3):
        selection_theme[idx] = code

    return selection_theme


def selectionner_automatismes_theme_futur(data, semaine, theme_futur, auto_weeks, used_codes, codes_selectionnes,
                                          min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                                          themes_passes, nb_automatismes):
    selection = [None] * nb_automatismes

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        return respecte_espacement(
            semaines_precedentes, semaine, est_rappel,
            min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3
        )

    futurs_autos = [c for c in data[data['Code'].str.startswith(theme_futur)]['Code']
                    if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]

    indices_futur = [1, 2, nb_automatismes - 2]
    top3 = futurs_autos[:3]
    for idx, code in zip(indices_futur, top3):
        selection[idx] = code

    return selection


def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
                               min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
                               themes_passes, sequences, nb_automatismes):

    base = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes,
        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
        themes_passes, nb_automatismes
    )
    codes_selectionnes = set([c for c in base if c])

    theme_futur = None
    for decalage in [2, 3]:
        if semaine + decalage < len(sequences):
            futur = sequences[semaine + decalage]
            if futur:
                theme_futur = futur
                break

    if theme_futur:
        futur_block = selectionner_automatismes_theme_futur(
            data, semaine, theme_futur, auto_weeks, used_codes, codes_selectionnes,
            min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
            themes_passes, nb_automatismes
        )
    else:
        futur_block = [None] * nb_automatismes

    codes_selectionnes.update([c for c in futur_block if c])

    selection_finale = [None] * nb_automatismes
    indices_theme = [0, nb_automatismes - 3, nb_automatismes - 1]
    indices_futur = [1, 2, nb_automatismes - 2]

    for i in indices_theme:
        if base[i]:
            selection_finale[i] = base[i]
    for i in indices_futur:
        if futur_block[i]:
            selection_finale[i] = futur_block[i]

    for i in range(nb_automatismes):
        if not selection_finale[i]:
            candidats = data[~data['Rappel'] & (~data['Code'].isin(codes_selectionnes))]
            candidats = candidats.sample(frac=1)  # shuffle
            for idx, row in candidats.iterrows():
                code = row['Code']
                if used_codes[code] < 3 and respecte_espacement(
                    auto_weeks.get(code, []), semaine, row['Rappel'],
                    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3
                ):
                    selection_finale[i] = code
                    codes_selectionnes.add(code)
                    break

    return selection_finale
