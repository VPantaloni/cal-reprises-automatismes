import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from io import BytesIO

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

def respecte_espacement(semaines, semaine_actuelle, est_rappel):
    if not semaines:
        return True
    dernier = max(semaines)
    ecart = semaine_actuelle - dernier
    if est_rappel:
        return ecart >= 2
    if len(semaines) == 1:
        return 2 <= ecart <= 4
    elif len(semaines) == 2:
        return 4 <= ecart <= 6
    else:
        return False

emoji_numeros = [f"S{i+1}" for i in range(32)]

try:
    data = pd.read_csv("Auto-6e.csv", sep=';', encoding='utf-8')
    data = data.dropna(subset=['Code', 'Automatisme'])
except Exception as e:
    st.error("Erreur lors de la lecture du fichier CSV : " + str(e))
    st.stop()

data['Sous-Thème'] = data['Code'].str[0]
data['Couleur'] = data['Sous-Thème'].map(subtheme_colors)
data['Rappel'] = data['Code'].str[1] == '↩'
data['Num'] = data['Code'].str.extract(r'(\d+)$').astype(float)

st.set_page_config(layout="wide")
st.title("\U0001F4C5 Reprises d'automatismes mathématiques en 6e")

# MODE NUIT (toggle)
dark_mode = st.sidebar.checkbox("🌙 Mode nuit")
if dark_mode:
    st.markdown("""
        <style>
        body, .stApp { background-color: #0e1117; color: white; }
        .stButton>button { background-color: #333; color: white; }
        </style>
    """, unsafe_allow_html=True)

with st.expander("\U0001F4D8 Légende des thèmes"):
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""<div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px; color:white; font-size:0.85em;'>
                <b>{emoji}</b> {label}</div>""", unsafe_allow_html=True)

if 'sequences' not in st.session_state:
    st.session_state.sequences = ["🔢", "📐", "📊", "➗", "📐", "🔢", "📏", "🔷"] + [""] * (32 - 8)
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = [[] for _ in range(32)]

col_reset, col_random, col_export = st.columns([1, 2, 2])
#with col_reset:
#    if st.button("\U0001F504 Réinitialiser"):
#        st.session_state.sequences = [None] * 32
#        st.rerun()
with col_random:
    if st.button("\U0001F3B2 Remplir aléatoirement"):
        new_seq = []
        prev = None
        for _ in range(32):
            options = [s for s in subtheme_emojis if s != prev]
            choice = random.choice(options)
            new_seq.append(choice)
            prev = choice
        st.session_state.sequences = new_seq
        st.rerun()

# Init trackers
auto_weeks = defaultdict(list)
used_codes = defaultdict(int)
next_index_by_theme = defaultdict(lambda: 1)

#st.markdown("## \U0001F4CC Grille de 32 semaines")

rows = [st.columns(8) for _ in range(4)]
for i in range(32):
    row_idx = i // 8
    col_idx = i % 8
    col = rows[row_idx][col_idx]
    selected = st.session_state.sequences[i]

    with col:
        emoji = selected if selected else "❓"
        st.markdown(f"<b>{emoji_numeros[i]}</b> ", unsafe_allow_html=True)
        if st.button(emoji, key=f"pick_{i}"):
            st.session_state[f"show_picker_{i}"] = not st.session_state.get(f"show_picker_{i}", False)
#grille de boutons de sélection des themes :
        if st.session_state.get(f"show_picker_{i}", False):
            picker_rows = [st.columns(3) for _ in range(4)]
            layout = [
                ["🔢", "➗", ""],
                ["📏", "🔷", "⌚"],
                ["📐", "🧊", ""],
                ["📊", "🎲", "∝"]
            ]
            for row, emojis in zip(picker_rows, layout):
                for col, icon in zip(row, emojis):
                    with col:
                        if icon:
                            if st.button(f"{icon}", key=f"choose_{i}_{icon}", use_container_width=True):
                                st.session_state.sequences[i] = icon
                                st.session_state[f"show_picker_{i}"] = False
                                st.rerun()
#fin de boutons
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
                    selection.append(row)
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
                        selection.append(row)
                        break
            essais += 1

        selection_df = pd.DataFrame(selection).head(6)
        st.session_state.selection_by_week[i] = selection_df['Code'].tolist() if not selection_df.empty else []

        for code in st.session_state.selection_by_week[i]:
            auto_weeks[code].append(i)
            used_codes[code] += 1

        if not selection_df.empty:
            col1, col2 = st.columns(2)
            for idx, (_, row) in enumerate(selection_df.iterrows()):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    st.markdown(f"""
                        <div title=\"{row['Automatisme']}\" style='padding:2px; margin:2px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; display:inline-block; width:100%; min-height:28px; font-size:0.75em; font-weight:bold; text-align:center; cursor:help;'>
                            {row['Code']}</div>""", unsafe_allow_html=True)

# Lecture par automatisme
st.markdown("---")
st.markdown("## \U0001F50D Lecture par automatisme")
recap_data = []
for _, row in data.iterrows():
    code = row['Code']
    semaines = [f"S{w+1}" for w in auto_weeks.get(code, [])]
    recap_data.append({
        "Code": code,
        "Automatisme": row['Automatisme'],
        "Semaines": ", ".join(semaines),
        "Couleur": row['Couleur']
    })

recap_df = pd.DataFrame(recap_data)
for _, row in recap_df.iterrows():
    st.markdown(f"""<div style='padding:2px; margin:2px; border: 3px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.8em;'>
            <b>{row['Code']}</b> : {row['Automatisme']}<br>
            <small><i>Semaine(s)</i> : {row['Semaines']}</small>
        </div>""", unsafe_allow_html=True)

with col_export:
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
        label="\U0001F4C5 Télécharger le planning Excel",
        data=buffer.getvalue(),
        file_name="planning_reprises.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
