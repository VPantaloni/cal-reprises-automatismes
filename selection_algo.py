from collections import defaultdict
import random

def get_espacement_fibonacci(occurrence):
    fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34]
    return fibonacci[occurrence - 1] if occurrence <= len(fibonacci) else fibonacci[-1]

def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel):
    if not semaines_precedentes:
        return True
    ecart = semaine_actuelle - max(semaines_precedentes)
    if est_rappel:
        return ecart >= 1
    occurrence = len(semaines_precedentes) + 1
    return ecart >= get_espacement_fibonacci(occurrence)

def peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes, theme):
    row = data[data['Code'] == code].iloc[0]
    theme_code = row['Code'][0]
    est_rappel = row['Rappel']
    semaines_precedentes = auto_weeks.get(code, [])

    if est_rappel:
        if used_codes[code] >= 5:  # augmenté de 4 → 5
            return False

    # Non-rappel : le thème doit être passé ou correspondre à celui de la semaine
    if not est_rappel and theme_code not in themes_passes and theme_code != theme:
        return False
    if semaine >= 25:
        if est_rappel and used_codes[code] >= 6:
            return False  # autorise 6 au lieu de 5
        # Réduire l’écart exigé ?
        return True  # désactive le contrôle d’espacement

    return respecte_espacement(semaines_precedentes, semaine, est_rappel)

def selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, themes_passes, positions):
    selection = [None] * 9
    theme_autos = [
        c for c in data[data['Code'].str.startswith(theme)]['Code']
        if peut_etre_place(c, data, semaine, auto_weeks, used_codes, themes_passes, theme)
    ]

    # ✅ On ne mélange pas, on respecte l'ordre du fichier CSV
    nb_autos = len(theme_autos)

    if nb_autos == 1:
        # Un seul automatisme → le répéter 3 fois
        code = theme_autos[0]
        for i in positions:
            selection[i] = code

    elif nb_autos == 2:
        # Deux automatismes → a, b, a ou a, b, b
        a, b = theme_autos
        variants = [[a, b, a], [a, b, b]]
        tirage = random.choice(variants)
        for i, pos in enumerate(positions[:3]):
            selection[pos] = tirage[i]

    else:
        # Trois ou plus → on prend les 3 premiers disponibles
        for i, pos in enumerate(positions):
            if i < len(theme_autos):
                selection[pos] = theme_autos[i]
    if not theme_autos:
    # On prend malgré tout les automatismes du thème, même s'ils ne respectent pas les règles
        theme_autos = list(data[data['Code'].str.startswith(theme)]['Code'])

    return selection


def selectionner_automatismes_autres_themes(data, semaine, auto_weeks, used_codes, codes_selectionnes, themes_passes, positions, theme):
    selection = [None] * 9
    tous_candidats = []
    for code in data['Code']:
        if code not in codes_selectionnes and peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes, theme):
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

def selectionner_automatismes(data, semaine, theme, auto_weeks, used_codes, next_index_by_theme, themes_passes, sequences):
    selection_finale = [None] * 9
    codes_selectionnes = set()

    # 1. Thème actuel
    pos_theme = [0, 3, 6]
    base_theme = selectionner_automatismes_theme(data, semaine, theme, auto_weeks, used_codes, themes_passes, pos_theme)
    for i in pos_theme:
        if base_theme[i] is not None:
            selection_finale[i] = base_theme[i]
            codes_selectionnes.add(base_theme[i])
    # Fallback : si aucune pastille du thème n'a été placée
    if all(selection_finale[i] is None for i in pos_theme):
        # Récupère tous les automatismes du thème, dans l'ordre du CSV
        fallback_autos = list(data[data['Code'].str.startswith(theme)]['Code'])
    
        # Cas : 1 automatisme → a, a, a | 2 automatismes → a, b, a (ou autre)
        if len(fallback_autos) == 1:
            fallback_autos = fallback_autos * 3
        elif len(fallback_autos) == 2:
            fallback_autos = [fallback_autos[0], fallback_autos[1], fallback_autos[0]]
    
        for i, pos in enumerate(pos_theme):
            selection_finale[pos] = fallback_autos[i]
            codes_selectionnes.add(fallback_autos[i])

    # 2. Thème futur (diagnostique)
    future_index = semaine + 2
    if future_index < len(sequences) and sequences[future_index] == theme:
        if semaine + 3 < len(sequences):
            future_index = semaine + 3
    if future_index < len(sequences):
        future_theme = sequences[future_index]
        pos_diag = [1, 4, 7]
        diag_theme = selectionner_automatismes_theme(
            data, semaine, future_theme, auto_weeks, used_codes,
            themes_passes + [future_theme], pos_diag
        )
        for i in pos_diag:
            if diag_theme[i] is not None:
                selection_finale[i] = diag_theme[i]
                codes_selectionnes.add(diag_theme[i])

    # 3. Complément : rappels + thèmes déjà vus
    pos_autres = [i for i in range(9) if selection_finale[i] is None]
    complement = selectionner_automatismes_autres_themes(
        data, semaine, auto_weeks, used_codes, codes_selectionnes, themes_passes, pos_autres, theme
    )
    for i in pos_autres:
        if selection_finale[i] is None and complement[i] is not None:
            selection_finale[i] = complement[i]
            codes_selectionnes.add(complement[i])

    # 4. Dernier recours
    for i in range(9):
        if selection_finale[i] is None:
            candidats = [
                c for c in data['Code']
                if c not in selection_finale and respecte_espacement(
                    auto_weeks.get(c, []), semaine, data[data['Code'] == c]['Rappel'].iloc[0])
            ]
            random.shuffle(candidats)
            for c in candidats:
                selection_finale[i] = c
                break

    return selection_finale
