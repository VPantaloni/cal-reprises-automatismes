import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from io import BytesIO

# ===== CONFIGURATION DES THÈMES =====
# Définition des sous-thèmes avec leurs emojis et couleurs
subthemes = [
    ("🔢", "#ac2747"), ("➗", "#be5770"), ("📏", "#cc6c1d"), ("🔷", "#d27c36"),
    ("⌚", "#dd9d68"), ("📐", "#16a34a"), ("🧊", "#44b56e"), ("📊", "#1975d1"),
    ("🎲", "#3384d6"), ("∝", "#8a38d2")
]

subtheme_emojis = [s[0] for s in subthemes]
subtheme_colors = dict(subthemes)

# Légendes des thèmes pour l'affichage
subtheme_legend = {
    "🔢": "Nombres entiers et décimaux", 
    "➗": "Fractions", 
    "📏": "Longueurs",
    "🔷": "Aires", 
    "⌚": "Temps", 
    "📐": "Étude de configurations planes",
    "🧊": "La vision dans l'espace", 
    "📊": "Organisation et gestion de données",
    "🎲": "Probabilités", 
    "∝": "Proportionnalité"
}

# ===== FONCTIONS UTILITAIRES =====

def respecte_espacement(semaines_precedentes, semaine_actuelle, est_rappel):
    """
    Vérifie si l'espacement entre les reprises d'un automatisme est respecté.
    
    Args:
        semaines_precedentes: Liste des semaines où l'automatisme a déjà été utilisé
        semaine_actuelle: Numéro de la semaine actuelle (0-31)
        est_rappel: Boolean indiquant si c'est un automatisme de rappel
    
    Returns:
        Boolean: True si l'espacement est respecté
    """
    if not semaines_precedentes:
        return True
    
    dernier_usage = max(semaines_precedentes)
    ecart = semaine_actuelle - dernier_usage
    
    # Règles d'espacement selon le type et le nombre d'utilisations
    if est_rappel:
        return ecart >= 2  # Au moins 2 semaines d'écart pour les rappels
    
    nb_utilisations = len(semaines_precedentes)
    if nb_utilisations == 1:
        return 2 <= ecart <= 4  # Entre 2 et 4 semaines après la 1ère utilisation
    elif nb_utilisations == 2:
        return 4 <= ecart <= 6  # Entre 4 et 6 semaines après la 2ème utilisation
    else:
        return False  # Pas plus de 3 utilisations

def charger_donnees():
    """
    Charge et traite le fichier CSV des automatismes.
    
    Returns:
        DataFrame: Données des automatismes avec colonnes ajoutées
    """
    try:
        data = pd.read_csv("Auto-6e.csv", sep=';', encoding='utf-8')
        data = data.dropna(subset=['Code', 'Automatisme'])
        
        # Extraction des informations du code
        data['Sous-Thème'] = data['Code'].str[0]  # Premier caractère = emoji du thème
        data['Couleur'] = data['Sous-Thème'].map(subtheme_colors)
        data['Rappel'] = data['Code'].str[1] == '↩'  # Deuxième caractère indique si c'est un rappel
        data['Num'] = data['Code'].str.extract(r'(\d+)$').astype(float)  # Numéro à la fin
        
        return data
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
        st.stop()

def afficher_legende():
    """Affiche la légende des thèmes dans un expander."""
    with st.expander("📖 Légende des thèmes"):
        cols = st.columns(5)
        for idx, (emoji, label) in enumerate(subtheme_legend.items()):
            with cols[idx % 5]:
                st.markdown(f"""
                    <div style='background:{subtheme_colors[emoji]}; padding:4px; 
                                border-radius:6px; color:white; font-size:0.85em;'>
                        <b>{emoji}</b> {label}
                    </div>
                """, unsafe_allow_html=True)

