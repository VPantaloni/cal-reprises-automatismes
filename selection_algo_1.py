
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

def selectionner_automatismes_theme(
    data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes=6
):
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

    # Placement selon le nombre d'automatismes
    if nb_automatismes == 6:
        # Mode 2x3 : positions 0 et 3 - TOUJOURS remplir
        positions_theme = [0, 3]
        nb_positions = 2
    else:
        # Mode 3x3 : positions 0, 3, 6 - TOUJOURS remplir
        positions_theme = [0, 3, 6]
        nb_positions = 3
    
    # Remplir les positions en répétant cycliquement les automatismes disponibles
    if theme_autos:
        for i, pos in enumerate(positions_theme):
            # Utiliser l'opérateur modulo pour répéter cycliquement
            selection_finale[pos] = theme_autos[i % len(theme_autos)]

    return selection_finale
def selectionner_automatismes_autres_themes(
    data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
    min_espacement_rappel, themes_passes, positions, nb_automatismes=6
):
    """Version modifiée : sélectionne individuellement chaque automatisme parmi tous les candidats valides"""
    selection = [None] * nb_automatismes

    # Créer une liste de tous les candidats valides (rappels ou thèmes déjà vus)
    tous_candidats = []
    for code in data['Code']:
        if (code not in codes_selectionnes and 
            peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes,
                           min_espacement_rappel, nb_automatismes)):
            
            row = data[data['Code'] == code].iloc[0]
            theme_code = row['Code'][0]
            est_rappel = row['Rappel']
            
            # Accepter si c'est un rappel OU si le thème a déjà été vu
            if est_rappel or theme_code in themes_passes:
                tous_candidats.append(code)
    
    # Mélanger les candidats pour la diversité
    random.shuffle(tous_candidats)
    
    # Assigner aux positions disponibles
    candidat_index = 0
    for pos in positions:
        if candidat_index < len(tous_candidats):
            selection[pos] = tous_candidats[candidat_index]
            codes_selectionnes.add(tous_candidats[candidat_index])
            candidat_index += 1

    return selection

def selectionner_automatismes(
    data, semaine, theme, auto_weeks, used_codes, next_index_by_theme,
    min_espacement_rappel, espacement_min2, espacement_max2, espacement_min3, espacement_max3,
    themes_passes, nb_automatismes=6
):
    # Note: espacement_min2, max2, min3, max3 ne sont plus utilisés avec Fibonacci
    # mais gardés pour compatibilité avec l'interface
    
    # Sélection des automatismes du thème principal
    base = selectionner_automatismes_theme(
        data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes
    )
    codes_selectionnes = set([c for c in base if c])

    # Définir les positions pour les autres thèmes selon le mode
    if nb_automatismes == 6:
        # Mode 2x3 : positions restantes [1,2,4,5]
        positions_autres = [1, 2, 4, 5]
    else:
        # Mode 3x3 : positions restantes [1,2,4,5,7,8]
        positions_autres = [1, 2, 4, 5, 7, 8]

    # Compléter avec d'autres automatismes (rappels ou thèmes déjà vus)
    complement = selectionner_automatismes_autres_themes(
        data, semaine, theme, auto_weeks, used_codes, codes_selectionnes,
        min_espacement_rappel, themes_passes, positions_autres, nb_automatismes
    )

    # Fusion finale
    selection_finale = [None] * nb_automatismes
    for i in range(nb_automatismes):
        if base[i]:
            selection_finale[i] = base[i]
        elif complement[i]:
            selection_finale[i] = complement[i]

    # Compléter les cases vides - PRIORITÉ : grille complète
    for i in range(nb_automatismes):
        if selection_finale[i] is None:
            # 1. D'abord, chercher des automatismes sous-utilisés (non-rappels)
            target_usage = 4 if nb_automatismes == 6 else 6
            candidats_sous_utilises = [
                c for c in data['Code']
                if (c not in selection_finale and 
                    not data[data['Code'] == c]['Rappel'].iloc[0] and  # Pas un rappel
                    used_codes[c] < target_usage and  # Sous-utilisé
                    respecte_espacement(auto_weeks.get(c, []), semaine, False, min_espacement_rappel))
            ]
            
            # 2. Si pas assez de sous-utilisés, prendre tous les non-rappels disponibles
            if not candidats_sous_utilises:
                candidats_sous_utilises = [
                    c for c in data['Code']
                    if (c not in selection_finale and 
                        not data[data['Code'] == c]['Rappel'].iloc[0] and  # Pas un rappel
                        respecte_espacement(auto_weeks.get(c, []), semaine, False, min_espacement_rappel))
                ]
            
            # 3. En dernier recours, prendre n'importe quel automatisme (même rappels)
            if not candidats_sous_utilises:
                candidats_sous_utilises = [
                    c for c in data['Code']
                    if (c not in selection_finale and
                        respecte_espacement(auto_weeks.get(c, []), semaine, 
                                          data[data['Code'] == c]['Rappel'].iloc[0], 
                                          min_espacement_rappel))
                ]
            
            if candidats_sous_utilises:
                choix = random.choice(candidats_sous_utilises)
                selection_finale[i] = choix

    return selection_finale
