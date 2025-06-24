from collections import defaultdict
import random

def selectionner_automatismes(data, semaine, theme_courant, auto_weeks, used_codes, next_index_by_theme,
                             min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):

    def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel):
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

    def peut_etre_place(code):
        semaines_precedentes = auto_weeks.get(code, [])
        est_rappel = data.loc[data['Code'] == code, 'Rappel'].values[0]
        # On autorise placement uniquement si thème déjà apparu ou rappel
        theme_code = data.loc[data['Code'] == code, 'Sous-Thème'].values[0]
        themes_passes = set([t for t in st.session_state.sequences[:semaine] if t])
        if (theme_code not in themes_passes) and (not est_rappel):
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel)

    selection_finale = [None] * 6

    # Pour faciliter filtres pandas, convertissons used_codes en set local
    codes_utilises = set(used_codes.keys())

    # Trouver les automatismes admissibles du thème courant (dans l'ordre du next_index_by_theme)
    autos_theme_all = list(data[(data['Sous-Thème'] == theme_courant)]['Code'])
    autos_theme_dispo = [code for code in autos_theme_all if peut_etre_place(code)]

    # On choisit auto1 et auto2 en fonction de next_index_by_theme[theme_courant] pour rotation
    idx = next_index_by_theme[theme_courant] - 1
    auto1 = autos_theme_dispo[idx % len(autos_theme_dispo)] if autos_theme_dispo else None
    auto2 = autos_theme_dispo[(idx + 1) % len(autos_theme_dispo)] if len(autos_theme_dispo) > 1 else None

    # Mise à jour de l'index pour la semaine suivante
    next_index_by_theme[theme_courant] = (idx + 2) % max(len(autos_theme_dispo), 1) + 1

    # Placer auto1 et auto2 en position 0 et 3
    if auto1:
        selection_finale[0] = auto1
        used_codes[auto1] += 1
    if auto2:
        selection_finale[3] = auto2
        used_codes[auto2] += 1

    # Compléter avec d'autres automatismes admissibles (hors auto1, auto2), en respectant contraintes et pas plus de 6 total
    autres_positions = [1, 2, 4, 5]
    for code in data['Code']:
        if code in used_codes and used_codes[code] > 0:
            continue
        if code == auto1 or code == auto2:
            continue
        if len([c for c in selection_finale if c is not None]) >= 6:
            break
        if peut_etre_place(code):
            pos = autres_positions.pop(0)
            selection_finale[pos] = code
            used_codes[code] += 1

    # Nettoyer None
    return [c for c in selection_finale if c is not None]

