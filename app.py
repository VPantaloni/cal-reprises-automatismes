import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from io import BytesIO

# ===== CONFIGURATION DES THÈMES =====
subthemes = [
    ("🔢", "#ac2747"), ("➗", "#be5770"), ("📏", "#cc6c1d"), ("🔷", "#d27c36"),
    ("⌚", "#dd9d68"), ("📐", "#16a34a"), ("🧊", "#44b56e"), ("📊", "#1975d1"),
    ("🎲", "#3384d6"), ("∝", "#8a38d2")
]

subtheme_emojis = [s[0] for s in subthemes]
subtheme_colors = dict(subthemes)

subtheme_legend = {
    "🔢": "Nombres entiers et décimaux", 
    "➗": "Fractions", 
    "📏": "Longueurs",
    "🔷": "Aires", 
    "⌚": "Temps", 
    "📐": "Étude de configurations planes",
    "🧊": "La vision dans l'espace", 
    "📊": "Orga. et gestion de données",
    "🎲": "Probabilités", 
    "∝": "Proportionnalité"
}

# =====  SIDEBAR =====
# -- bouton remplissage aléatoire
if st.sidebar.button("🎲 Remplir aléatoirement les ❓"):
    new_seq = st.session_state.sequences.copy()
    prev = new_seq[7]  # On part de la semaine 8
    for i in range(8, 32):
        options = [s for s in subtheme_emojis if s != prev]
        choice = random.choice(options)
        new_seq[i] = choice
        prev = choice
    st.session_state.sequences = new_seq
    st.rerun()
# parametres en sliders
st.sidebar.markdown("### Paramètres d'espacement")
min_espacement_rappel = st.sidebar.slider("Espacement min pour rappels", 1, 6, 1)
espacement_min2 = st.sidebar.slider("1ère → 2e apparition (min)", 1, 6, 2)
espacement_max2 = st.sidebar.slider("1ère → 2e apparition (max)", 2, 10, 6)
espacement_min3 = st.sidebar.slider("2e → 3e apparition (min)", 2, 10, 4)
espacement_max3 = st.sidebar.slider("2e → 3e apparition (max)", 2, 15, 10)

# ===== FONCTIONS UTILITAIRES =====

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

def charger_donnees():
    try:
        df = pd.read_csv("Auto-6e.csv", sep=';', encoding='utf-8')
        df = df.dropna(subset=['Code', 'Automatisme'])
        df['Sous-Thème'] = df['Code'].str[0]
        df['Couleur'] = df['Sous-Thème'].map(subtheme_colors)
        df['Rappel'] = df['Code'].str[1] == '↩'
        df['Num'] = df['Code'].str.extract(r'(\d+)$').astype(float)
        return df
    except Exception as e:
        st.error(f"Erreur de lecture CSV : {e}")
        st.stop()

def afficher_pastilles_compacte(selection_df):
    if not selection_df.empty:
        pastilles = [
            f"<div title=\"{row['Automatisme']}\" style='flex:1; padding:2px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em; font-weight:bold; text-align:center; cursor:help;'> {row['Code']} </div>"
            for _, row in selection_df.iterrows()
        ]
        lignes = ["<div style='display:flex; gap:4px;'>" + "".join(pastilles[i:i+2]) + "</div>" for i in range(0, len(pastilles), 2)]
        for ligne in lignes:
            st.markdown(ligne, unsafe_allow_html=True)

