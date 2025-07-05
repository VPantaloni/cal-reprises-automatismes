
import random
from collections import defaultdict

def selectionner_automatismes_theme_q1q2(data, semaine, theme, auto_weeks, used_codes, themes_passes, positions):
    selection = [None] * 9
    # Récupérer tous les automatismes du thème
    theme_autos = list(data[data['Code'].str.startswith(theme)]['Code'])

    if not theme_autos:
        return selection  # Aucun automatisme, rien à faire

    # Si 1 ou 2 automatismes → répétitions intelligentes
    if len(theme_autos) == 1:
        for pos in positions:
            selection[pos] = theme_autos[0]
        return selection
    elif len(theme_autos) == 2:
        alternance = [theme_autos[0], theme_autos[1], theme_autos[0]]
        for pos, code in zip(positions, alternance):
            selection[pos] = code
        return selection

    # Sinon, équilibrer selon les occurrences (used_codes)
    # Trier par nombre d'utilisations croissant, puis ordre dans CSV
    auto_scores = [(code, used_codes.get(code, 0)) for code in theme_autos]
    auto_scores.sort(key=lambda x: (x[1], theme_autos.index(x[0])))  # tri par usage puis position

    # Remplir les positions avec les moins utilisés
    for pos, (code, _) in zip(positions, auto_scores):
        selection[pos] = code

    return selection


def selectionner_q1q2(data, semaine, theme, sequences):
    selection_finale = [None] * 9
    pos_theme = [0, 3, 6]
    pos_diag = [1, 4, 7]

    # Q1 : thème de la semaine
    base_theme = selectionner_automatismes_theme_q1q2(data, semaine, theme, None, None, [], pos_theme)
    for i in pos_theme:
        if base_theme[i] is not None:
            selection_finale[i] = base_theme[i]

    # Q2 : thème futur dans 2 ou 3 semaines
    future_index = semaine + 2
    if future_index < len(sequences) and sequences[future_index] == theme:
        future_index = semaine + 3
    if future_index < len(sequences):
        future_theme = sequences[future_index]
        diag_theme = selectionner_automatismes_theme_q1q2(data, semaine, future_theme, None, None, [theme], pos_diag)
        for i in pos_diag:
            if diag_theme[i] is not None:
                selection_finale[i] = diag_theme[i]

    # Q3 : ❓ placeholder
    for i in range(9):
        if selection_finale[i] is None:
            selection_finale[i] = "❓"

    return selection_finale
