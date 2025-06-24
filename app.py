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
    "📊": "Organisation et gestion de données",
    "🎲": "Probabilités", 
    "∝": "Proportionnalité"
}

# ===== ESPACEMENT PARAMÉTRABLE VIA SIDEBAR =====
st.sidebar.markdown("### Paramètres d'espacement")
min_espacement_rappel = st.sidebar.slider("Espacement min pour rappels", 1, 6, 2)
espacement_min2 = st.sidebar.slider("1ère → 2e apparition (min)", 1, 6, 2)
espacement_max2 = st.sidebar.slider("1ère → 2e apparition (max)", 2, 10, 4)
espacement_min3 = st.sidebar.slider("2e → 3e apparition (min)", 2, 10, 4)
espacement_max3 = st.sidebar.slider("2e → 3e apparition (max)", 2, 12, 6)

if st.sidebar.button("🎲 Remplir aléatoirement les thèmes vides"):
    new_seq = st.session_state.sequences.copy()
    prev = None
    for i in range(32):
        if not new_seq[i] or new_seq[i] == "❓":
            options = [s for s in subtheme_emojis if s != prev]
            choice = random.choice(options)
            new_seq[i] = choice
            prev = choice
        else:
            prev = new_seq[i]
    st.session_state.sequences = new_seq
    st.rerun()

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

# ===== POINT D'ENTRÉE =====

st.set_page_config(layout="wide")
st.title("📅 Reprises d'automatismes mathématiques en 6e")

if 'sequences' not in st.session_state:
    st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + ["❓"] * 24
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]

# ===== AFFICHAGE DES 32 SEMAINES AVEC BOUTONS ET AUTOMATISMES =====
data = charger_donnees()
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
recap_data = []
emoji_numeros = [f"S{i+1}" for i in range(32)]
rows = [st.columns(8) for _ in range(4)]

for i in range(32):
    row_idx = i // 8
    col_idx = i % 8
    col = rows[row_idx][col_idx]
    selected = st.session_state.sequences[i]

    with col:
        emoji = selected if selected else "❓"
        st.markdown(f"<div style='text-align:center; font-weight:bold;'>{emoji_numeros[i]}</div>", unsafe_allow_html=True)
        if st.button(emoji, key=f"pick_{i}"):
            st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)

        if st.session_state.get(f"show_picker_{i}", False):
            picker_rows = [st.columns(3) for _ in range(4)]
            layout = [["🔢", "➗", ""], ["📏", "🔷", "⌚"], ["📐", "🧊", ""], ["📊", "🎲", "∝"]]
            for row, emojis in zip(picker_rows, layout):
                for col2, icon in zip(row, emojis):
                    with col2:
                        if icon and st.button(f"{icon}", key=f"choose_{i}_{icon}", use_container_width=True):
                            st.session_state.sequences[i] = icon
                            st.session_state[f"show_picker_{i}"] = False
                            st.rerun()

        # Sélection des automatismes pour cette semaine
        theme = st.session_state.sequences[i]
        selection = []
        if theme != "❓":
            possibles = data[(data['Sous-Thème'] == theme) & (~data['Rappel'])]
            possibles = possibles.sort_values('Num')
            for code in possibles['Code']:
                if code not in st.session_state.selection_by_week[i]:
                    st.session_state.selection_by_week[i].append(code)
                    auto_weeks[code].append(i)
                    used_codes[code] += 1
                    break

        # Affichage des pastilles (en grille 2x3)
        selection_df = data[data['Code'].isin(st.session_state.selection_by_week[i])]
        auto_grid = ""
        for idx, (_, row) in enumerate(selection_df.iterrows()):
            if idx >= 6:
                break
            if idx % 2 == 0:
                auto_grid += "<div style='display:flex; gap:2px; margin:1px 0;'>"
            auto_grid += f"""
                <div title=\"{row['Automatisme']}\" 
                     style='flex:1; padding:2px; border: 2px solid {row['Couleur']}; 
                            background:transparent; border-radius:4px; 
                            font-size:0.65em; font-weight:bold; text-align:center; 
                            cursor:help; min-height:18px; line-height:1.2;'>
                    {row['Code']}
                </div>
            """
            if idx % 2 == 1:
                auto_grid += "</div>"
        if len(selection_df) % 2 == 1:
            auto_grid += "</div>"
        st.markdown(auto_grid, unsafe_allow_html=True)

# ===== RÉCAPITULATIF PAR AUTOMATISME EN 3 COLONNES FIXES =====
for _, row in data.iterrows():
    code = row['Code']
    semaines = [f"S{i+1}" for i in auto_weeks.get(code, [])]
    recap_data.append({
        "Code": code,
        "Automatisme": row['Automatisme'],
        "Semaines": ", ".join(semaines),
        "Couleur": row['Couleur']
    })

st.markdown("---")
st.markdown("## 🔍 Lecture par automatisme")
cols = st.columns(3)
col1, col2, col3 = cols

for j, r in enumerate(recap_data):
    if j < 18:
        col = col1
    elif j < 36:
        col = col2
    else:
        col = col3
    with col:
        st.markdown(f"<div style='padding:2px; margin:2px; border: 3px solid {r['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em;'><b>{r['Code']}</b> : {r['Automatisme']}<br><small><i>Semaine(s)</i> : {r['Semaines']}</small></div>", unsafe_allow_html=True)

# ===== FIN DE L'APPLICATION =====
