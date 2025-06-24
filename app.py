def selectionner_automatismes(data, semaine_idx, theme, auto_weeks, used_codes, next_index_by_theme):
    deja_abordes = [st.session_state.sequences[k] for k in range(semaine_idx+1) if st.session_state.sequences[k]]
    themes_rappel = data[data['Rappel']]['Sous-Thème'].unique().tolist()
    pool = list(set(deja_abordes + themes_rappel))

    candidats = data[data['Sous-Thème'].isin(pool)].copy()
    candidats = candidats[(candidats['Rappel']) | (candidats['Sous-Thème'].isin(deja_abordes))]
    candidats['Used'] = candidats['Code'].map(lambda c: used_codes[c])
    candidats = candidats[candidats['Used'] < 4]
    candidats = candidats[candidats['Code'].apply(lambda c: respecte_espacement(auto_weeks[c], semaine_idx, data.set_index('Code').loc[c, 'Rappel']))]

    # Initialiser la sélection finale avec 6 positions
    selection_finale = [None] * 6
    codes_selectionnes = set()
    
    if theme:
        # Sélectionner les automatismes du thème principal
        theme_df = candidats[(candidats['Sous-Thème'] == theme) & (~candidats['Rappel'])].sort_values('Num')
        
        # Position 1 : Premier automatisme du thème
        attendu_1 = next_index_by_theme[theme]
        for _, row in theme_df.iterrows():
            if int(row['Num']) == attendu_1 and row['Code'] not in codes_selectionnes:
                selection_finale[0] = row
                codes_selectionnes.add(row['Code'])
                next_index_by_theme[theme] += 1
                break
        
        # Position 4 : Deuxième automatisme du thème
        attendu_2 = next_index_by_theme[theme]
        for _, row in theme_df.iterrows():
            if int(row['Num']) == attendu_2 and row['Code'] not in codes_selectionnes:
                selection_finale[3] = row
                codes_selectionnes.add(row['Code'])
                next_index_by_theme[theme] += 1
                break
        
        # Si pas assez d'automatismes dans l'ordre, prendre les suivants disponibles
        if selection_finale[0] is None or selection_finale[3] is None:
            theme_disponibles = theme_df[~theme_df['Code'].isin(codes_selectionnes)]
            for _, row in theme_disponibles.iterrows():
                if selection_finale[0] is None:
                    selection_finale[0] = row
                    codes_selectionnes.add(row['Code'])
                elif selection_finale[3] is None:
                    selection_finale[3] = row
                    codes_selectionnes.add(row['Code'])
                    break

    # Remplir les positions restantes (2, 3, 5, 6) avec d'autres thèmes
    autres_candidats = candidats[~candidats['Code'].isin(codes_selectionnes)]
    
    # Grouper par thème pour diversifier
    groupes_autres = autres_candidats.groupby('Sous-Thème')
    autres_selection = []
    
    for sous_theme, groupe in groupes_autres:
        if sous_theme != theme:  # Éviter le thème principal déjà traité
            meilleur = groupe.sort_values('Num').iloc[0]
            autres_selection.append(meilleur)
    
    # Mélanger pour éviter un ordre prévisible
    random.shuffle(autres_selection)
    
    # Remplir les positions libres
    positions_libres = [i for i in [1, 2, 4, 5] if selection_finale[i] is None]
    
    for i, pos in enumerate(positions_libres):
        if i < len(autres_selection):
            selection_finale[pos] = autres_selection[i]
            codes_selectionnes.add(autres_selection[i]['Code'])
    
    # Compléter avec d'autres automatismes si nécessaire
    tentatives = 0
    while None in selection_finale and tentatives < 50:
        restants = candidats[~candidats['Code'].isin(codes_selectionnes)]
        if restants.empty:
            break
            
        for pos in range(6):
            if selection_finale[pos] is None:
                for _, row in restants.iterrows():
                    if (row['Code'] not in codes_selectionnes and 
                        respecte_espacement(auto_weeks[row['Code']], semaine_idx, row['Rappel'])):
                        selection_finale[pos] = row
                        codes_selectionnes.add(row['Code'])
                        break
                break
        tentatives += 1
    
    # Convertir en codes et nettoyer les None
    codes_finaux = []
    for item in selection_finale:
        if item is not None:
            codes_finaux.append(item['Code'])
    
    return codes_finaux[:6]
