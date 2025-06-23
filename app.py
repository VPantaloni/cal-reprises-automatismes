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

# ===== RÉCAPITULATIF PAR AUTOMATISME EN 3 COLONNES FIXES =====
data = charger_donnees()
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
recap_data = []

for i in range(32):
    theme = st.session_state.sequences[i]
    if theme != "❓":
        possibles = data[(data['Sous-Thème'] == theme) & (~data['Rappel'])]
        possibles = possibles.sort_values('Num')
        for code in possibles['Code']:
            if code not in st.session_state.selection_by_week[i]:
                st.session_state.selection_by_week[i].append(code)
                auto_weeks[code].append(i)
                used_codes[code] += 1
                break

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
