from collections import defaultdict

def get_espacement_fibonacci(occurrence):
    fibonacci = [1, 2, 3, 5, 8, 11, 15, 20]
    return fibonacci[occurrence - 1] if occurrence <= len(fibonacci) else fibonacci[-1]

def est_valide(week, code, auto_weeks, used_codes):
    if used_codes[code] >= 3:
        return False
    if not auto_weeks[code]:
        return True
    dernier = max(auto_weeks[code])
    espacement_requis = get_espacement_fibonacci(used_codes[code] + 1)
    return week - dernier >= espacement_requis

def selectionner_q3(data, sequences, selection_by_week, auto_weeks, used_codes):
    for semaine in range(len(sequences)):
        selection = selection_by_week[semaine]
        if not selection:
            continue

        for i in range(9):
            if selection[i] == "❓":
                # Cherche un automatisme compatible avec le thème de la semaine
                theme = sequences[semaine]
                candidats = list(data[data['Code'].str.startswith(theme)]['Code'])

                # Trier pour équilibrer les occurrences et espacer les répétitions
                def score(c):
                    nb = used_codes[c]
                    spacing = semaine - max(auto_weeks[c]) if auto_weeks[c] else 999
                    return (nb, -spacing)

                candidats = sorted(c for c in candidats if est_valide(semaine, c, auto_weeks, used_codes))
                candidats.sort(key=score)

                if candidats:
                    selection[i] = candidats[0]
                    used_codes[candidats[0]] += 1
                    auto_weeks[candidats[0]].append(semaine)

    # Correction des 2 dernières semaines (Q2 manquante parfois)
    for semaine in [33, 34]:
        selection = selection_by_week[semaine]
        if not selection:
            continue
        for i in [1, 4, 7]:  # positions Q2
            if selection[i] == "❓":
                theme = sequences[semaine]
                candidats = list(data[data['Code'].str.startswith(theme)]['Code'])
                candidats = sorted(c for c in candidats if est_valide(semaine, c, auto_weeks, used_codes))
                if candidats:
                    selection[i] = candidats[0]
                    used_codes[candidats[0]] += 1
                    auto_weeks[candidats[0]].append(semaine)
