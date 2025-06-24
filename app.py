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
    deja_abordes = [st.session_state.sequences[k] for k in range(semaine_idx+1) if st.session_state.sequences[k]]
    themes_rappel = data[data['Rappel']]['Sous-Thème'].unique().tolist()
    pool = list(set(deja_abordes + themes_rappel))

    candidats = data[data['Sous-Thème'].isin(pool)].copy()
    candidats = candidats[(candidats['Rappel']) | (candidats['Sous-Thème'].isin(deja_abordes))]
    candidats['Used'] = candidats['Code'].map(lambda c: used_codes[c])
    candidats = candidats[candidats['Used'] < 4]
    candidats = candidats[candidats['Code'].apply(lambda c: respecte_espacement(auto_weeks[c], semaine_idx, data.set_index('Code').loc[c, 'Rappel']))]

    selection = []
    if theme:
        theme_df = candidats[(candidats['Sous-Thème'] == theme) & (~candidats['Rappel'])].sort_values('Num')
        attendu = next_index_by_theme[theme]
        for _, row in theme_df.iterrows():
            if int(row['Num']) == attendu:
                selection.append(row)
                next_index_by_theme[theme] += 1
                break

    autres = candidats[~candidats['Code'].isin([r['Code'] for r in selection])]
    groupes = autres.groupby('Sous-Thème')
    divers = [g.sort_values('Num').iloc[0] for _, g in groupes if not g.empty]
    random.shuffle(divers)
    selection.extend(divers[:5])

    tentatives = 0
    while len(selection) < 6 and tentatives < 50:
        restants = candidats[~candidats['Code'].isin([r['Code'] for r in selection])]
        for _, row in restants.iterrows():
            if row['Code'] not in [r['Code'] for r in selection] and respecte_espacement(auto_weeks[row['Code']], semaine_idx, row['Rappel']):
                selection.append(row)
                break
        tentatives += 1

    return [r['Code'] for r in selection[:6]]

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
