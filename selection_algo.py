from collections import defaultdict
import random

def get_espacement_fibonacci(occurrence):
    fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    return fibonacci[occurrence - 1] if occurrence <= len(fibonacci) else fibonacci[-1]

def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel, min_espacement_rappel):
    if not semaines_precedentes:
        return True
    ecart = semaine_actuelle - max(semaines_precedentes)
    if est_rappel:
        return ecart >= min_espacement_rappel
    occurrence = len(semaines_precedentes) + 1
    return ecart >= get_espacement_fibonacci(occurrence)

def peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes, min_espacement_rappel, nb_automatismes):
    row = data[data['Code'] == code].iloc[0]
    theme_code = row['Code'][0]
    est_rappel = row['Rappel']
    semaines_precedentes = auto_weeks.get(code, [])

    max_usage = 2 if est_rappel and nb_automatismes == 6 else \
                3 if est_rappel and nb_automatismes == 9 else \
                4 if nb_automatismes == 6 else 6

    if used_codes[code] >= max_usage:
        return False
    if not est_rappel and theme_code not in themes_passes:
        return False

    return respecte_espacement(semaines_precedentes, semaine, est_rappel, min_espacement_rappel)

def selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes):
    selection_finale = [None] * nb_automatismes
    theme_autos_optimaux = [
        c for c in data[data['Code'].str.startswith(theme)]['Code']
        if peut_etre_place(c, data, semaine, auto_weeks, used_codes, themes_passes, min_espacement_rappel, nb_automatismes)
    ]

    if len(theme_autos_optimaux) < (2 if nb_automatismes == 6 else 3):
        tous_theme_autos = data[data['Code'].str.startswith(theme)]['Code'].tolist()
        theme_autos = theme_autos_optimaux + [c for c in tous_theme_autos if c not in theme_autos_optimaux]
    else:
        theme_autos = theme_autos_optimaux

    positions_theme = [0, 3] if nb_automatismes == 6 else [0, 3, 6]
    if theme_autos:
        for i, pos in enumerate(positions_theme):
            selection_finale[pos] = theme_autos[i % len(theme_autos)]

    return selection_finale

def selectionner_automatismes_autres_themes(data, semaine, theme, auto_weeks, used_codes, codes_selectionnes, min_espacement_rappel, themes_passes, positions, nb_automatismes):
    selection = [None] * nb_automatismes
    tous_candidats = []
    for code in data['Code']:
        if code not in codes_selectionnes and peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes, min_espacement_rappel, nb_automatismes):
            row = data[data['Code'] == code].iloc[0]
            theme_code = row['Code'][0]
            est_rappel = row['Rappel']
            if est_rappel or theme_code in themes_passes:
                tous_candidats.append(code)

    random.shuffle(tous_candidats)
    candidat_index = 0
    for pos in positions:
        if candidat_index < len(tous_candidats):
            selection[pos] = tous_candidats[candidat_index]
            codes_selectionnes.add(tous_candidats[candidat_index])
            candidat_index += 1

    return selection

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme, min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3, themes_passes, sequences, nb_automatismes):
    base = selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes)
    codes_selectionnes = set([c for c in base if c])

    positions_autres = [1, 2, 4, 5] if nb_automatismes == 6 else [1, 2, 4, 5, 7, 8]
    complement = selectionner_automatismes_autres_themes(data, semaine, theme, auto_weeks, used_codes, codes_selectionnes, min_espacement_rappel, themes_passes, positions_autres, nb_automatismes)

    selection_finale = [None] * nb_automatismes
    for i in range(nb_automatismes):
        if base[i]:
            selection_finale[i] = base[i]
        elif complement[i]:
            selection_finale[i] = complement[i]

    for i in range(nb_automatismes):
        if selection_finale[i] is None:
            target_usage = 4 if nb_automatismes == 6 else 6
            candidats_sous_utilises = [
                c for c in data['Code']
                if c not in selection_finale and not data[data['Code'] == c]['Rappel'].iloc[0] and used_codes[c] < target_usage and respecte_espacement(auto_weeks.get(c, []), semaine, False, min_espacement_rappel)
            ]
            if not candidats_sous_utilises:
                candidats_sous_utilises = [
                    c for c in data['Code']
                    if c not in selection_finale and not data[data['Code'] == c]['Rappel'].iloc[0] and respecte_espacement(auto_weeks.get(c, []), semaine, False, min_espacement_rappel)
                ]
            if not candidats_sous_utilises:
                candidats_sous_utilises = [
                    c for c in data['Code']
                    if c not in selection_finale and respecte_espacement(auto_weeks.get(c, []), semaine, data[data['Code'] == c]['Rappel'].iloc[0], min_espacement_rappel)
                ]
            if candidats_sous_utilises:
                choix = random.choice(candidats_sous_utilises)
                selection_finale[i] = choix

    return selection_finale
