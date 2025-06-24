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

import random

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
                             min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):
    """
    Sélectionne 6 automatismes pour la semaine donnée :
    - 2 du thème courant (forcés en position 0 et 3)
    - 4 autres selon règles d’espacement et fréquence
    """

    # Tous les automatismes du thème courant
    # Trouver les deux automatismes du thème courant non utilisés ou peu utilisés
    autos_theme = list(data[(data['Sous-Thème'] == theme_courant) & (~data['Code'].isin(used_codes))]['Code'])
    autos_theme += list(data[(data['Sous-Thème'] == theme_courant)]['Code'])  # au cas où tous utilisés

    auto1 = autos_theme[0] if len(autos_theme) > 0 else None
    auto2 = autos_theme[1] if len(autos_theme) > 1 else None

    selection_finale = [None] * 6

    if auto1:
        selection_finale[0] = auto1
        used_codes.add(auto1)
    if auto2:
        selection_finale[3] = auto2
        used_codes.add(auto2)

    # Remplir les autres positions (1,2,4,5)
    autres_positions = [1, 2, 4, 5]
    for code in data['Code']:
        if code in used_codes:
            continue
        if len([c for c in selection_finale if c is not None]) >= 6:
            break
        # Teste si on peut le placer ici (respect espacement, etc.)
        if peut_etre_place(code):
            pos = autres_positions.pop(0)
            selection_finale[pos] = code
            used_codes.add(code)

    # Nettoyage final : enlever les None
    selection_finale = [c for c in selection_finale if c is not None]

    return selection_finale
