from collections import defaultdict
import random
import pandas as pd

def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    for i, semaine in enumerate(selection_by_week):
        for code in semaine:
            if code != "❓":
                auto_weeks[code].append(i)
    return auto_weeks

def selectionner_q3(data, selection_by_week):
    # Recalcul des occurences
    auto_weeks = reconstruire_auto_weeks(selection_by_week)
    used_codes = defaultdict(int)
    for code, semaines in auto_weeks.items():
        used_codes[code] = len(semaines)

    # Index des 2 dernières semaines
    indices_q2_finaux = [33, 34]
    for semaine in indices_q2_finaux:
        if semaine >= len(selection_by_week):
            continue
        futur_index = semaine + 2
        if futur_index < len(selection_by_week):
            theme = selection_by_week[futur_index][0] if selection_by_week[futur_index][0] != "❓" else None
        else:
            theme = None
        if theme:
            candidats = list(data[data['Code'].str.startswith(theme)]['Code'])
            for i in [1, 4, 7]:
                if i < len(selection_by_week[semaine]):
                    selection_by_week[semaine][i] = candidats[i % len(candidats)] if candidats else "❓"

    # Complétion des ❓ restants
    for semaine, semaine_data in enumerate(selection_by_week):
        for i, code in enumerate(semaine_data):
            if code == "❓":
                candidats = list(data['Code'])
                # Tri par nombre d’occurrences croissant
                candidats.sort(key=lambda c: used_codes.get(c, 0))
                for candidat in candidats:
                    semaines_precedentes = auto_weeks.get(candidat, [])
                    if all(abs(semaine - s) >= 2 for s in semaines_precedentes):
                        selection_by_week[semaine][i] = candidat
                        auto_weeks[candidat].append(semaine)
                        used_codes[candidat] += 1
                        break
    return selection_by_week