def selectionner_automatismes(data, semaine_idx, theme, auto_weeks, used_codes, next_index_by_theme):
    selection_finale = []
    codes_selectionnes = set()
    
    # 1. AUTOMATISMES PRINCIPAUX DU THÈME DE LA SEMAINE
    if theme:
        # Récupérer tous les automatismes du thème (non-rappels) triés par Num
        theme_autos = data[
            (data['Sous-Thème'] == theme) & 
            (~data['Rappel'])
        ].sort_values('Num').copy()
        
        # Filtrer ceux qui respectent les contraintes d'espacement
        theme_disponibles = []
        for _, row in theme_autos.iterrows():
            code = row['Code']
            if (used_codes[code] < 4 and 
                respecte_espacement(auto_weeks[code], semaine_idx, row['Rappel'])):
                theme_disponibles.append(row)
        
        # Sélectionner selon les règles :
        # - Si >= 2 disponibles : prendre les 2 premiers
        # - Si 1 disponible : prendre celui-ci
        # - Si 0 disponible : aucun
        nb_theme_a_prendre = min(2, len(theme_disponibles))
        for i in range(nb_theme_a_prendre):
            selection_finale.append(theme_disponibles[i]['Code'])
            codes_selectionnes.add(theme_disponibles[i]['Code'])
    
    # 2. COMPLÉTER AVEC DES RAPPELS (jusqu'à 6 automatismes total)
    slots_restants = 6 - len(selection_finale)
    
    if slots_restants > 0:
        # Identifier tous les automatismes déjà vus (pour les rappels)
        themes_deja_abordes = set()
        for k in range(semaine_idx):
            if st.session_state.sequences[k]:
                themes_deja_abordes.add(st.session_state.sequences[k])
        
        # Ajouter les thèmes qui ont des automatismes de rappel
        themes_rappel = set(data[data['Rappel']]['Sous-Thème'].unique())
        pool_themes = themes_deja_abordes.union(themes_rappel)
        
        # Candidats pour les rappels
        candidats_rappel = data[
            (data['Sous-Thème'].isin(pool_themes)) &
            (~data['Code'].isin(codes_selectionnes))  # Pas de doublon
        ].copy()
        
        # Filtrer selon les contraintes d'espacement et d'usage
        rappels_possibles = []
        for _, row in candidats_rappel.iterrows():
            code = row['Code']
            if (used_codes[code] < 4 and 
                respecte_espacement(auto_weeks[code], semaine_idx, row['Rappel'])):
                rappels_possibles.append(row)
        
        # Trier les rappels par priorité :
        # 1. Ceux qui n'ont jamais été vus (used_codes = 0)
        # 2. Ceux qui ont été vus le moins souvent
        # 3. Diversifier par thème
        rappels_possibles.sort(key=lambda x: (
            used_codes[x['Code']],  # Moins utilisés en priorité
            x['Sous-Thème'] == theme,  # Éviter le thème courant sauf si nécessaire
            x['Num']  # Ordre dans le thème
        ))
        
        # Sélectionner les rappels en évitant les doublons de thème quand possible
        themes_rappel_selectionnes = set()
        for row in rappels_possibles:
            if len(selection_finale) >= 6:
                break
                
            code = row['Code']
            sous_theme = row['Sous-Thème']
            
            # Préférer la diversité des thèmes, mais accepter les doublons si nécessaire
            if (sous_theme not in themes_rappel_selectionnes or 
                len(themes_rappel_selectionnes) >= len(pool_themes)):
                selection_finale.append(code)
                codes_selectionnes.add(code)
                themes_rappel_selectionnes.add(sous_theme)
    
    # 3. COMPLÉTER SI NÉCESSAIRE (cas d'urgence)
    # Si on n'a pas 6 automatismes, prendre ce qui reste
    if len(selection_finale) < 6:
        tous_candidats = data[~data['Code'].isin(codes_selectionnes)].copy()
        candidats_urgence = []
        
        for _, row in tous_candidats.iterrows():
            code = row['Code']
            if (used_codes[code] < 4 and 
                respecte_espacement(auto_weeks[code], semaine_idx, row['Rappel'])):
                candidats_urgence.append(row)
        
        # Prendre les premiers disponibles
        for row in candidats_urgence:
            if len(selection_finale) >= 6:
                break
            selection_finale.append(row['Code'])
    
    # 4. RÉORGANISER SELON LA CONTRAINTE DE POSITION
    # Les automatismes du thème doivent être en positions 1 et 4
    if theme and len(selection_finale) >= 2:
        # Identifier les automatismes du thème dans la sélection
        autos_theme = [code for code in selection_finale 
                      if data.set_index('Code').loc[code, 'Sous-Thème'] == theme]
        
        # Réorganiser pour mettre les automatismes du thème en positions 1 et 4
        autres_autos = [code for code in selection_finale if code not in autos_theme]
        
        # Nouvelle organisation
        selection_reordonnee = []
        
        # Position 1 : premier auto du thème
        if len(autos_theme) >= 1:
            selection_reordonnee.append(autos_theme[0])
        
        # Positions 2-3 : autres automatismes
        for i in range(min(2, len(autres_autos))):
            selection_reordonnee.append(autres_autos[i])
        
        # Position 4 : deuxième auto du thème (si disponible)
        if len(autos_theme) >= 2:
            selection_reordonnee.append(autos_theme[1])
        
        # Positions 5-6 : compléter avec le reste
        restants = autres_autos[2:] + autos_theme[2:]
        for auto in restants:
            if len(selection_reordonnee) < 6:
                selection_reordonnee.append(auto)
        
        selection_finale = selection_reordonnee
    
    # S'assurer qu'on a exactement 6 automatismes (compléter ou tronquer)
    while len(selection_finale) < 6:
        selection_finale.append("")  # Placeholder vide si vraiment rien n'est disponible
    
    return selection_finale[:6]

