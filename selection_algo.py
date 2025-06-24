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
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
    themes_passes
):
    selection_finale = [None] * 6
    codes_selectionnes = set()

    # 1. Automatisme du thème courant
    auto1, auto2 = None, None
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
            elif len(tous_candidats) >= 2:
                auto1 = tous_candidats[0]['Code']
                auto2 = tous_candidats[1]['Code']
            elif len(tous_candidats) == 1:
                auto1 = auto2 = tous_candidats[0]['Code']

            if auto1:
                selection_finale[0] = auto1
                codes_selectionnes.add(auto1)
            if auto2:
                selection_finale[3] = auto2
                codes_selectionnes.add(auto2)

    # 2. Automatisme rappels
    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    candidats = []
    for _, row in data.iterrows():
        code = row['Code']
        if code in codes_selectionnes:
            continue
        if peut_etre_place(code):
            candidats.append(row)

    candidats.sort(key=lambda r: used_codes[r['Code']])

    for i in range(6):
        if selection_finale[i] is None and candidats:
            choix = candidats.pop(0)['Code']
            selection_finale[i] = choix
            codes_selectionnes.add(choix)

    # Nettoyage et retour
    selection_finale = [code for code in selection_finale if code is not None]
    return selection_finale