def selectionner_automatismes_pour_semaine(data, semaine_idx, theme_semaine, 
                                         auto_weeks, used_codes, next_index_by_theme):
    """
    Sélectionne les automatismes pour une semaine donnée.
    
    Args:
        data: DataFrame des automatismes
        semaine_idx: Index de la semaine (0-31)
        theme_semaine: Thème sélectionné pour cette semaine
        auto_weeks: Dictionnaire {code: [semaines]} des utilisations précédentes
        used_codes: Dictionnaire {code: nb_utilisations}
        next_index_by_theme: Dictionnaire {theme: prochain_index}
    
    Returns:
        DataFrame: DataFrame des automatismes sélectionnés
    """
    # 1. Déterminer le pool d'automatismes disponibles
    themes_deja_abordes = [st.session_state.sequences[k] for k in range(semaine_idx+1) 
                          if st.session_state.sequences[k]]
    themes_rappels = data[data['Rappel']]['Sous-Thème'].unique().tolist()
    pool_themes = list(set(themes_deja_abordes + themes_rappels))
    
    # 2. Filtrer les candidats selon les critères
    candidats = data[data['Sous-Thème'].isin(pool_themes)].copy()
    candidats = candidats[
        (candidats['Rappel']) | 
        (candidats['Sous-Thème'].isin(themes_deja_abordes))
    ]
    
    # 3. Appliquer les contraintes d'utilisation et d'espacement
    candidats['Used'] = candidats['Code'].map(lambda c: used_codes[c])
    candidats = candidats[candidats['Used'] < 4]  # Maximum 4 utilisations
    
    candidats = candidats[candidats['Code'].apply(
        lambda c: respecte_espacement(
            auto_weeks[c], 
            semaine_idx, 
            data.set_index('Code').loc[c, 'Rappel']
        )
    )]
    
    # 4. Sélection prioritaire selon le thème de la semaine
    selection = []
    
    if theme_semaine:
        # Chercher l'automatisme suivant du thème principal
        theme_df = candidats[
            (candidats['Sous-Thème'] == theme_semaine) & 
            (~candidats['Rappel'])
        ].sort_values('Num')
        
        attendu = next_index_by_theme[theme_semaine]
        for _, row in theme_df.iterrows():
            if int(row['Num']) == attendu:
                selection.append(row)
                next_index_by_theme[theme_semaine] += 1
                break
    
    # 5. Compléter avec d'autres thèmes (diversification)
    autres_candidats = candidats[~candidats['Code'].isin([r['Code'] for r in selection])]
    groupes_par_theme = autres_candidats.groupby('Sous-Thème')
    
    # Prendre le premier de chaque thème disponible
    divers = [groupe.sort_values('Num').iloc[0] for _, groupe in groupes_par_theme if not groupe.empty]
    random.shuffle(divers)
    selection.extend(divers[:5])  # Limiter à 5 pour avoir de la place
    
    # 6. Compléter jusqu'à 6 automatismes si possible
    tentatives = 0
    while len(selection) < 6 and tentatives < 50:
        restants = candidats[~candidats['Code'].isin([row['Code'] for row in selection])]
        for _, row in restants.iterrows():
            if row['Code'] not in [sel['Code'] for sel in selection]:
                if respecte_espacement(auto_weeks[row['Code']], semaine_idx, row['Rappel']):
                    selection.append(row)
                    break
        tentatives += 1
    
    # Retourner un DataFrame avec les 6 premiers automatismes
    return pd.DataFrame(selection).head(6)

