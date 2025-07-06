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

# 🔍 Nouvelle fonction : vérifier si le thème d’un code a déjà été abordé
def theme_deja_aborde(code, semaine, sequences):
    emoji_theme = code[0]
    return emoji_theme in sequences[:semaine]

def selectionner_q3(data, selection_by_week, sequences, auto_weeks, used_codes):
    nb_semaines = len(sequences)
    all_codes = list(data['Code'].unique())

    for semaine in range(nb_semaines):
        if not selection_by_week[semaine]:
            selection_by_week[semaine] = ["❓"] * 9

        for pos in range(9):
            if selection_by_week[semaine][pos] == "❓":
                sorted_codes = sorted(all_codes, key=lambda c: used_codes.get(c, 0))
                
                placed = False
                for code in sorted_codes:
                    if est_valide(code, semaine, auto_weeks):
                        if theme_deja_aborde(code, semaine, sequences) or code[1] == "↩":
                            selection_by_week[semaine][pos] = code
                            auto_weeks[code].append(semaine)
                            used_codes[code] += 1
                            placed = True
                            break

                if not placed and sorted_codes:
                    # 🔁 Aucun code ne passe les critères pédagogiques → fallback forcé
                    fallback_code = sorted_codes[0]
                    selection_by_week[semaine][pos] = fallback_code
                    auto_weeks[fallback_code].append(semaine)
                    used_codes[fallback_code] += 1

    return selection_by_week
