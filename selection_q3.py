from collections import defaultdict
import random

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
    return all(abs(s - semaine) >= espacement for s in auto_weeks[code])

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    nb_semaines = len(sequences)
    all_codes = list(data['Code'].unique())

    for semaine in range(nb_semaines):
        if not selection_by_week[semaine]:
            selection_by_week[semaine] = ["❓"] * 9

        for pos in range(9):
            if selection_by_week[semaine][pos] == "❓":
                # 🔽 On trie les codes par nombre d'occurrences (les moins fréquents en premier)
                sorted_codes = sorted(all_codes, key=lambda c: used_codes.get(c, 0))
                for code in sorted_codes:
                    if est_valide(code, semaine, auto_weeks):
                        selection_by_week[semaine][pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        break
                else:
                    # ⚠️ Aucun ne respecte l'espacement → forçage du moins utilisé
                    fallback_code = sorted_codes[0]
                    selection_by_week[semaine][pos] = fallback_code
                    auto_weeks[fallback_code].append(semaine)
                    used_codes[fallback_code] += 1

    return selection_by_week
