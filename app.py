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

# ===== INITIALISATION =====
if 'auto_weeks' not in st.session_state:
    st.session_state.auto_weeks = defaultdict(list)
if 'used_codes' not in st.session_state:
    st.session_state.used_codes = defaultdict(int)
if 'next_index_by_theme' not in st.session_state:
    st.session_state.next_index_by_theme = defaultdict(lambda: 1)
if 'mode_affichage' not in st.session_state:
    st.session_state.mode_affichage = "32_semaines"  # ou "35_semaines"

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

def afficher_pastilles_compacte(selection_df, nb_auto_par_ligne=2):
    if not selection_df.empty:
        codes = list(selection_df['Code'])
        pastilles = [
            f"<div title=\"{row['Automatisme']}\" style='flex:1; padding:2px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em; font-weight:bold; text-align:center; cursor:help;'> {row['Code']} </div>"
            for _, row in selection_df.iterrows()
        ]
        lignes = ["<div style='display:flex; gap:4px;'>" + "".join(pastilles[i:i+nb_auto_par_ligne]) + "</div>" 
                 for i in range(0, len(pastilles), nb_auto_par_ligne)]
        for ligne in lignes:
            st.markdown(ligne, unsafe_allow_html=True)

def melanger_sans_consecutifs(liste):
    for _ in range(1000):
        melange = random.sample(liste, len(liste))
        if all(melange[i] != melange[i+1] for i in range(len(melange)-1)):
            return melange
    return liste

def get_nb_semaines():
    return 32 if st.session_state.mode_affichage == "32_semaines" else 35

def get_nb_automatismes():
    return 6 if st.session_state.mode_affichage == "32_semaines" else 9

def initialiser_sequences():
    nb_semaines = get_nb_semaines()
    if st.session_state.mode_affichage == "32_semaines":
        return ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * (nb_semaines - 8)
    else:  # 35 semaines
        return ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷", "⌚", "🧊"] + [""] * (nb_semaines - 10)

def initialiser_selection_by_week():
    nb_semaines = get_nb_semaines()
    return [[] for _ in range(nb_semaines)]

# Configuration de la page
st.set_page_config(layout="wide")
st.title("📅 Reprises d'automatismes mathématiques en 6e")

# Affichage du mode actuel
#mode_text = "32 semaines (4×8) - 6 automatismes par semaine" if st.session_state.mode_affichage == "32_semaines" else "35 semaines (5×7) - 9 automatismes par semaine"
#st.info(f"Mode actuel : {mode_text}")

