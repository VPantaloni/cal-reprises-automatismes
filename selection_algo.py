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
    autos_theme = list(data[data['Sous-Thème'] == theme]['Code'])
    if not autos_theme:
        # Pas d'automatisme pour ce thème, on renvoie vide
        return []

    # Détermination auto1 et auto2 selon next_index_by_theme (indices circulaires)
    idx1 = (next_index_by_theme[theme] - 1) % len(autos_theme)
    idx2 = (idx1 + 1) % len(autos_theme)
    auto1 = autos_theme[idx1]
    auto2 = autos_theme[idx2]

    # Mise à jour de l’indice pour la prochaine semaine (pour le thème courant)
    next_index_by_theme[theme] = (idx2 + 1) % len(autos_theme) + 1

    # Ensemble des codes sélectionnés (pour éviter doublons)
    codes_selectionnes = set([auto1, auto2])

    # Liste finale avec 6 positions, None par défaut
    selection_finale = [None] * 6
    selection_finale[0] = auto1  # 1er auto thème courant
    selection_finale[3] = auto2  # 2e auto thème courant

    # Liste des positions libres restantes
    positions_libres = [1, 2, 4, 5]

    # Liste candidate des autres automatismes (hors auto1 et auto2), randomisée pour diversité
    autres_autos = list(set(data['Code']) - codes_selectionnes)
    random.shuffle(autres_autos)

    # Fonction locale pour vérifier l’espacement pour un code donné
    def peut_etre_place(code):
        semaines_precedentes = auto_weeks.get(code, [])
        est_rappel = data.loc[data['Code'] == code, 'Rappel'].iloc[0]
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    # Compléter les autres positions avec automatismes respectant l’espacement
    for code in autres_autos:
        if not positions_libres:
            break
        if peut_etre_place(code):
            pos = positions_libres.pop(0)
            selection_finale[pos] = code
            codes_selectionnes.add(code)

    # Si positions libres restent (manque d’autos respectant les contraintes), on complète naïvement
    if positions_libres:
        for code in autres_autos:
            if not positions_libres:
                break
            if code not in codes_selectionnes:
                pos = positions_libres.pop(0)
                selection_finale[pos] = code
                codes_selectionnes.add(code)

    # Debug : afficher la sélection finale par semaine (décommenter pour debug)
    # print(f"Semaine {semaine+1} ({theme}): {selection_finale}")

    return [code for code in selection_finale if code is not None]
