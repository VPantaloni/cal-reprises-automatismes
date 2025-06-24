from collections import defaultdict

def selectionner_automatismes(data, semaine_idx, theme, auto_weeks, used_codes, next_index_by_theme,
                               min_espacement_rappel=1,
                               espacement_min2=2, espacement_max2=6,
                               espacement_min3=4, espacement_max3=10):
    def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel):
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

    selection_finale = [None] * 6
    codes_selectionnes = set()

    # AUTOMATISMES DU THÈME COURANT
    if theme:
        theme_autos = data[data['Code'].str.startswith(theme)].sort_values('Num')
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
            auto1, auto2 = candidats_prioritaires[:2]
        elif len(candidats_prioritaires) == 1:
            auto1 = candidats_prioritaires[0]
            auto2 = next((row for row in tous_candidats if row['Code'] != auto1['Code']), auto1)
        else:
            auto1 = tous_candidats[0]
            auto2 = tous_candidats[1] if len(tous_candidats) > 1 else tous_candidats[0]

        selection_finale[0] = auto1['Code']
        selection_finale[3] = auto2['Code']
        codes_selectionnes.update([auto1['Code'], auto2['Code']])

    # AUTOMATISMES EN RAPPEL
    themes_deja_abordes = set()
    for k in range(semaine_idx):
        if k < len(next_index_by_theme) and next_index_by_theme.get(k):
            themes_deja_abordes.add(next_index_by_theme[k])

    candidats_rappel = []
    for _, row in data.iterrows():
        code = row['Code']
        if code in codes_selectionnes:
            continue
        nb_vues = used_codes[code]
        besoin_revu = (row['Rappel'] and 0 < nb_vues < 2) or (not row['Rappel'] and 0 < nb_vues < 3)
        theme_de_lauto = code[0]
        if besoin_revu and (theme_de_lauto in themes_deja_abordes or row['Rappel']):
            if respecte_espacement(auto_weeks[code], semaine_idx, row['Rappel']):
                candidats_rappel.append(row)

    candidats_rappel.sort(key=lambda r: (
        used_codes[r['Code']],
        r['Code'][0] == theme,
        r['Rappel'],
        r['Num']
    ))

    positions_rappel = [i for i in range(6) if selection_finale[i] is None]
    candidat_idx = 0
    for pos in positions_rappel:
        if candidat_idx < len(candidats_rappel):
            candidat = candidats_rappel[candidat_idx]
            selection_finale[pos] = candidat['Code']
            codes_selectionnes.add(candidat['Code'])
            candidats_rappel = [c for c in candidats_rappel if c['Code'] != candidat['Code']]
            candidat_idx = 0

    # COMPLÉTION D'URGENCE
    for i in range(6):
        if selection_finale[i] is None:
            candidats_urgence = [
                row for _, row in data.iterrows()
                if row['Code'] not in codes_selectionnes and used_codes[row['Code']] < 5
            ]
            if candidats_urgence:
                candidat = min(candidats_urgence, key=lambda r: used_codes[r['Code']])
                selection_finale[i] = candidat['Code']
                codes_selectionnes.add(candidat['Code'])
            elif codes_selectionnes:
                selection_finale[i] = next(iter(codes_selectionnes))
            else:
                selection_finale[i] = data.iloc[0]['Code']

    return selection_finale
