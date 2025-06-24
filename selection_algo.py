from collections import defaultdict
def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel,
                        min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):
    if not semaines_precedentes:
        return True
    ecart = semaine_actuelle - max(semaines_precedentes)
    if est_rappel:
        return ecart >= min_espacement_rappel
    if len(semaines_precedentes) == 1:
        return espacement_min2 <= ecart <= espacement_max2
    elif len(semaines_precedentes) == 2:
        return espacement_min3 <= ecart <= espacement_max3
    return False

def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3
):
    selection_finale = [None] * 6
    codes_selectionnes = set()

    # 1. Automatisme du thème courant
    if theme:
        theme_autos = data[data['Code'].str.startswith(theme)].sort_values('Num')

        if not theme_autos.empty:
            candidats_prioritaires = []
            tous_candidats = []
            for _, row in theme_autos.iterrows():
                code = row['Code']
                nb_vues = used_codes[code]
                tous_candidats.append(row)
                if row['Rappel']:
                    if nb_vues < 2:
                        candidats_prioritaires.append(row)
                else:
                    if nb_vues < 3:
                        candidats_prioritaires.append(row)

            if len(candidats_prioritaires) >= 2:
                auto1 = candidats_prioritaires[0]['Code']
                auto2 = candidats_prioritaires[1]['Code']
            elif len(candidats_prioritaires) == 1:
                auto1 = candidats_prioritaires[0]['Code']
                auto2 = next((c['Code'] for c in tous_candidats if c['Code'] != auto1), auto1)
            else:
                auto1 = tous_candidats[0]['Code']
                auto2 = tous_candidats[1]['Code'] if len(tous_candidats) > 1 else auto1

            selection_finale[0] = auto1
            selection_finale[3] = auto2
            codes_selectionnes.add(auto1)
            codes_selectionnes.add(auto2)

    # 2. Automatisme rappels
    candidats_rappel = []
    for _, row in data.iterrows():
        code = row['Code']
        if code in codes_selectionnes:
            continue
        if row['Rappel']:
            semaines_precedentes = auto_weeks.get(code, [])
            if respecte_espacement(semaines_precedentes, semaine, True,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3):
                candidats_rappel.append(row)

    candidats_rappel.sort(key=lambda r: used_codes[r['Code']])

    positions_libres = [i for i in range(6) if selection_finale[i] is None]
    for pos in positions_libres:
        if candidats_rappel:
            choix = candidats_rappel.pop(0)['Code']
            selection_finale[pos] = choix
            codes_selectionnes.add(choix)
        else:
            candidats_autres = []
            for _, row in data.iterrows():
                code = row['Code']
                if code not in codes_selectionnes and not row['Rappel']:
                    candidats_autres.append(row)
            candidats_autres.sort(key=lambda r: used_codes[r['Code']])
            if candidats_autres:
                choix = candidats_autres.pop(0)['Code']
                selection_finale[pos] = choix
                codes_selectionnes.add(choix)
            else:
                selection_finale[pos] = None

    assert selection_finale[0] and selection_finale[3], "Positions 1 et 4 doivent contenir les automatismes du thème courant."

    selection_finale = [code for code in selection_finale if code is not None]
    # Retourner la liste finale d'automatismes (longueur <= 6)
    return selection_finale
