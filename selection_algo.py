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

    # Limiter le nombre de révisions des rappels strictement
    if est_rappel:
        max_usages = 2 if nb_automatismes == 6 else 4
        if used_codes[code] >= max_usages:
            return False

    # Les autres automatismes ne sont pas limités strictement

    if not est_rappel and theme_code not in themes_passes:
        return False

    return respecte_espacement(semaines_precedentes, semaine, est_rappel, min_espacement_rappel)

def selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes, positions):
    selection = [None] * nb_automatismes
    theme_autos = [
        c for c in data[data['Code'].str.startswith(theme)]['Code']
        if peut_etre_place(c, data, semaine, auto_weeks, used_codes, themes_passes, min_espacement_rappel, nb_automatismes)
    ]
    random.shuffle(theme_autos)
    for i, pos in enumerate(positions):
        if i < len(theme_autos):
            selection[pos] = theme_autos[i]
    return selection

def selectionner_automatismes_autres_themes(data, semaine, auto_weeks, used_codes, codes_selectionnes, min_espacement_rappel, themes_passes, positions, nb_automatismes):
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
    for pos in positions:
        if tous_candidats:
            choix = tous_candidats.pop()
            selection[pos] = choix
            codes_selectionnes.add(choix)
    return selection

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme, min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3, themes_passes, sequences, nb_automatismes):
    selection_finale = [None] * nb_automatismes
    codes_selectionnes = set()

    # 1. Automatisme du thème de la semaine
    pos_theme = [0, 3] if nb_automatismes == 6 else [0, 3, 6]
    base_theme = selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes, pos_theme)
    for i in pos_theme:
        if base_theme[i] is not None:
            selection_finale[i] = base_theme[i]
            codes_selectionnes.add(base_theme[i])

    # 2. Automatisme diagnostique du thème à venir (rappels ou non)
    future_index = semaine + 2 if nb_automatismes == 6 else semaine + 3
    if future_index < len(sequences):
        future_theme = sequences[future_index]
        pos_diag = [1, 4] if nb_automatismes == 6 else [1, 4, 7]
        diag_theme = selectionner_automatismes_theme(data, semaine, future_theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes + [future_theme], nb_automatismes, pos_diag)
        for i in pos_diag:
            if diag_theme[i] is not None:
                selection_finale[i] = diag_theme[i]
                codes_selectionnes.add(diag_theme[i])

    # 3. Complément (rappels et thèmes déjà vus)
    pos_autres = [i for i in range(nb_automatismes) if selection_finale[i] is None]
    complement = selectionner_automatismes_autres_themes(data, semaine, auto_weeks, used_codes, codes_selectionnes, min_espacement_rappel, themes_passes, pos_autres, nb_automatismes)
    for i in pos_autres:
        if selection_finale[i] is None and complement[i] is not None:
            selection_finale[i] = complement[i]
            codes_selectionnes.add(complement[i])

    # 4. Dernier recours : remplir les cases vides (même sans toutes les contraintes)
    for i in range(nb_automatismes):
        if selection_finale[i] is None:
            candidats = [
                c for c in data['Code']
                if c not in selection_finale and respecte_espacement(auto_weeks.get(c, []), semaine, data[data['Code'] == c]['Rappel'].iloc[0], min_espacement_rappel)
            ]
            random.shuffle(candidats)
            for c in candidats:
                selection_finale[i] = c
                break

    return selection_finale
