from collections import defaultdict
import random

def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)

    # Adapté pour dict ou liste
    if hasattr(selection_by_week, 'items'):
        iterator = selection_by_week.items()
    else:
        iterator = enumerate(selection_by_week)

    for semaine, codes in iterator:
        if not codes:
            continue
        for code in codes:
            if code != "❓":
                auto_weeks[code].append(semaine)
                used_codes[code] += 1

    return auto_weeks, used_codes

def est_valide(code, semaine, auto_weeks, espacement=3):
    return all(abs(s - semaine) >= espacement for s in auto_weeks.get(code, []))

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    positions_q3 = [2, 5, 8]
    all_codes = list(data['Code'].unique())

    for semaine in range(len(sequences)):
        if semaine >= len(selection_by_week):
            continue
        semaine_codes = selection_by_week[semaine]
        if not semaine_codes or len(semaine_codes) < 9:
            semaine_codes += ["❓"] * (9 - len(semaine_codes))

        for pos in positions_q3:
            if semaine_codes[pos] == "❓":
                random.shuffle(all_codes)
                for code in all_codes:
                    if est_valide(code, semaine, auto_weeks):
                        semaine_codes[pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        break
        selection_by_week[semaine] = semaine_codes

    return selection_by_week
