import random
from collections import defaultdict

# Fonction pour reconstruire les auto_weeks et used_codes après Q1/Q2
def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)
    for semaine, codes in enumerate(selection_by_week):
        for code in codes:
            if code != "❓":
                auto_weeks[code].append(semaine)
                used_codes[code] += 1
    return auto_weeks, used_codes

def get_espacement_fibonacci(occurrence):
    fibonacci = [1, 2, 3, 5, 8, 11, 15, 20]
    return fibonacci[occurrence - 1] if occurrence <= len(fibonacci) else fibonacci[-1]

def est_rappel(code):
    return "↩" in code

def peut_etre_place(code, semaine, auto_weeks, used_codes, theme_code, theme_semaine):
    occur = used_codes[code]
    if occur == 0:
        # Première occurrence : le thème doit avoir déjà été vu (ou est vu cette semaine)
        return theme_code in theme_semaine or theme_code == theme_semaine.get(semaine)
    else:
        if est_rappel(code):
            if occur >= 5:
                return False
            derniere = max(auto_weeks[code])
            espacement = semaine - derniere
            return espacement >= get_espacement_fibonacci(occur)
        else:
            return False  # Non-rappel déjà vu une fois

def selectionner_q3(data, selection_by_week, sequences):
    auto_weeks, used_codes = reconstruire_auto_weeks(selection_by_week)
    all_codes = list(data['Code'])
    theme_par_code = {row['Code']: row['Code'][:2] for _, row in data.iterrows()}
    tous_les_themes = {i: sequences[i] for i in range(len(sequences))}

    # Calcul des occurrences actuelles
    code_occurrences = defaultdict(int)
    for semaine, codes in enumerate(selection_by_week):
        for code in codes:
            if code != "❓":
                code_occurrences[code] += 1

    # Trier les automatismes les moins vus en priorité
    codes_tries = sorted(all_codes, key=lambda x: (code_occurrences[x], est_rappel(x)))

    # Remplissage des cases ❓
    for semaine in range(len(selection_by_week)):
        for i in range(9):
            if selection_by_week[semaine][i] == "❓":
                for code in codes_tries:
                    theme_code = theme_par_code.get(code, "")
                    if peut_etre_place(code, semaine, auto_weeks, used_codes, theme_code, tous_les_themes):
                        selection_by_week[semaine][i] = code
                        used_codes[code] += 1
                        auto_weeks[code].append(semaine)
                        break  # On passe à la case suivante
    return selection_by_week
