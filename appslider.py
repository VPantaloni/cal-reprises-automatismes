import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from io import BytesIO

# === DÉCLARATIONS GÉNÉRALES ===

# Définition des sous-thèmes et couleurs associées
subthemes = [
    ("🔢", "#ac2747"), ("➗", "#be5770"), ("📏", "#cc6c1d"), ("🔷", "#d27c36"),
    ("⌚", "#dd9d68"), ("📐", "#16a34a"), ("🧊", "#44b56e"), ("📊", "#1975d1"),
    ("🎲", "#3384d6"), ("∝", "#8a38d2")
]

subtheme_emojis = [s[0] for s in subthemes]
subtheme_colors = dict(subthemes)
subtheme_legend = {
    "🔢": "Nombres entiers et décimaux", "➗": "Fractions", "📏": "Longueurs",
    "🔷": "Aires", "⌚": "Temps", "📐": "Étude de configurations planes",
    "🧊": "La vision dans l’espace", "📊": "Organisation et gestion de données",
    "🎲": "Probabilités", "∝": "Proportionnalité"
}

# Mode sombre (dark mode)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

if st.session_state.dark_mode:
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            background-color: #111 !important;
            color: #ddd !important;
        }
        .stButton>button {
            background-color: #333 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Liste des numéros de semaines (S1 à S32)
emoji_numeros = [f"S{i+1}" for i in range(32)]

# Séquence personnalisée des thèmes pour les 32 semaines (ordre initial)
theme_sequence_custom = [
    "🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷",
    "🔢", "⌚", "📐", "➗", "🎲", "📐", "∝", "📐",
    "🎲", "🔢", "🧊", "➗", "🔢", "⌚", "🔷", "🧊",
    "🔢", "📐", "➗", "📐", "📏", "📐", "∝", "📊"
]

# === CONTRÔLES POUR LES TESTS ===
st.sidebar.markdown("### Paramètres d'espacement")
min_espacement_rappel = st.sidebar.slider("Espacement minimum pour rappels (semaines)", 1, 6, 2)
espacement_min2 = st.sidebar.slider("Espacement 1ère → 2e apparition", 1, 6, 2)
espacement_max2 = st.sidebar.slider("Espacement max 1ère → 2e apparition", 2, 10, 4)
espacement_min3 = st.sidebar.slider("Espacement 2e → 3e apparition", 2, 10, 4)
espacement_max3 = st.sidebar.slider("Espacement max 2e → 3e apparition", 2, 12, 6)

# Fonction de vérification de l'espacement entre répétitions d'un automatisme
def respecte_espacement(semaines, semaine_actuelle, est_rappel):
    if not semaines:
        return True
    dernier = max(semaines)
    ecart = semaine_actuelle - dernier
    if est_rappel:
        return ecart >= min_espacement_rappel
    if len(semaines) == 1:
        return espacement_min2 <= ecart <= espacement_max2
    elif len(semaines) == 2:
        return espacement_min3 <= ecart <= espacement_max3
    else:
        return False
# === CHARGEMENT DES DONNÉES ===
try:
    data = pd.read_csv("Auto-6e.csv", sep=';', encoding='utf-8')
    data = data.dropna(subset=['Code', 'Automatisme'])
except Exception as e:
    st.error("Erreur lors de la lecture du fichier CSV : " + str(e))
    st.stop()

data['Sous-Thème'] = data['Code'].str[0]
data['Rappel'] = data['Code'].str[1] == '↩'
data['Num'] = data['Code'].str.extract(r'(\d+)$').astype(float)
data['Couleur'] = data['Sous-Thème'].map(subtheme_colors)

# === INITIALISATION DES ÉTATS SESSION ===
if 'sequences' not in st.session_state:
    st.session_state.sequences = theme_sequence_custom.copy()

if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]

# === INIT TRACKERS DE DISTRIBUTION ===
auto_weeks = defaultdict(list)      # Semaines où chaque automatisme a été placé
used_codes = defaultdict(int)       # Combien de fois chaque code a été utilisé
next_index_by_theme = defaultdict(lambda: 1)  # Pour les automatismes ordonnés par thème


# === CALCUL AUTOMATISMES PAR SEMAINE ===
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
next_index_by_theme = defaultdict(lambda: 1)

for i in range(32):
    theme_semaine = st.session_state.sequences[i]
    deja_abordes = [st.session_state.sequences[k] for k in range(i+1) if st.session_state.sequences[k]]
    rappels = data[data['Rappel']]['Sous-Thème'].unique().tolist()
    pool = list(set(deja_abordes + rappels))

    candidats = data[data['Sous-Thème'].isin(pool)].copy()
    candidats = candidats[(candidats['Rappel']) | (candidats['Sous-Thème'].isin(deja_abordes))]
    candidats['Used'] = candidats['Code'].map(lambda c: used_codes[c])
    candidats = candidats[candidats['Used'] < 4]
    candidats = candidats[candidats['Code'].apply(lambda c: respecte_espacement(auto_weeks[c], i, data.set_index('Code').loc[c, 'Rappel']))]

    selection = []
    if theme_semaine:
        theme_df = candidats[(candidats['Sous-Thème'] == theme_semaine) & (~candidats['Rappel'])].sort_values('Num')
        attendu = next_index_by_theme[theme_semaine]
        for _, row in theme_df.iterrows():
            if int(row['Num']) == attendu:
                selection.append(row.to_dict())
                next_index_by_theme[theme_semaine] += 1
                break

    autres = candidats[~candidats['Code'].isin([r['Code'] for r in selection])]
    groupes = autres.groupby('Sous-Thème')
    divers = [g.sort_values('Num').iloc[0] for _, g in groupes if not g.empty]
    random.shuffle(divers)
    selection.extend(divers[:5])

    essais = 0
    while len(selection) < 6 and essais < 50:
        restants = candidats[~candidats['Code'].isin([row['Code'] for row in selection])]
        for _, row in restants.iterrows():
            if row['Code'] not in [sel['Code'] for sel in selection]:
                if respecte_espacement(auto_weeks[row['Code']], i, row['Rappel']):
                    selection.append(row.to_dict())
                    break
        essais += 1

    st.session_state.selection_by_week[i] = [row['Code'] for row in selection]
    for row in selection:
        code = row['Code']
        auto_weeks[code].append(i)
        used_codes[code] += 1

#   Affichage dynamique des pastilles et export Excel)
