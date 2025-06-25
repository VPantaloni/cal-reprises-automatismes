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
#  INIT
if 'auto_weeks' not in st.session_state:
    st.session_state.auto_weeks = defaultdict(list)
if 'used_codes' not in st.session_state:
    st.session_state.used_codes = defaultdict(int)
if 'next_index_by_theme' not in st.session_state:
    st.session_state.next_index_by_theme = defaultdict(lambda: 1)
    
# ===== FONCTIONS UTILITAIRES =====

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
        codes = list(selection_df['Code'])
        # Affichage dans l’ordre naturel des indices : 0&1, 2&3, 4&5
        pastilles = [
            f"<div title=\"{row['Automatisme']}\" style='flex:1; padding:2px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em; font-weight:bold; text-align:center; cursor:help;'> {row['Code']} </div>"
            for _, row in selection_df.iterrows()
        ]
        lignes = ["<div style='display:flex; gap:4px;'>" + "".join(pastilles[i:i+2]) + "</div>" for i in range(0, len(pastilles), 2)]
        for ligne in lignes:
            st.markdown(ligne, unsafe_allow_html=True)


#--- début du corps principal ---

# Configuration de la page
st.set_page_config(layout="wide")
st.title("📅 Reprises d'automatismes mathématiques en 6e")
## LEGENDES
with st.expander("\U0001F4D8 Légende des thèmes ⤵  Ouvrir le menu latéral pour plus d'actions !"):
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""<div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px; color:white; font-size:0.85em;'>
                <b>{emoji}</b> {label}</div>""", unsafe_allow_html=True)
#--- fin légendes
#Fonction de mélange sans répétition consecutive
def melanger_sans_consecutifs(liste):
    for _ in range(1000):  # on essaie jusqu’à trouver une permutation valide
        melange = random.sample(liste, len(liste))
        if all(melange[i] != melange[i+1] for i in range(len(melange)-1)):
            return melange
    return liste  # fallback si on n'y arrive pas


# =====  SIDEBAR =====
st.sidebar.markdown("### Actions")
# Progressons pré-définies :
progression_1 = [
    "🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷",
    "🔢", "⌚", "📐", "➗", "🎲", "📐", "∝", "📐",
    "🎲", "🔢", "🧊", "➗", "🔢", "⌚", "🔷", "🧊",
    "🔢", "📐", "➗", "📐", "📏", "📐", "∝", "📊"
]
if st.sidebar.button("📘 Progression n°1"):
    st.session_state.sequences = progression_1.copy()
    st.rerun()
# Prog. Aléa :
if st.sidebar.button("🔀 Progression aléatoire"):
    progression_random = melanger_sans_consecutifs(progression_1)
    st.session_state.sequences = progression_random
    st.rerun()
# -- Recalcul
top_button_placeholder = st.sidebar.empty()
# -- bouton remplissage aléatoire
if st.sidebar.button("🎲 Compléter "❓"):
    new_seq = st.session_state.sequences.copy()
    prev = new_seq[7]  # On part de la semaine 8
    for i in range(8,32):
        options = [s for s in subtheme_emojis if s != prev]
        choice = random.choice(options)
        new_seq[i] = choice
        prev = choice
    st.session_state.sequences = new_seq
    st.rerun()
    ##########
st.sidebar.markdown("### Paramètres d'espacement")
min_espacement_rappel = st.sidebar.slider("Espacement min pour rappels", 1, 6, 1)
espacement_min2 = st.sidebar.slider("1ère → 2e apparition (min)", 1, 6, 2)
espacement_max2 = st.sidebar.slider("1ère → 2e apparition (max)", 2, 10, 6)
espacement_min3 = st.sidebar.slider("2e → 3e apparition (min)", 2, 10, 4)
espacement_max3 = st.sidebar.slider("2e → 3e apparition (max)", 2, 15, 10)



# Chargement des données
data = charger_donnees()

# Initialisation session state
if 'sequences' not in st.session_state:
    st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * 24
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None
for i in range(32):
    if f"show_picker_{i}" not in st.session_state:
        st.session_state[f"show_picker_{i}"] = False

# Bouton de redistribution :
from selection_algo import selectionner_automatismes

def recalculer_toute_la_repartition():
    st.session_state.selection_by_week = [[] for _ in range(32)]
    st.session_state.auto_weeks.clear()
    st.session_state.used_codes.clear()
    st.session_state.next_index_by_theme = defaultdict(lambda: 1)
    
    for i in range(32):
        if st.session_state.sequences[i]:
            themes_passes = [t for t in st.session_state.sequences[:i] if t]
            codes = selectionner_automatismes(
                data, i, st.session_state.sequences[i],
                st.session_state.auto_weeks,
                st.session_state.used_codes,
                st.session_state.next_index_by_theme,
                min_espacement_rappel=min_espacement_rappel,
                espacement_min2=espacement_min2,
                espacement_max2=espacement_max2,
                espacement_min3=espacement_min3,
                espacement_max3=espacement_max3,
                themes_passes=themes_passes
            )
            st.session_state.selection_by_week[i] = codes
            for code in codes:
                st.session_state.auto_weeks[code].append(i)
                st.session_state.used_codes[code] += 1

# === Affichage réel du bouton dans le placeholder ===
if top_button_placeholder.button("🔄 Recalculer la répartition"):
    recalculer_toute_la_repartition()
    st.rerun()
#if st.sidebar.button("🔄 Recalculer la répartition"):
#    recalculer_toute_la_repartition()
#    st.rerun()

# Affichage de la grille
emoji_numeros = [f"Semaine {i+1}:" for i in range(32)]
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

        if st.session_state.sequences[i] and st.session_state.selection_by_week[i]:
            codes = st.session_state.selection_by_week[i]
            afficher_pastilles_compacte(data[data['Code'].isin(codes)])
            st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
## Volet 2 :
import volet2

# plus bas dans ton script principal, après calcul et affichage des semaines
volet2.afficher_lecture_et_export(data, subtheme_legend)
