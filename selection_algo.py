from collections import defaultdict
import random


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

    def peut_etre_place(code):
        row = data[data['Code'] == code].iloc[0]
        theme_code = row['Code'][0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        if not est_rappel and theme_code not in themes_passes:
            return False
        return respecte_espacement(semaines_precedentes, semaine, est_rappel,
                                   min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3)

    def choisir_2_auto_valide(theme_prefix):
        candidats = data[data['Code'].str.startswith(theme_prefix)].sort_values('Num')
        valides = [row['Code'] for _, row in candidats.iterrows()
                   if peut_etre_place(row['Code']) and used_codes[row['Code']] < 3 and row['Code'] not in codes_selectionnes]
        return valides

    # Étape 1 : choisir auto1 et auto2 (thème courant)
    auto1, auto2 = None, None
    if theme:
        theme_autos = choisir_2_auto_valide(theme)
        if len(theme_autos) >= 2:
            auto1, auto2 = theme_autos[:2]
            codes_selectionnes.update([auto1, auto2])

    # Étape 2 : choisir d'autres thèmes pour compléter les paires
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    groupes = []

    for t in autres_themes:
        valides = choisir_2_auto_valide(t)
        if len(valides) >= 2:
            groupes.append(valides[:2])
        elif len(valides) == 1:
            groupes.append([valides[0]])
        if sum(len(g) for g in groupes) >= 4:
            break

    # Complétion si nécessaire avec un 4e thème
    if sum(len(g) for g in groupes) < 4:
        for t in autres_themes:
            valides = choisir_2_auto_valide(t)
            for v in valides:
                if v not in codes_selectionnes:
                    groupes.append([v])
                    if sum(len(g) for g in groupes) >= 4:
                        break
            if sum(len(g) for g in groupes) >= 4:
                break

    # Placement : A1, B1, C1, A2, B2, C2
    placement = []
    if auto1:
        placement.append(auto1)
    if len(groupes) > 0 and len(groupes[0]) >= 1:
        placement.append(groupes[0][0])
    if len(groupes) > 1 and len(groupes[1]) >= 1:
        placement.append(groupes[1][0])
    if auto2:
        placement.append(auto2)
    if len(groupes) > 0 and len(groupes[0]) >= 2:
        placement.append(groupes[0][1])
    elif len(groupes) > 2 and len(groupes[2]) >= 1:
        placement.append(groupes[2][0])
    if len(groupes) > 1 and len(groupes[1]) >= 2:
        placement.append(groupes[1][1])
    elif len(groupes) > 3 and len(groupes[3]) >= 1:
        placement.append(groupes[3][0])

    for idx, code in enumerate(placement[:6]):
        selection_finale[idx] = code
        codes_selectionnes.add(code)

    return selection_finale
