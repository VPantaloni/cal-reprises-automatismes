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

def afficher_pastilles(selection_df):
    if not selection_df.empty:
        col1, col2 = st.columns(2)
        for idx, (_, row) in enumerate(selection_df.iterrows()):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                st.markdown(f"""
                    <div title=\"{row['Automatisme']}\" style='padding:2px; margin:1px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; display:inline-block; width:100%; min-height:28px; font-size:0.75em; font-weight:bold; text-align:center; cursor:help;'>
                        {row['Code']}
                    </div>""", unsafe_allow_html=True)

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

if 'sequences' not in st.session_state:
    st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * 24
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None

data = charger_donnees()
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
next_index_by_theme = defaultdict(lambda: 1)
emoji_numeros = [f"S{i+1}" for i in range(32)]

# Grille 4 lignes × 8 colonnes
rows = [st.columns(8) for _ in range(4)]
for i in range(32):
    row = i // 8
    col = i % 8
    with rows[row][col]:
        st.markdown(f"<b>{emoji_numeros[i]}</b>", unsafe_allow_html=True)
        emoji = st.session_state.sequences[i] if st.session_state.sequences[i] else "❓"
        if st.button(emoji, key=f"btn_{i}"):
            st.session_state.picker_open = i
        st.markdown(f"<div style='text-align:center; font-size:1.5em'>{emoji}</div>", unsafe_allow_html=True)

        if st.session_state.sequences[i]:
            codes = selectionner_automatismes(data, i, st.session_state.sequences[i], auto_weeks, used_codes, next_index_by_theme)
            st.session_state.selection_by_week[i] = codes
            for code in codes:
                auto_weeks[code].append(i)
                used_codes[code] += 1
            afficher_pastilles(data[data['Code'].isin(codes)])

# Affichage du sélecteur de thème
if st.session_state.picker_open is not None:
    idx = st.session_state.picker_open
    st.markdown(f"### Choisir un thème pour la semaine S{idx+1}")
    layout = [
        ["🔢", "➗", ""],
        ["📏", "🔷", "⌚"],
        ["📐", "🧊", ""],
        ["📊", "🎲", "∝"]
    ]
    for row in layout:
        cols = st.columns(3)
        for col, emoji in zip(cols, row):
            if emoji:
                with col:
                    if st.button(f"{emoji}", key=f"set_{idx}_{emoji}"):
                        st.session_state.sequences[idx] = emoji
                        st.session_state.picker_open = None
                        st.rerun()

st.markdown("---")
st.markdown("## 🔍 Lecture par automatisme")
recap_data = []
for _, row in data.iterrows():
    code = row['Code']
    semaines = [f"S{i+1}" for i in auto_weeks.get(code, [])]
    recap_data.append({"Code": code, "Automatisme": row['Automatisme'], "Semaines": ", ".join(semaines), "Couleur": row['Couleur']})
for r in recap_data:
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
