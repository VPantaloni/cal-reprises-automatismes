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
    return all(abs(s - semaine) >= espacement for s in auto_weeks.get(code, []))

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    all_codes = list(data['Code'].unique())
    nb_semaines = len(sequences)
    positions_q3 = [2, 5, 8]

    for semaine in range(nb_semaines):
        if semaine not in selection_by_week:
            continue

        ligne = selection_by_week[semaine]

        # S'assurer que la ligne fait bien 9 éléments
        if len(ligne) < 9:
            ligne += ["❓"] * (9 - len(ligne))

        for pos in positions_q3:
            if ligne[pos] == "❓":
                # Trier par occurrences croissantes
                candidates = sorted(all_codes, key=lambda c: used_codes.get(c, 0))
                for code in candidates:
                    if est_valide(code, semaine, auto_weeks):
                        ligne[pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        break
                else:
                    # Aucun code ne respecte l'espacement : on prend celui avec le moins d'occurrences
                    fallback = candidates[0]
                    ligne[pos] = fallback
                    auto_weeks[fallback].append(semaine)
                    used_codes[fallback] += 1

        selection_by_week[semaine] = ligne

    return selection_by_week
