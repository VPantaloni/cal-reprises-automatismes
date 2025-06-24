from collections import defaultdict

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

    # 1. Sélection des deux automatismes du thème courant
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

        auto_theme = sorted(auto_theme, key=lambda x: x[1])[:2]  # les 2 moins utilisés
        if len(auto_theme) > 0:
            selection_finale[0] = auto_theme[0][0]
            codes_selectionnes.add(auto_theme[0][0])
        if len(auto_theme) > 1:
            selection_finale[3] = auto_theme[1][0]
            codes_selectionnes.add(auto_theme[1][0])

    # 2. Compléter avec les autres candidats admissibles
    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    candidats = []
    for _, row in data.iterrows():
        code = row['Code']
        if code in codes_selectionnes:
            continue
        if peut_etre_place(code):
            candidats.append((code, used_codes[code]))

    candidats.sort(key=lambda x: x[1])

    for i in range(6):
        if selection_finale[i] is None and candidats:
            choix = candidats.pop(0)[0]
            selection_finale[i] = choix
            codes_selectionnes.add(choix)

    return selection_finale