def afficher_grille_selection(data, auto_weeks, used_codes, next_index_by_theme):
    """
    Affiche la grille de sélection des thèmes pour chaque semaine.
    """
    emoji_numeros = [f"S{i+1}" for i in range(32)]
    
    # Organisation en 4 lignes de 8 colonnes
    rows = [st.columns(8) for _ in range(4)]
    
    for i in range(32):
        row_idx = i // 8
        col_idx = i % 8
        col = rows[row_idx][col_idx]
        
        selected_theme = st.session_state.sequences[i]
        
        with col:
            # Affichage du numéro de semaine et du bouton thème
            emoji = selected_theme if selected_theme else "❓"
            st.markdown(f"<b>{emoji_numeros[i]}</b> ", unsafe_allow_html=True)
            
            # Bouton pour ouvrir le sélecteur de thème
            if st.button(emoji, key=f"pick_{i}"):
                st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)
            
            # Affichage de la grille de sélection de thèmes si ouverte
            if st.session_state.get(f"show_picker_{i}", False):
                picker_rows = [st.columns(3) for _ in range(4)]
                layout = [
                    ["🔢", "➗", ""],
                    ["📏", "🔷", "⌚"],
                    ["📐", "🧊", ""],
                    ["📊", "🎲", "∝"]
                ]
                for row, emojis in zip(picker_rows, layout):
                    for col_picker, icon in zip(row, emojis):
                        with col_picker:
                            if icon:
                                if st.button(f"{icon}", key=f"choose_{i}_{icon}", use_container_width=True):
                                    st.session_state.sequences[i] = icon
                                    st.session_state[f"show_picker_{i}"] = False
                                    st.rerun()
            
            # Sélection des automatismes pour cette semaine
            theme_semaine = st.session_state.sequences[i]
            
            # Appel de la fonction de sélection
            selection_df = selectionner_automatismes_pour_semaine(
                data, i, theme_semaine, auto_weeks, used_codes, next_index_by_theme
            )
            
            # Enregistrement de la sélection
            st.session_state.selection_by_week[i] = selection_df['Code'].tolist() if not selection_df.empty else []
            
            # Mise à jour des trackers
            for code in st.session_state.selection_by_week[i]:
                auto_weeks[code].append(i)
                used_codes[code] += 1