## LEGENDES
with st.expander("📘 Légende des thèmes ⤵" + " " + " " + " " + "\u00A0"* 15 + ">> Ouvrir le menu latéral pour plus d'actions !"):
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""<div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px; color:white; font-size:0.85em;'>
                <b>{emoji}</b> {label}</div>""", unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.markdown("### 🎯 Mode d'affichage")
# === MODE NUIT ===
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if st.sidebar.button("🌙 Mode nuit" if not st.session_state.dark_mode else "☀️ Mode clair"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body, .stApp {
            background-color: #0e1117 !important;
            color: #FAFAFA !important;
        }
        .css-1v0mbdj, .css-1d391kg, .st-bc {
            background-color: #1c1e26 !important;
            color: #FAFAFA !important;
        }
        .css-1v0mbdj:hover, .css-1d391kg:hover {
            background-color: #2c2e36 !important;
        }
        .stButton button {
            background-color: #444 !important;
            color: #fafafa !important;
            border: 1px solid #666;
        }
        .stButton > button {
            background-color: #444 !important;
            color: #fafafa !important;
            border: 1px solid #666;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
###
if st.sidebar.button("📆 35 sem. (3×3)", 
             type="primary" if st.session_state.mode_affichage == "35_semaines" else "secondary"):
    if st.session_state.mode_affichage != "35_semaines":
        st.session_state.mode_affichage = "35_semaines"
        st.session_state.sequences = initialiser_sequences()
        st.session_state.selection_by_week = initialiser_selection_by_week()
        # Réinitialiser les états des pickers
        for i in range(50):
            if f"show_picker_{i}" in st.session_state:
                st.session_state[f"show_picker_{i}"] = False
        st.rerun()
        
if st.sidebar.button("🗓 32 sem. (2×3)", 
             type="primary" if st.session_state.mode_affichage == "32_semaines" else "secondary"):
    if st.session_state.mode_affichage != "32_semaines":
        st.session_state.mode_affichage = "32_semaines"
        st.session_state.sequences = initialiser_sequences()
        st.session_state.selection_by_week = initialiser_selection_by_week()
        # Réinitialiser les états des pickers
        for i in range(50):  # Sécurité pour tous les pickers possibles
            if f"show_picker_{i}" in st.session_state:
                st.session_state[f"show_picker_{i}"] = False
        st.rerun()


st.sidebar.markdown("### Actions")

# Progressions adaptées au mode
if st.session_state.mode_affichage == "32_semaines":
    progression_1 = [
        "🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷",
        "🔢", "⌚", "📐", "➗", "🎲", "📐", "∝", "📐",
        "🎲", "🔢", "🧊", "➗", "🔢", "⌚", "🔷", "🧊",
        "🔢", "📐", "➗", "📐", "📏", "📐", "∝", "📊"
    ]
    progression_2 = [
        "🔢", "📐", "🔢", "📐", "∝", "🎲", "📐", "🔢",
        "⌚", "📐", "➗", "🔢", "📊", "📏", "📐", "➗",
        "∝", "🎲", "📐", "🔢", "🧊", "⌚", "➗", "🔢",
        "📏", "📐", "➗", "🔷", "🧊", "📊", "📐", "🔷"
    ]
else:  # 35 semaines
    progression_1 = [
        "🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷", "➗", "⌚", "🧊",
        "🔢", "📐", "➗", "🎲", "📐", "∝", "📐", "🎲", "🔢", "🧊",
        "➗", "🔢", "⌚", "🔷", "🧊", "🔢", "📐", "➗", "📐", "📏",
        "📐", "∝", "📊", "🔢"
    ]
    progression_2 = [
        "🔢", "📐", "🔢", "📐", "∝", "🎲", "📐", "🔢", "⌚", "📐",
        "➗", "🔢", "📊", "📏", "📐", "➗", "∝", "🎲", "📐", "🔢",
        "🧊", "⌚", "➗", "🔢", "📏", "📐", "➗", "🔷", "🧊", "📊",
        "📐", "🔷", "🔢", "📐", "➗"
    ]

if st.sidebar.button("📘 Progression n°1"):
    st.session_state.sequences = progression_1.copy()
    st.rerun()

if st.sidebar.button("📙 Progression n°2"):
    st.session_state.sequences = progression_2.copy()
    st.rerun()

if st.sidebar.button("🔀 Progression aléa."):
    progression_random = melanger_sans_consecutifs(progression_1)
    st.session_state.sequences = progression_random
    st.rerun()

top_button_placeholder = st.sidebar.empty()

# Bouton remplissage aléatoire adapté
if st.sidebar.button("🎲 Compléter les ❓"):
    nb_semaines = get_nb_semaines()
    new_seq = st.session_state.sequences.copy()
    start_idx = 8 if st.session_state.mode_affichage == "32_semaines" else 10
    if len(new_seq) > start_idx - 1:
        prev = new_seq[start_idx - 1]
        for i in range(start_idx, nb_semaines):
            options = [s for s in subtheme_emojis if s != prev]
            choice = random.choice(options)
            new_seq[i] = choice
            prev = choice
    st.session_state.sequences = new_seq
    st.rerun()

st.sidebar.markdown(
    "<a href='https://codimd.apps.education.fr/s/xd2gxRA1m' target='_blank' style='text-decoration: none;'>"
    "📚 Tuto </a>",
    unsafe_allow_html=True
)

#st.sidebar.markdown("### Paramètres d'espacement")
#min_espacement_rappel = st.sidebar.slider("Espacement min pour rappels", 1, 6, 1)
#espacement_min2 = st.sidebar.slider("1ère → 2e apparition (min)", 1, 6, 2)
#espacement_max2 = st.sidebar.slider("1ère → 2e apparition (max)", 2, 10, 6)
#espacement_min3 = st.sidebar.slider("2e → 3e apparition (min)", 2, 10, 4)
#espacement_max3 = st.sidebar.slider("2e → 3e apparition (max)", 2, 15, 10)

#parametres obsolètes mais utiles pour la cohérence des appels.
min_espacement_rappel = 1
espacement_min2 = 1 #"1ère → 2e apparition (min)", 1, 6, 2)
espacement_max2 = 3 #st.sidebar.slider("1ère → 2e apparition (max)", 2, 10, 6)
espacement_min3 = 2 #st.sidebar.slider("2e → 3e apparition (min)", 2, 10, 4)
espacement_max3 = 5 #st.sidebar.slider("2e → 3e apparition (max)", 2, 15, 10)

# Chargement des données
data = charger_donnees()

# Initialisation session state
nb_semaines = get_nb_semaines()
nb_automatismes = get_nb_automatismes()

if 'sequences' not in st.session_state:
    st.session_state.sequences = initialiser_sequences()
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = initialiser_selection_by_week()
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None

# Assurer que les listes ont la bonne taille
if len(st.session_state.sequences) != nb_semaines:
    old_sequences = st.session_state.sequences.copy()
    st.session_state.sequences = initialiser_sequences()
    # Copier les anciennes valeurs si possible
    for i in range(min(len(old_sequences), nb_semaines)):
        if old_sequences[i]:
            st.session_state.sequences[i] = old_sequences[i]

if len(st.session_state.selection_by_week) != nb_semaines:
    st.session_state.selection_by_week = initialiser_selection_by_week()

for i in range(nb_semaines):
    if f"show_picker_{i}" not in st.session_state:
        st.session_state[f"show_picker_{i}"] = False

# Import de l'algorithme de sélection
from selection_algo import selectionner_automatismes

def recalculer_toute_la_repartition():
    nb_semaines = get_nb_semaines()
    st.session_state.selection_by_week = [[] for _ in range(nb_semaines)]
    st.session_state.auto_weeks.clear()
    st.session_state.used_codes.clear()
    st.session_state.next_index_by_theme = defaultdict(lambda: 1)
    
    for i in range(nb_semaines):
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
                themes_passes=themes_passes,
                nb_automatismes=get_nb_automatismes()
            )
            st.session_state.selection_by_week[i] = codes
            for code in codes:
                st.session_state.auto_weeks[code].append(i)
                st.session_state.used_codes[code] += 1

# Bouton recalcul
if top_button_placeholder.button("🔄 Recalculer la répartition"):
    recalculer_toute_la_repartition()
    st.rerun()

# Affichage de la grille
emoji_numeros = [f"Semaine {i+1}:" for i in range(nb_semaines)]

# Affichage adapté selon le mode
if st.session_state.mode_affichage == "32_semaines":
    # 4 lignes de 8 colonnes
    rows = [st.columns(8) for _ in range(4)]
    for i in range(nb_semaines):
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
                    ["❓", "🔢", "➗"],
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
                afficher_pastilles_compacte(data[data['Code'].isin(codes)], nb_auto_par_ligne=2)
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
else:
    # 5 lignes de 7 colonnes
    rows = [st.columns(7) for _ in range(5)]
    for i in range(nb_semaines):
        row = i // 7
        col = i % 7
        with rows[row][col]:
            emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else "❓"
            label = emoji_numeros[i]
            if st.button(f"{label} {emoji}", key=f"pick_{i}"):
                st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)

            if st.session_state.get(f"show_picker_{i}", False):
                picker_rows = [st.columns(3) for _ in range(4)]
                layout = [
                    ["❓", "🔢", "➗"],
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
                afficher_pastilles_compacte(data[data['Code'].isin(codes)], nb_auto_par_ligne=3)
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

# Import du volet 2
import volet2
volet2.afficher_lecture_et_export(data, subtheme_legend)
