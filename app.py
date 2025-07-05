# app.py
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

# ===== FONCTIONS UTILITAIRES =====
def charger_donnees():
    try:
        df = pd.read_csv("Auto-6e.csv", sep=';', encoding='utf-8')
        df = df.dropna(subset=['Code', 'Automatisme'])
        df['Sous-Thème'] = df['Code'].str[0]
        df['Couleur'] = df['Sous-Thème'].map(subtheme_colors)
        df['Rappel'] = df['Code'].str[1] == '↩'
        df['Num'] = df['Code'].str.extract(r'(\d+)$').astype(float)
        df['__ordre__'] = range(len(df))  # 👈 Ajout essentiel pour préserver l'ordre
        return df
    except Exception as e:
        st.error(f"Erreur de lecture CSV : {e}")
        st.stop()

def afficher_pastilles_compacte(selection_df, nb_auto_par_ligne=3, total_cases=9):
    if not selection_df.empty:
        pastilles_dict = {
            int(row['Position']): f"<div title=\"{row['Automatisme']}\" style='flex:1; padding:2px; border:3px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em; font-weight:bold; text-align:center; cursor:help;'> {row['Code']} </div>"
            for _, row in selection_df.iterrows()
        }
        nb_lignes = (total_cases + nb_auto_par_ligne - 1) // nb_auto_par_ligne

        for ligne in range(nb_lignes):
            ligne_html = "<div style='display:flex; gap:4px;'>"
            for col in range(nb_auto_par_ligne):
                pos = col * nb_lignes + ligne
                if pos in pastilles_dict:
                    ligne_html += pastilles_dict[pos]
                else:
                    ligne_html += "<div style='flex:1; padding:2px; border:1px dashed #ccc; border-radius:4px; height:1.5em;'></div>"
            ligne_html += "</div>"
            st.markdown(ligne_html, unsafe_allow_html=True)

def melanger_sans_consecutifs(liste):
    for _ in range(1000):
        melange = random.sample(liste, len(liste))
        if all(melange[i] != melange[i+1] for i in range(len(melange)-1)):
            return melange
    return liste

def initialiser_sequences():
    return ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷", "⌚", "🧊"] + [""] * 25

def initialiser_selection_by_week():
    return [[] for _ in range(35)]

# Configuration de la page
st.set_page_config(layout="wide")
#st.title("📅 Reprises d'automatismes mathématiques en 6e")
st.markdown("## 📅 Reprises d'automatismes mathématiques en 6e")

