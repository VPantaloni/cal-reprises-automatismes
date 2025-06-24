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
        if candidats:
            auto1 = candidats[0]
            codes_selectionnes.add(auto1)
        if len(candidats) > 1:
            auto2 = candidats[1]
            codes_selectionnes.add(auto2)

    # Placer auto1 et auto2 en position 0 et 3 (ligne 1)
    if auto1:
        selection_finale[0] = auto1
    if auto2:
        selection_finale[3] = auto2

    # Étape 2 : choisir 2 autres thèmes différents
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    for t in autres_themes:
        autos = data[data['Code'].str.startswith(t)].sort_values('Num')
        valides = [row['Code'] for _, row in autos.iterrows()
                   if row['Code'] not in codes_selectionnes
                   and peut_etre_place(row['Code'])
                   and used_codes[row['Code']] < 3]
        if len(valides) >= 2:
            # Choisir 2 et les placer dans les cases libres suivantes
            ajoutés = 0
            for code in valides[:2]:
                for pos in range(6):
                    if selection_finale[pos] is None:
                        selection_finale[pos] = code
                        codes_selectionnes.add(code)
                        ajoutés += 1
                        break
                if ajoutés >= 2:
                    break
        if sum(x is not None for x in selection_finale) >= 6:
            break

    return selection_finale