def afficher_grille_automatismes_compacte():
    """
    Affiche la grille compacte des automatismes avec 16 colonnes et 3 lignes par bloc.
    """
    st.markdown("### 📋 Grille des automatismes")
    
    # Traitement par bloc de 8 semaines
    for bloc in range(4):
        debut_semaine = bloc * 8
        fin_semaine = debut_semaine + 8
        
        st.markdown(f"**Semaines {debut_semaine + 1} à {fin_semaine}**")
        
        # Création de la grille 16 colonnes x 3 lignes
        for ligne_auto in range(3):  # 3 lignes d'automatismes
            cols = st.columns(16)  # 16 colonnes (2 par semaine)
            
            for semaine_dans_bloc in range(8):  # 8 semaines dans le bloc
                semaine_globale = debut_semaine + semaine_dans_bloc
                
                # Récupération des automatismes pour cette semaine
                automatismes = st.session_state.selection_by_week[semaine_globale] if semaine_globale < len(st.session_state.selection_by_week) else []
                
                # Affichage de 2 automatismes par semaine (colonnes paires)
                for col_auto in range(2):  # 2 colonnes par semaine
                    col_index = semaine_dans_bloc * 2 + col_auto
                    auto_index = ligne_auto * 2 + col_auto  # Index de l'automatisme (0-5)
                    
                    with cols[col_index]:
                        if auto_index < len(automatismes):
                            code = automatismes[auto_index]
                            # Récupération de la couleur depuis les données
                            couleur = "#666666"  # Couleur par défaut
                            try:
                                data = charger_donnees()
                                row = data[data['Code'] == code]
                                if not row.empty:
                                    couleur = row.iloc[0]['Couleur']
                                    automatisme_text = row.iloc[0]['Automatisme']
                                else:
                                    automatisme_text = code
                            except:
                                automatisme_text = code
                            
                            st.markdown(f"""
                                <div title="{automatisme_text}" 
                                     style='padding:1px; margin:1px; border: 2px solid {couleur}; 
                                            background:transparent; border-radius:3px; 
                                            font-size:0.7em; font-weight:bold; 
                                            text-align:center; cursor:help; 
                                            min-height:20px; line-height:18px;'>
                                    {code}
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            # Case vide
                            st.markdown(f"""
                                <div style='padding:1px; margin:1px; border: 1px dashed #ccc; 
                                            background:transparent; border-radius:3px; 
                                            font-size:0.7em; text-align:center; 
                                            min-height:20px; line-height:18px;'>
                                    
                                </div>
                            """, unsafe_allow_html=True)
        
        st.markdown("---")  # Séparateur entre les blocs

def generer_selection_aleatoire():
    """Génère une sélection aléatoire de thèmes pour toutes les semaines."""
    nouvelle_sequence = []
    theme_precedent = None
    
    for _ in range(32):
        # Évite de répéter le même thème consécutivement
        options = [s for s in subtheme_emojis if s != theme_precedent]
        choix = random.choice(options)
        nouvelle_sequence.append(choix)
        theme_precedent = choix
    
    return nouvelle_sequence

# ===== APPLICATION PRINCIPALE =====

def main():
    """Fonction principale de l'application Streamlit."""
    
    # Configuration de la page
    st.set_page_config(layout="wide", page_title="Reprises d'automatismes 6e")
    st.title("📅 Reprises d'automatismes mathématiques en 6e")
    
    # Chargement des données
    data = charger_donnees()
    
    # Mode nuit (sidebar)
    dark_mode = st.sidebar.checkbox("🌙 Mode nuit")
    if dark_mode:
        st.markdown("""
            <style>
            body, .stApp { background-color: #0e1117; color: white; }
            .stButton>button { background-color: #333; color: white; }
            </style>
        """, unsafe_allow_html=True)
    
    # Affichage de la légende
    afficher_legende()
    
    # Initialisation des états de session
    if 'sequences' not in st.session_state:
        # Séquence par défaut avec quelques thèmes prédéfinis
        st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * 24
    
    if 'selection_by_week' not in st.session_state:
        st.session_state.selection_by_week = [[] for _ in range(32)]
    
    # Boutons d'action
    col_random, col_export = st.columns([2, 2])
    
    with col_random:
        if st.button("🎲 Remplir aléatoirement"):
            st.session_state.sequences = generer_selection_aleatoire()
            st.rerun()
    
    # Initialisation des trackers pour l'algorithme
    auto_weeks = defaultdict(list)  # {code: [semaines_utilisees]}
    used_codes = defaultdict(int)   # {code: nb_utilisations}
    next_index_by_theme = defaultdict(lambda: 1)  # {theme: prochain_numero}
    
    # Affichage de la grille de sélection des thèmes
    afficher_grille_selection(data, auto_weeks, used_codes, next_index_by_theme)
    
    # Affichage de la grille compacte des automatismes
    afficher_grille_automatismes_compacte()
    
    # ===== SECTION RÉCAPITULATIF =====
    st.markdown("---")
    st.markdown("## 🔍 Lecture par automatisme")
    
    # Création du récapitulatif
    recap_data = []
    for _, row in data.iterrows():
        code = row['Code']
        semaines_utilisees = [f"S{w+1}" for w in auto_weeks.get(code, [])]
        recap_data.append({
            "Code": code,
            "Automatisme": row['Automatisme'],
            "Semaines": ", ".join(semaines_utilisees),
            "Couleur": row['Couleur']
        })
    
    # Affichage du récapitulatif
    recap_df = pd.DataFrame(recap_data)
    for _, row in recap_df.iterrows():
        st.markdown(f"""
            <div style='padding:2px; margin:2px; border: 3px solid {row['Couleur']}; 
                        background:transparent; border-radius:4px; font-size:0.8em;'>
                <b>{row['Code']}</b> : {row['Automatisme']}<br>
                <small><i>Semaine(s)</i> : {row['Semaines']}</small>
            </div>
        """, unsafe_allow_html=True)
    
    # ===== EXPORT EXCEL =====
    with col_export:
        buffer = BytesIO()
        
        # Préparation des données pour l'export
        grille_data = []
        for i in range(32):
            semaine = f"S{i+1}"
            theme_emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else ""
            theme_label = subtheme_legend.get(theme_emoji, "")
            auto_codes = st.session_state.selection_by_week[i] if i < len(st.session_state.selection_by_week) else []
            auto_codes += [""] * (6 - len(auto_codes))  # Compléter jusqu'à 6
            grille_data.append([semaine, f"{theme_emoji} {theme_label}"] + auto_codes)
        
        # Création des DataFrames pour Excel
        df_grille = pd.DataFrame(grille_data, columns=["Semaine", "Thème semaine"] + [f"Auto{i+1}" for i in range(6)])
        df_recap = pd.DataFrame(recap_data)
        
        # Création du fichier Excel
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_grille.to_excel(writer, index=False, sheet_name='Grille')
            df_recap.to_excel(writer, index=False, sheet_name='Lecture_par_automatisme')
        
        st.download_button(
            label="📅 Télécharger le planning Excel",
            data=buffer.getvalue(),
            file_name="planning_reprises.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ===== POINT D'ENTRÉE =====
if __name__ == "__main__":
    main()
