#selection_q1q2.py
from collections import defaultdict

def selectionner_automatismes_theme_q1q2(data, semaine, theme, auto_weeks, used_codes, themes_passes, positions):
    selection = [None] * 9
    theme_autos = list(data[data['Code'].str.startswith(theme)]['Code'])

    # Exclure les automatismes déjà placés cette semaine dans un autre thème
    if themes_passes:
        theme_autos = [code for code in theme_autos if code[:1] not in themes_passes]

    # Trier par (nb d'utilisations, espacement le plus grand avec semaine actuelle)
    def score(code):
        nb = used_codes[code]
        spacing = min([abs(semaine - w) for w in auto_weeks[code]]) if auto_weeks[code] else 999
        return (nb, -spacing)

    theme_autos.sort(key=score)

    # Distribution des automatismes (y compris cas à 1 ou 2 automatisme(s))
    for i, pos in enumerate(positions):
        if len(theme_autos) == 0:
            break
        elif len(theme_autos) == 1:
            selection[pos] = theme_autos[0]
        elif len(theme_autos) == 2:
            selection[pos] = theme_autos[i % 2]
        else:
            if i < len(theme_autos):
                selection[pos] = theme_autos[i]
            else:
                selection[pos] = theme_autos[i % len(theme_autos)]

    return selection

def selectionner_q1q2(data, semaine, theme, sequences, auto_weeks, used_codes):
    selection_finale = [None] * 9
    pos_theme = [0, 3, 6]
    pos_diag = [1, 4, 7]

    # Q1 : thème de la semaine
    base_theme = selectionner_automatismes_theme_q1q2(
        data, semaine, theme, auto_weeks, used_codes, [], pos_theme
    )
    for i in pos_theme:
        if base_theme[i] is not None:
            selection_finale[i] = base_theme[i]
            auto_weeks[base_theme[i]].append(semaine)
            used_codes[base_theme[i]] += 1

    # Q2 : thème dans 2 ou 3 semaines
    future_index = semaine + 2
    if future_index < len(sequences) and sequences[future_index] == theme:
        future_index += 1
    if future_index < len(sequences):
        future_theme = sequences[future_index]
        diag_theme = selectionner_automatismes_theme_q1q2(
            data, semaine, future_theme, auto_weeks, used_codes, [theme], pos_diag
        )
        for i in pos_diag:
            if diag_theme[i] is not None:
                selection_finale[i] = diag_theme[i]
                auto_weeks[diag_theme[i]].append(semaine)
                used_codes[diag_theme[i]] += 1

    # Q3 : cases restantes = ❓
    for i in range(9):
        if selection_finale[i] is None:
            selection_finale[i] = "❓"

    return selection_finale
