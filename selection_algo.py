# selection_algo.py
from collections import defaultdict
import random

def get_espacement_fibonacci(occurrence):
    """Retourne l'espacement basé sur la suite de Fibonacci pour une occurrence donnée"""
    fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34]  # Extensible si besoin
    if occurrence <= len(fibonacci):
        return fibonacci[occurrence - 1]
    return fibonacci[-1]  # Dernier espacement si on dépasse

def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel, min_espacement_rappel):
    if not semaines_precedentes:
        return True
    
    ecart = semaine_actuelle - max(semaines_precedentes)
    
    # Pour les rappels, utiliser l'espacement minimum fixe
    if est_rappel:
        return ecart >= min_espacement_rappel
    
    # Pour les automatismes normaux, utiliser Fibonacci
    occurrence = len(semaines_precedentes) + 1  # Prochaine occurrence
    espacement_requis = get_espacement_fibonacci(occurrence)
    
    return ecart >= espacement_requis

def peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes, 
                   min_espacement_rappel, nb_automatismes):
    """Fonction utilitaire pour vérifier si un automatisme peut être placé"""
    row = data[data['Code'] == code].iloc[0]
    theme_code = row['Code'][0]
    est_rappel = row['Rappel']
    semaines_precedentes = auto_weeks.get(code, [])
    
    # Vérifier les limites d'usage selon le mode et le type
    max_usage = 2 if est_rappel and nb_automatismes == 6 else \
                3 if est_rappel and nb_automatismes == 9 else \
                4 if nb_automatismes == 6 else 6
    
    if used_codes[code] >= max_usage:
        return False
    
    # Pour les non-rappels, vérifier que le thème a été abordé
    if not est_rappel and theme_code not in themes_passes:
        return False
    
    # Vérifier l'espacement
    return respecte_espacement(semaines_precedentes, semaine, est_rappel, min_espacement_rappel)

def get_theme_semaine_plus_2(themes_progression, semaine_actuelle):
    """Retourne le thème qui sera étudié dans 2 semaines"""
    if semaine_actuelle + 2 <= len(themes_progression):
        return themes_progression[semaine_actuelle + 1]  # Index 0-based
    return None

def selectionner_automatismes_theme_courant(
    data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes=6
):
    """Sélectionne les automatismes du thème courant (ligne 1)"""
    selection_finale = [None] * nb_automatismes

    # D'abord, essayer avec les automatismes qui respectent l'espacement
    theme_autos_optimaux = [
        c for c in data[data['Code'].str.startswith(theme)]['Code']
        if peut_etre_place(c, data, semaine, auto_weeks, used_codes, themes_passes,
                          min_espacement_rappel, nb_automatismes)
    ]
    
    # Si pas assez d'automatismes optimaux, prendre tous ceux du thème (sans contrainte d'espacement)
    if len(theme_autos_optimaux) < (2 if nb_automatismes == 6 else 3):
        tous_theme_autos = data[data['Code'].str.startswith(theme)]['Code'].tolist()
        theme_autos = theme_autos_optimaux + [
            c for c in tous_theme_autos 
            if c not in theme_autos_optimaux
        ]
    else:
        theme_autos = theme_autos_optimaux

    # Placement selon le nombre d'automatismes - LIGNE 1
    if nb_automatismes == 6:
        # Mode 2x3 : positions 0, 1, 2 (première ligne)
        positions_theme = [0, 1, 2]
        nb_positions = 2  # On n'utilise que 2 positions sur les 3
    else:
        # Mode 3x3 : positions 0, 1, 2 (première ligne)
        positions_theme = [0, 1, 2]
        nb_positions = 3
    
    # Remplir les positions en répétant cycliquement les automatismes disponibles
    if theme_autos:
        for i in range(nb_positions):
            pos = positions_theme[i]
            # Utiliser l'opérateur modulo pour répéter cycliquement
            selection_finale[pos] = theme_autos[i % len(theme_autos)]

    return selection_finale

