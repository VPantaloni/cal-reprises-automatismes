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

def get_theme_diagnostic(themes_progression, semaine_actuelle, theme_courant):
    """
    Retourne le thème pour la ligne diagnostic avec souplesse :
    1. Essaie semaine S+2
    2. Si identique au thème courant, essaie S+3
    3. Sinon essaie S+1
    """
    if not themes_progression or semaine_actuelle >= len(themes_progression):
        return None
    
    # Essayer S+2 d'abord
    if semaine_actuelle + 2 < len(themes_progression):
        theme_s2 = themes_progression[semaine_actuelle + 1]  # Index 0-based
        if theme_s2 != theme_courant:
            return theme_s2
    
    # Si S+2 = thème courant ou inexistant, essayer S+3
    if semaine_actuelle + 3 < len(themes_progression):
        theme_s3 = themes_progression[semaine_actuelle + 2]  # Index 0-based
        if theme_s3 != theme_courant:
            return theme_s3
    
    # Sinon essayer S+1
    if semaine_actuelle + 1 < len(themes_progression):
        theme_s1 = themes_progression[semaine_actuelle]  # Index 0-based
        if theme_s1 != theme_courant:
            return theme_s1
    
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

def selectionner_automatismes_theme_diagnostic(
    data, semaine, theme_diagnostic, auto_weeks, used_codes, min_espacement_rappel, 
    themes_passes, nb_automatismes=6
):
    """
    Sélectionne les automatismes du thème diagnostic (ligne 2) 
    Permet les répétitions si premières apparitions
    """
    selection_finale = [None] * nb_automatismes
    
    if not theme_diagnostic:
        return selection_finale
    
    # Prendre TOUS les automatismes du thème diagnostic
    theme_diagnostic_autos = data[data['Code'].str.startswith(theme_diagnostic)]['Code'].tolist()
    
    # Séparer selon les premières apparitions et les répétitions
    premieres_apparitions = []
    autres_disponibles = []
    
    for code in theme_diagnostic_autos:
        row = data[data['Code'] == code].iloc[0]
        est_rappel = row['Rappel']
        semaines_precedentes = auto_weeks.get(code, [])
        
        # Vérifier les limites d'usage
        max_usage = 2 if est_rappel and nb_automatismes == 6 else \
                    3 if est_rappel and nb_automatismes == 9 else \
                    4 if nb_automatismes == 6 else 6
        
        # Si première apparition, priorité absolue (même sans espacement)
        if not semaines_precedentes and used_codes[code] < max_usage:
            premieres_apparitions.append(code)
        # Sinon, vérifier espacement classique
        elif (used_codes[code] < max_usage and 
              respecte_espacement(semaines_precedentes, semaine, est_rappel, min_espacement_rappel)):
            autres_disponibles.append(code)
    
    # Combiner : priorité aux premières apparitions
    candidats_diagnostic = premieres_apparitions + autres_disponibles
    
    # Si pas assez, prendre tous les automatismes du thème (souplesse maximale)
    if len(candidats_diagnostic) < (2 if nb_automatismes == 6 else 3):
        candidats_diagnostic = theme_diagnostic_autos
    
    # Définir les positions selon le mode
    if nb_automatismes == 6:
        # Mode 2x3 : positions 2, 3 
        positions_diagnostic = [2, 3]
        nb_positions = 2
    else:
        # Mode 3x3 : positions 3, 4, 5 (deuxième ligne complète)
        positions_diagnostic = [3, 4, 5]
        nb_positions = 3
    
    # Remplir les positions - PERMET LES RÉPÉTITIONS
    if candidats_diagnostic:
        for i in range(nb_positions):
            pos = positions_diagnostic[i]
            selection_finale[pos] = candidats_diagnostic[i % len(candidats_diagnostic)]

    return selection_finale

def selectionner_automatismes_autres_themes(
    data, semaine, theme_courant, theme_diagnostic, auto_weeks, used_codes, codes_selectionnes,
    min_espacement_rappel, themes_passes, nb_automatismes=6
):
    """Sélectionne les automatismes des autres thèmes (ligne 3) selon les contraintes initiales"""
    selection_finale = [None] * nb_automatismes
    
    # Définir les positions pour les autres thèmes - LIGNE 3
    if nb_automatismes == 6:
        # Mode 2x3 : positions 4, 5
        positions_autres = [4, 5]
    else:
        # Mode 3x3 : positions 6, 7, 8 (troisième ligne complète)
        positions_autres = [6, 7, 8]
    
    # Créer une liste de tous les candidats valides (rappels ou thèmes déjà vus)
    # Exclure le thème courant et le thème diagnostic
    tous_candidats = []
    for code in data['Code']:
        if (code not in codes_selectionnes and 
            peut_etre_place(code, data, semaine, auto_weeks, used_codes, themes_passes,
                           min_espacement_rappel, nb_automatismes)):
            
            row = data[data['Code'] == code].iloc[0]
            theme_code = row['Code'][0]
            est_rappel = row['Rappel']
            
            # Exclure les automatismes du thème courant et du thème diagnostic
            if theme_code not in [theme_courant, theme_diagnostic]:
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
    Nouvelle logique à 3 lignes avec souplesse :
    - Ligne 1 : Thème courant
    - Ligne 2 : Thème diagnostic (S+2, S+3 ou S+1 selon disponibilité)
    - Ligne 3 : Autres thèmes (contraintes habituelles)
    Permet les répétitions d'automatismes dans la même semaine
    """
    
    # Obtenir le thème diagnostic avec souplesse
    theme_diagnostic = get_theme_diagnostic(themes_progression, semaine, theme)
    
    # Ligne 1 : Automatismes du thème courant
    selection_ligne_1 = selectionner_automatismes_theme_courant(
        data, semaine, theme, auto_weeks, used_codes, min_espacement_rappel, themes_passes, nb_automatismes
    )
    codes_selectionnes = set([c for c in selection_ligne_1 if c])
    
    # Ligne 2 : Automatismes du thème diagnostic
    selection_ligne_2 = selectionner_automatismes_theme_diagnostic(
        data, semaine, theme_diagnostic, auto_weeks, used_codes, min_espacement_rappel, 
        themes_passes, nb_automatismes
    )
    # Ne pas ajouter à codes_selectionnes pour permettre les répétitions
    
    # Ligne 3 : Autres thèmes avec contraintes habituelles
    selection_ligne_3 = selectionner_automatismes_autres_themes(
        data, semaine, theme, theme_diagnostic, auto_weeks, used_codes, codes_selectionnes,
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
                if respecte_espacement(auto_weeks.get(c, []), semaine, 
                                     data[data['Code'] == c]['Rappel'].iloc[0], 
                                     min_espacement_rappel)
            ]
            
            if candidats_fallback:
                choix = random.choice(candidats_fallback)
                selection_finale[i] = choix

    return selection_finale
