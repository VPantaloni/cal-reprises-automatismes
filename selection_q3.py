from collections import defaultdict

def reconstruire_auto_weeks(selection_by_week):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)
    for semaine, codes in selection_by_week.items():
        for code in codes:
            if code != "❓":
                auto_weeks[code].append(semaine)
                used_codes[code] += 1
    return auto_weeks, used_codes

def est_valide(code, semaine, auto_weeks, used_codes, sequences, selection_by_week):
    # Exemple de contrainte : espacement minimum entre occurrences
    espacement_min = 3
    if code not in auto_weeks:
        return True
    for s in auto_weeks[code]:
        if abs(s - semaine) < espacement_min:
            return False
    # Eviter de mettre plusieurs fois le même code dans la même semaine
    if code in selection_by_week[semaine]:
        return False
    return True

def selectionner_q3(data, sequences, selection_by_week, auto_weeks, used_codes):
    all_codes = list(data['Code'].unique())
    nb_semaines = len(sequences)

    # Positions Q3 dans la grille
    positions_q3 = [2, 5, 8]

    for semaine in range(nb_semaines):
        for pos in positions_q3:
            if selection_by_week[semaine][pos] == "❓":
                # On cherche un code valide
                trouve = False
                # Essayer d'abord les codes les moins utilisés pour équilibrer
                codes_tries = sorted(all_codes, key=lambda c: used_codes.get(c,0))
                for code in codes_tries:
                    if est_valide(code, semaine, auto_weeks, used_codes, sequences, selection_by_week):
                        selection_by_week[semaine][pos] = code
                        auto_weeks[code].append(semaine)
                        used_codes[code] += 1
                        trouve = True
                        break
                # Fallback si rien trouvé : mettre un code au hasard (le moins utilisé)
                if not trouve:
                    for code in codes_tries:
                        if code not in selection_by_week[semaine]:
                            selection_by_week[semaine][pos] = code
                            auto_weeks[code].append(semaine)
                            used_codes[code] += 1
                            break

    # Retourner la sélection mise à jour (même si pas obligatoire car modif en place)
    return selection_by_week
