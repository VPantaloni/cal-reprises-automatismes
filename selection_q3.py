from collections import defaultdict
import random

def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)

    # Si selection_by_week est dict
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
    # Vérifie qu'on ne place pas le même code trop près dans le temps
    if code not in auto_weeks:
        return True
    for s in auto_weeks[code]:
        if abs(s - semaine) < espacement:
            return False
    return True

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    nb_semaines = len(sequences)
    positions_q3 = [2, 5, 8]  # Positions réservées à Q3 uniquement

    all_codes = list(data['Code'].unique())

    for semaine in range(nb_semaines):
        # S'assurer que la semaine a bien une liste de 9 éléments
        if semaine not in selection_by_week:
            selection_by_week[semaine] = ["❓"] * 9
        elif len(selection_by_week[semaine]) < 9:
            selection_by_week[semaine] += ["❓"] * (9 - len(selection_by_week[semaine]))

        for pos in positions_q3:
            # Ne compléter que si Q3 est encore un placeholder
            if selection_by_week[semaine][pos] == "❓":
                random.shuffle(all_codes)
                for code in all_codes:
                    # Ne pas prendre un code déjà utilisé trop souvent ou trop rapproché
                    if est_valide(code, semaine, auto_weeks):
                        selection_by_week[semaine][pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        break
                else:
                    # En dernier recours, mettre un code quelconque
                    code = all_codes[0]
                    selection_by_week[semaine][pos] = code
                    auto_weeks[code].append(semaine)
                    used_codes[code] += 1

    return selection_by_week
