from collections import defaultdict
import random

def get_espacement_fibonacci(occurrence):
    fibonacci = [1, 2, 3, 5, 8, 11, 15, 20]
    return fibonacci[occurrence - 1] if occurrence <= len(fibonacci) else fibonacci[-1]

def respecte_espacement(semaines_precedentes, semaine_actuelle):
    if not semaines_precedentes:
        return True
    ecart = semaine_actuelle - max(semaines_precedentes)
    occurrence = len(semaines_precedentes) + 1
    return ecart >= get_espacement_fibonacci(occurrence)

def completer_q3(data, selection_by_week, auto_weeks):
    # 1. Compter les occurrences globales
    occurrences = defaultdict(int)
    for code, semaines in auto_weeks.items():
        occurrences[code] = len(semaines)

    # 2. Pour chaque semaine, compléter les ❓ en position 2, 5, 8
    for semaine in range(len(selection_by_week)):
        for pos in [2, 5, 8]:
            code_actuel = selection_by_week[semaine][pos]
            if code_actuel == "❓":
                # Sélectionner candidats avec espacement suffisant
                candidats = []
                for code in data['Code']:
                    if respecte_espacement(auto_weeks.get(code, []), semaine):
                        candidats.append((code, occurrences[code]))

                if candidats:
                    # Trier par occurrence croissante
                    candidats.sort(key=lambda x: x[1])
                    choix = candidats[0][0]
                    selection_by_week[semaine][pos] = choix
                    auto_weeks[choix].append(semaine)
                    occurrences[choix] += 1

    return selection_by_week
