import random
from collections import defaultdict

def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)

    if hasattr(selection_by_week, 'items'):
        iterator = selection_by_week.items()
    else:
        iterator = enumerate(selection_by_week)

    for semaine, codes in iterator:
        if codes is None:
            continue
        for code in codes:
            if code != "❓":
                auto_weeks[code].append(semaine)
                used_codes[code] += 1

    return auto_weeks, used_codes

def est_valide(code, semaine, auto_weeks, espacement=3):
    if code not in auto_weeks:
        return True
    for s in auto_weeks[code]:
        if abs(s - semaine) < espacement:
            return False
    return True

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    nb_semaines = len(sequences)
    positions_q3 = [2, 5, 8]
    all_codes = list(data['Code'].unique())

    for semaine in range(nb_semaines):
        if semaine not in selection_by_week:
            continue  # Ne rien faire si la semaine n'existe pas

        ligne = selection_by_week[semaine]

        if len(ligne) < 9:
            # On complète uniquement avec des ❓ à la fin (sans toucher Q1/Q2 déjà là)
            ligne += ["❓"] * (9 - len(ligne))
            selection_by_week[semaine] = ligne

        for pos in positions_q3:
            if ligne[pos] == "❓":
                random.shuffle(all_codes)
                for code in all_codes:
                    if est_valide(code, semaine, auto_weeks):
                        ligne[pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        break
                else:
                    # Aucun code valide, on met quand même le premier
                    code = all_codes[0]
                    ligne[pos] = code
                    auto_weeks[code].append(semaine)
                    used_codes[code] += 1

        selection_by_week[semaine] = ligne

    return selection_by_week
