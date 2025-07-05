
import random
from collections import defaultdict

def selectionner_automatismes_theme_q1q2(data, semaine, theme, auto_weeks, used_codes, themes_passes, positions):
    selection = [None] * 9
    theme_autos = list(data[data['Code'].str.startswith(theme)]['Code'])

    # Respect de l'ordre d'apparition dans le fichier CSV
    for i, pos in enumerate(positions):
        if i < len(theme_autos):
            selection[pos] = theme_autos[i]
        elif len(theme_autos) == 1:
            selection[pos] = theme_autos[0]
        elif len(theme_autos) == 2:
            selection[pos] = theme_autos[i % 2]
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