## LEGENDES
with st.expander("📘 Légende des thèmes ⤵" + " " + " " + " " + "\u00A0"* 15 + ">> Ouvrir le menu latéral pour plus d'actions !"):
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""<div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px; color:white; font-size:0.85em;'>
                <b>{emoji}</b> {label}</div>""", unsafe_allow_html=True)

# ===== SIDEBAR =====

st.sidebar.markdown("### 🎯 Affichage")
# Choix de la zone de vacances
# Définitions des durées vacances (en nombre de semaines)
vacances_A = [7, 7, 5, 6]
vacances_B = [7, 7, 6, 6]
vacances_C = [7, 7, 7, 6]

vacances_map = {
    "Zone A": vacances_A,
    "Zone B": vacances_B,
    "Zone C": vacances_C
}
# Initialiser la valeur par défaut dans session_state si absente
if "zone_vacances" not in st.session_state:
    st.session_state.zone_vacances = "Zone B"

# Widget radio, lié à la clé zone_vacances pour garder la sélection dans la session
zone = st.sidebar.radio(
    "Choix vacances 🡆|",
    ["Zone A", "Zone B", "Zone C"],
    index=["Zone A", "Zone B", "Zone C"].index(st.session_state.zone_vacances),
    key="zone_vacances"
)

# Utilisation
vacances = vacances_map[zone]
vacances_semaines = []
s = 0
for v in vacances:
    s += v
    vacances_semaines.append(s)

#--------
st.sidebar.checkbox("🔍 Afficher vue par automatisme", key="show_recap")
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

st.sidebar.markdown("### Compléter grille")

# Progressions pour 35 semaines
progression_1 = [
    "🔢", "📐", "➗", "📏", "📐", "🔢", "📏", "🔷", "➗", "⌚", "🧊",
    "🔢", "📐", "➗", "🎲", "📐", "∝", "📐", "🎲", "🔢", "🧊",
    "➗", "🔢", "⌚", "🔷", "🧊", "🔢", "📐", "➗", "📐", "📏",
    "📐", "∝", "📊", "🔢"
]
progression_2 = [
    "🔢", "📐", "➗", "🔢", "📐", "∝", "🎲", "📐", "🔢", "⌚", "📐",
    "➗", "🔢", "📊", "📏", "📐", "➗", "∝", "🎲", "📐", "🔢",
    "🧊", "⌚", "➗", "🔢", "📏", "📐", "➗", "🔷", "🧊", "📊",
    "📐", "🔷", "🔢", "📐"
]

if st.sidebar.button("📘 Progression n°1"):
    st.session_state.sequences = progression_1.copy()
    st.rerun()

if st.sidebar.button("📙 Progression n°2"):
    st.session_state.sequences = progression_2.copy()
    st.rerun()

top_button_placeholder = st.sidebar.empty()
#st.sidebar.markdown("### Affichages")
st.sidebar.markdown(
    "<a href='https://codimd.apps.education.fr/s/xd2gxRA1m' target='_blank' style='text-decoration: none;'>"
    "📚 Lien vers tutoriel </a>",
    unsafe_allow_html=True
)


# Chargement des données
data = charger_donnees()

# Initialisation session state
if 'sequences' not in st.session_state:
    st.session_state.sequences = initialiser_sequences()
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = initialiser_selection_by_week()
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None

# Assurer que les listes ont la bonne taille
if len(st.session_state.sequences) != 35:
    old_sequences = st.session_state.sequences.copy()
    st.session_state.sequences = initialiser_sequences()
    # Copier les anciennes valeurs si possible
    for i in range(min(len(old_sequences), 35)):
        if old_sequences[i]:
            st.session_state.sequences[i] = old_sequences[i]

if len(st.session_state.selection_by_week) != 35:
    st.session_state.selection_by_week = initialiser_selection_by_week()

for i in range(35):
    if f"show_picker_{i}" not in st.session_state:
        st.session_state[f"show_picker_{i}"] = False

# Import de l'algorithme de sélection
from selection_algo import selectionner_automatismes

def recalculer_toute_la_repartition():
    st.session_state.selection_by_week = [[] for _ in range(35)]
    st.session_state.auto_weeks.clear()
    st.session_state.used_codes.clear()
    st.session_state.next_index_by_theme = defaultdict(lambda: 1)
    
    for i in range(35):
        if st.session_state.sequences[i]:
            themes_passes = [t for t in st.session_state.sequences[:i] if t]
            codes = selectionner_automatismes(
                data, i, st.session_state.sequences[i],
                st.session_state.auto_weeks,
                st.session_state.used_codes,
                st.session_state.next_index_by_theme,
                themes_passes=themes_passes,
                sequences=st.session_state.sequences
            )
            st.session_state.selection_by_week[i] = codes
            for code in codes:
                st.session_state.auto_weeks[code].append(i)
                st.session_state.used_codes[code] += 1

# Bouton recalcul
if top_button_placeholder.button("🔄 (Re)calculer la distribution des automatismes"):
    recalculer_toute_la_repartition()
    st.rerun()

# ===================== AFFICHAGE PLANNING =====================

# Emojis numérotés S1 à S35
emoji_numeros = [f"S{i+1}" for i in range(35)]

# Affichage en 5 lignes de 7 colonnes
# Affichage en 5 lignes de 7 colonnes
rows = [st.columns(7) for _ in range(5)]
vacances_A = [6, 12, 18, 26]  # Numéros de semaine juste avant vacances

for i in range(35):
    row = i // 7
    col = i % 7
    semaine_num = i + 1
    emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else "❓"
    label = emoji_numeros[i]
    vacances_txt = "🡆|" if semaine_num in vacances_semaines else ""

    with rows[row][col]:
        # Ligne contenant bouton semaine + repère vacances à droite
        col_btn, col_vac = st.columns([5, 1])
        with col_btn:
            if st.button(f"{label} {emoji}", key=f"pick_{i}"):
                st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)
                st.rerun()
        with col_vac:
            st.markdown(f"<div style='font-size: 1.5em; text-align:right; color: yellow'>{vacances_txt}</div>", unsafe_allow_html=True)

        # Picker d'emoji (sélecteur de thème)
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

        # Affichage des pastilles si disponibles
        if st.session_state.sequences[i] and st.session_state.selection_by_week[i]:
            codes = st.session_state.selection_by_week[i]
            selection_df = []
            for pos, code in enumerate(codes):
                if code:
                    row = data[data['Code'] == code].iloc[0]
                    selection_df.append({
                        "Position": pos,
                        "Code": row['Code'],
                        "Automatisme": row['Automatisme'],
                        "Couleur": row['Couleur']
                    })
            selection_df = pd.DataFrame(selection_df)
            afficher_pastilles_compacte(selection_df, nb_auto_par_ligne=3, total_cases=9)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

# Import du volet 2

def afficher_lecture_et_export(data, subtheme_legend):
    st.markdown("---")
    st.markdown("## 🔍 Lecture par automatisme")

    recap_data = []
    for _, row in data.iterrows():
        code = row['Code']
        semaines = [f"S{i+1}" for i in st.session_state.auto_weeks.get(code, [])]
        recap_data.append({
            "Code": code,
            "Automatisme": row['Automatisme'],
            "Semaines": ", ".join(semaines),
            "Couleur": row['Couleur']
        })

    cols = st.columns(3)
    nb = len(recap_data)
    
    # Répartition initiale
    base = nb // 3
    reste = nb % 3
    
    # Attribution manuelle des tailles selon ta logique :
    # - col 0 : +1 (donc base + 1)
    # - col 1 : base +0 
    # - col 2 : le reste
    sizes = [base + 1, base + 0, nb - (base + 1 + base + 0)]
    
    start = 0
    for j in range(3):
        end = start + sizes[j]
        for r in recap_data[start:end]:
            with cols[j]:
                st.markdown(
                    f"<div style='padding:2px; margin:2px; border: 3px solid {r['Couleur']}; "
                    f"background:transparent; border-radius:4px; font-size:0.8em;'>"
                    f"<b>{r['Code']}</b> : {r['Automatisme']}<br>"
                    f"<small><i>Semaine(s)</i> : {r['Semaines']}</small></div>",
                    unsafe_allow_html=True
                )
        start = end
    
    return recap_data


    
if st.session_state.show_recap:
    recap_data = afficher_lecture_et_export(data, subtheme_legend)
else:
    recap_data = []  # Nécessaire pour éviter erreur dans export Excel

#-----------------------
# Génération export Excel
buffer = BytesIO()
grille_data = []

for i in range(35):
    semaine = f"S{i+1}"
    theme_emoji = st.session_state.sequences[i] if i < len(st.session_state.sequences) and st.session_state.sequences[i] else ""
    theme_label = subtheme_legend.get(theme_emoji, "")
    auto_codes = st.session_state.selection_by_week[i] if i < len(st.session_state.selection_by_week) else []
    auto_codes = auto_codes[:9] + [""] * (9 - len(auto_codes))
    grille_data.append([semaine, f"{theme_emoji} {theme_label}"] + auto_codes)

colonnes = ["Semaine", "Thème semaine"] + [f"Auto{i+1}" for i in range(9)]
df_grille = pd.DataFrame(grille_data, columns=colonnes)

# Recap par automatisme (tu dois avoir `recap_data` défini ailleurs)
df_recap = pd.DataFrame(recap_data)

with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_grille.to_excel(writer, index=False, sheet_name='Grille')
    df_recap.to_excel(writer, index=False, sheet_name='Lecture_par_automatisme')

buffer.seek(0)  # ← très important !

# Bouton dans la sidebar
st.sidebar.download_button(
    label="📅 Télécharger le planning Excel",
    data=buffer.getvalue(),
    file_name="planning_reprises_35sem.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