# ===== POINT D'ENTRÉE =====

st.set_page_config(layout="wide")
st.title("📅 Reprises d'automatismes mathématiques en 6e")
## LEGENDES
with st.expander("\U0001F4D8 Légende des thèmes"):
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""<div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px; color:white; font-size:0.85em;'>
                <b>{emoji}</b> {label}</div>""", unsafe_allow_html=True)
#--- fin légendes
if 'sequences' not in st.session_state:
    st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * 24
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None

for i in range(32):
    if f"show_picker_{i}" not in st.session_state:
        st.session_state[f"show_picker_{i}"] = False

data = charger_donnees()
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
next_index_by_theme = defaultdict(lambda: 1)
emoji_numeros = [f"Semaine {i+1}:" for i in range(32)]

# Grille 4 lignes × 8 colonnes
rows = [st.columns(8) for _ in range(4)]
for i in range(32):
    row = i // 8
    col = i % 8
    with rows[row][col]:
        emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else "❓"
        label = emoji_numeros[i]
        if st.button(f"{label} {emoji}", key=f"pick_{i}"):
            st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)

        if st.session_state.get(f"show_picker_{i}", False):
            picker_rows = [st.columns(3) for _ in range(4)]
            layout = [
                ["🔢", "➗", ""],
                ["📏", "🔷", "⌚"],
                ["📐", "🧊", ""],
                ["📊", "🎲", "∝"]
            ]
            for picker_row, icons in zip(picker_rows, layout):
                for picker_col, icon in zip(picker_row, icons):
                    with picker_col:
                        if icon:
                            if st.button(f"{icon}", key=f"choose_{i}_{icon}", use_container_width=True):
                                st.session_state.sequences[i] = icon
                                st.session_state[f"show_picker_{i}"] = False
                                st.rerun()

        if st.session_state.sequences[i]:
            codes = selectionner_automatismes(data, i, st.session_state.sequences[i], auto_weeks, used_codes, next_index_by_theme)
            st.session_state.selection_by_week[i] = codes
            for code in codes:
                auto_weeks[code].append(i)
                used_codes[code] += 1
            afficher_pastilles_compacte(data[data['Code'].isin(codes)])
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
            #st.markdown("<hr style='margin-top:8px; margin-bottom:8px; border: none; border-top: 1px solid #ccc;' />", unsafe_allow_html=True)
#
## === LECTURE AUTOMATISMES
#
st.markdown("---")
st.markdown("## 🔍 Lecture par automatisme")
recap_data = []
for _, row in data.iterrows():
    code = row['Code']
    semaines = [f"S{i+1}" for i in auto_weeks.get(code, [])]
    recap_data.append({"Code": code, "Automatisme": row['Automatisme'], "Semaines": ", ".join(semaines), "Couleur": row['Couleur']})

cols = st.columns(3)
nb = len(recap_data)
chunk_size = (nb + 2) // 3 -2
for j in range(3):
    for r in recap_data[j*chunk_size:(j+1)*chunk_size]:
        with cols[j]:
            st.markdown(f"<div style='padding:2px; margin:2px; border: 3px solid {r['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em;'><b>{r['Code']}</b> : {r['Automatisme']}<br><small><i>Semaine(s)</i> : {r['Semaines']}</small></div>", unsafe_allow_html=True)


# ===== EXPORT EXCEL =====
buffer = BytesIO()
grille_data = []
for i in range(32):
    semaine = f"S{i+1}"
    theme_emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else ""
    theme_label = subtheme_legend.get(theme_emoji, "")
    auto_codes = st.session_state.selection_by_week[i] if i < len(st.session_state.selection_by_week) else []
    auto_codes += [""] * (6 - len(auto_codes))
    grille_data.append([semaine, f"{theme_emoji} {theme_label}"] + auto_codes)

df_grille = pd.DataFrame(grille_data, columns=["Semaine", "Thème semaine"] + [f"Auto{i+1}" for i in range(6)])
df_recap = pd.DataFrame(recap_data)

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_grille.to_excel(writer, index=False, sheet_name='Grille')
    df_recap.to_excel(writer, index=False, sheet_name='Lecture_par_automatisme')

st.download_button(
    label="📅 Télécharger le planning Excel",
    data=buffer.getvalue(),
    file_name="planning_reprises.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