def selectionner_automatismes_theme_plus_2(
    data, semaine, theme_plus_2, auto_weeks, used_codes, min_espacement_rappel, 
    themes_passes, nb_automatismes=6
):
    """Sélectionne les automatismes du thème semaine+2 (ligne 2) - diagnostic/réactivation"""
    selection_finale = [None] * nb_automatismes
    
    if not theme_plus_2:
        return selection_finale
    
    # Prendre TOUS les automatismes du thème +2 (même si pas encore vu)
    # car c'est du diagnostic/réactivation
    theme_plus_2_autos = data[data['Code'].str.startswith(theme_plus_2)]['Code'].tolist()
    
    # Filtrer seulement par usage et espacement, pas par thème vu
    theme_plus_2_disponibles = []
    for code in theme_plus_2_autos:
        row = data[data['Code'] == code].iloc[0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        
        # Vérifier les limites d'usage
        max_usage = 2 if est_rappel and nb_automatismes == 6 else \
                    3 if est_rappel and nb_automatismes == 9 else \
                    4 if nb_automatismes == 6 else 6
        
        if (used_codes[code] < max_usage and 
            respecte_espacement(semaines_precedentes, semaine, est_rappel, min_espacement_rappel)):
            theme_plus_2_disponibles.append(code)
    
    # Si pas assez d'automatismes disponibles, prendre tous ceux du thème +2
    if len(theme_plus_2_disponibles) < (2 if nb_automatismes == 6 else 3):
        theme_plus_2_disponibles = theme_plus_2_autos
    
    # Placement selon le nombre d'automatismes - LIGNE 2
    if nb_automatismes == 6:
        # Mode 2x3 : position 2 (reste de ligne 1) + positions 3, 4 (début ligne 2)
        positions_theme_plus_2 = [2, 3, 4]
        nb_positions = 2  # On n'utilise que 2 positions sur les 3
        start_idx = 1  # Commencer par la position 3 (index 1 dans la liste)
    else:
        # Mode 3x3 : positions 3, 4, 5 (deuxième ligne complète)
        positions_theme_plus_2 = [3, 4, 5]
        nb_positions = 3
        start_idx = 0
    
    # Remplir les positions
    if theme_plus_2_disponibles:
        for i in range(nb_positions):
            pos = positions_theme_plus_2[start_idx + i]
            selection_finale[pos] = theme_plus_2_disponibles[i % len(theme_plus_2_disponibles)]

    return selection_finale

def selectionner_automatismes_autres_themes(
    data, semaine, theme_courant, theme_plus_2, auto_weeks, used_codes, codes_selectionnes,
    min_espacement_rappel, themes_passes, nb_automatismes=6
):
    """Sélectionne les automatismes des autres thèmes (ligne 3) selon les contraintes initiales"""
    selection_finale = [None] * nb_automatismes
    
    # Définir les positions pour les autres thèmes - LIGNE 3
    if nb_automatismes == 6:
        # Mode 2x3 : position 5 (reste de ligne 2)
        positions_autres = [5]
    else:
        # Mode 3x3 : positions 6, 7, 8 (troisième ligne complète)
        positions_autres = [6, 7, 8]
    
    # Créer une liste de tous les candidats valides (rappels ou thèmes déjà vus)
    # Exclure le thème courant et le thème +2
    tous_candidats = []
    for code in data['Code']:
        if (code not in codes_selectionnes and 
            peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes,
                           min_espacement_rappel, nb_automatismes)):
            
            row = data[data['Code'] == code].iloc[0]
            theme_code = row['Code'][0]
            est_rappel = row['Rappel']
            
            # Exclure les automatismes du thème courant et du thème +2
            if theme_code not in [theme_courant, theme_plus_2]:
                # Accepter si c'est un rappel OU si le thème a déjà été vu
                if est_rappel or theme_code in themes_passes:
                    tous_candidats.append(code)
    
    # Mélanger les candidats pour la diversité
    random.shuffle(tous_candidats)
    
    # Assigner aux positions disponibles
    for i, pos in enumerate(positions_autres):
        if i < len(tous_candidats):
            selection_finale[pos] = tous_candidats[i]

    return selection_finale

def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
    themes_passes, themes_progression, nb_automatismes=6
):
    """
    Nouvelle logique à 3 lignes :
    - Ligne 1 : Thème courant
    - Ligne 2 : Thème semaine+2 (diagnostic/réactivation)  
    - Ligne 3 : Autres thèmes (contraintes habituelles)
    """
    
    # Obtenir le thème de la semaine +2
    theme_plus_2 = get_theme_semaine_plus_2(themes_progression, semaine)
    
    # Ligne 1 : Automatismes du thème courant
    selection_ligne_1 = selectionner_automatismes_theme_courant(
        data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes
    )
    codes_selectionnes = set([c for c in selection_ligne_1 if c])
    
    # Ligne 2 : Automatismes du thème semaine+2
    selection_ligne_2 = selectionner_automatismes_theme_plus_2(
        data, semaine, theme_plus_2, auto_weeks, used_codes, min_espacement_rappel, 
        themes_passes, nb_automatismes
    )
    codes_selectionnes.update([c for c in selection_ligne_2 if c])
    
    # Ligne 3 : Autres thèmes avec contraintes habituelles
    selection_ligne_3 = selectionner_automatismes_autres_themes(
        data, semaine, theme, theme_plus_2, auto_weeks, used_codes, codes_selectionnes,
        min_espacement_rappel, themes_passes, nb_automatismes
    )
    
    # Fusion des trois lignes
    selection_finale = [None] * nb_automatismes
    for i in range(nb_automatismes):
        if selection_ligne_1[i]:
            selection_finale[i] = selection_ligne_1[i]
        elif selection_ligne_2[i]:
            selection_finale[i] = selection_ligne_2[i]
        elif selection_ligne_3[i]:
            selection_finale[i] = selection_ligne_3[i]
    
    # Compléter les cases vides restantes si nécessaire
    for i in range(nb_automatismes):
        if selection_finale[i] is None:
            # Chercher n'importe quel automatisme disponible
            candidats_fallback = [
                c for c in data['Code']
                if (c not in selection_finale and
                    respecte_espacement(auto_weeks.get(c, []), semaine, 
                                      data[data['Code'] == c]['Rappel'].iloc[0], 
                                      min_espacement_rappel))
            ]
            
            if candidats_fallback:
                choix = random.choice(candidats_fallback)
                selection_finale[i] = choix

    return selection_finale
