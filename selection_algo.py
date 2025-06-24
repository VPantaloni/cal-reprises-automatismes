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
    selection_finale = [None]*6
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

    # Choix des 2 auto du thème courant
    theme_autos = [c for c in data[data['Code'].str.startswith(theme)]['Code'] if peut_etre_place(c) and used_codes[c] < 3]
    if len(theme_autos) >= 2:
        auto1, auto2 = theme_autos[:2]
    elif len(theme_autos) == 1:
        auto1 = auto2 = theme_autos[0]
    else:
        # Aucun auto valide thème courant, choisir au moins 1 auto (stratégie à affiner)
        auto1 = auto2 = None

    if auto1:
        selection_finale[0] = auto1
        codes_selectionnes.add(auto1)
    if auto2:
        selection_finale[3] = auto2
        codes_selectionnes.add(auto2)

    # Remplissage des autres positions avec autres thèmes
    autres_positions = [1,2,4,5]
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)

    for t in autres_themes:
        candidats = [c for c in data[data['Code'].str.startswith(t)]['Code']
                     if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]
        for c in candidats:
            if autres_positions:
                pos = autres_positions.pop(0)
                selection_finale[pos] = c
                codes_selectionnes.add(c)
            else:
                break
        if not autres_positions:
            break

    # Compléter encore si cases vides
    if any(x is None for x in selection_finale):
        candidats_restants = [c for c in data['Code']
                             if peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes]
        for c in candidats_restants:
            if None not in selection_finale:
                break
            pos = selection_finale.index(None)
            selection_finale[pos] = c
            codes_selectionnes.add(c)

    # En dernier recours, remplir les cases vides avec doublons autorisés si thème a peu d'autos
    for i, val in enumerate(selection_finale):
        if val is None:
            # Mettre auto1 ou auto2 (si défini) en doublon ici
            selection_finale[i] = auto1 if auto1 else (auto2 if auto2 else None)

    return selection_finale

