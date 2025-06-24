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

    # Étape 1 : sélection des automatismes du thème courant
    auto1, auto2 = None, None
    if theme:
        theme_autos = choisir_2_auto_valide(theme)
        if len(theme_autos) >= 2:
            auto1, auto2 = theme_autos[:2]
        elif len(theme_autos) == 1:
            auto1 = auto2 = theme_autos[0]  # répéter si un seul
        if auto1:
            codes_selectionnes.add(auto1)
        if auto2:
            codes_selectionnes.add(auto2)

    # Étape 2 : choix de 2 autres thèmes
    autres_themes = [t for t in set(data['Code'].str[0]) if t != theme]
    random.shuffle(autres_themes)
    candidats_groupes = []

    for t in autres_themes:
        valides = choisir_2_auto_valide(t)
        if len(valides) >= 2:
            candidats_groupes.append((t, valides[:2]))
        elif len(valides) == 1:
            candidats_groupes.append((t, [valides[0]]))
        if sum(len(g[1]) for g in candidats_groupes) >= 4:
            break

    # Compléter avec autres automatismes peu vus si insuffisants
    if sum(len(g[1]) for g in candidats_groupes) < 4:
        reste = data[data['Code'].apply(lambda c: peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes)]
        for _, row in reste.iterrows():
            t = row['Code'][0]
            if t != theme:
                candidats_groupes.append((t, [row['Code']]))
                codes_selectionnes.add(row['Code'])
                if sum(len(g[1]) for g in candidats_groupes) >= 4:
                    break

    # Étape 3 : placement strict A1, B1, C1, A2, B2, C2 avec A = thème semaine
    ordered = [None] * 6
    if auto1:
        ordered[0] = auto1
    if auto2:
        ordered[3] = auto2

    pos = [1, 2, 4, 5]
    i = 0
    for _, groupe in candidats_groupes:
        for code in groupe:
            while i < len(pos) and ordered[pos[i]] is not None:
                i += 1
            if i < len(pos):
                ordered[pos[i]] = code
                codes_selectionnes.add(code)
                i += 1

    # Dernier remplissage si trous
    if None in ordered:
        reste_final = data[data['Code'].apply(lambda c: peut_etre_place(c) and used_codes[c] < 3 and c not in codes_selectionnes)]
        for _, row in reste_final.iterrows():
            for i in range(6):
                if ordered[i] is None:
                    ordered[i] = row['Code']
                    codes_selectionnes.add(row['Code'])
                    break

    return ordered
