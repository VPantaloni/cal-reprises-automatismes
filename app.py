# app.py
import streamlit as st
import pandas as pd
import random
from collections import defaultdict
from io import BytesIO
import selection_q1q2
import selection_q3

# ===== CONFIGURATION DES THÈMES =====
subthemes = [
    ("🔢", "#ac2747"), ("➗", "#be5770"), ("📏", "#cc6c1d"), ("🔷", "#d27c36"),
    ("⌚", "#dd9d68"), ("📐", "#16a34a"), ("🧊", "#44b56e"), ("📊", "#1975d1"),
    ("🎲", "#3384d6"), ("∝", "#8a38d2")
]
theme_emojis = [emoji for emoji, _ in subthemes]
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
if "show_legend" not in st.session_state:
    st.session_state.show_legend = True
if "show_recap" not in st.session_state:
    st.session_state.show_recap = False
if "show_tuto" not in st.session_state:
    st.session_state.show_tuto = False
#if "show_histogram" not in st.session_state:
#    st.session_state.show_histogram = False
show_histogram = False
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

# Chargement des données
data = charger_donnees()

def afficher_pastilles_compacte(selection_df, nb_auto_par_ligne=3, total_cases=9):
    if not selection_df.empty:
        pastilles_dict = {
            int(row['Position']): f"<div title=\"{row['Automatisme']}\" style='flex:1; padding:2px; border:2.5px solid {row['Couleur']}; background:transparent; border-radius:4px; font-size:0.68em; font-weight:bold; text-align:center; cursor:help;'> {row['Code']} </div>"
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
                    ligne_html += "<div style='flex:1; padding:2px; border:1px dashed #ccc; border-radius:4px; height:1.4em;'></div>"
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
##
# INIT
# Initialisation session state
if 'sequences' not in st.session_state:
    st.session_state.sequences = initialiser_sequences()
if 'selection_by_week' not in st.session_state:
    st.session_state.selection_by_week = initialiser_selection_by_week()
if 'picker_open' not in st.session_state:
    st.session_state.picker_open = None
#show_histogram = False
#show_recap = False
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


# Configuration de la page
st.set_page_config(layout="wide")
#st.title("📅 Reprises d'automatismes mathématiques en 6e")
st.markdown("### 📅 Reprises d'automatismes mathématiques en 6e")

# AFFICHAGE LÉGENDE SI ACTIVÉ
if st.session_state.show_legend:
    st.markdown("##### 📘 Légende des thèmes")
    cols = st.columns(5)
    for idx, (emoji, label) in enumerate(subtheme_legend.items()):
        with cols[idx % 5]:
            st.markdown(f"""
                <div style='background:{subtheme_colors[emoji]}; padding:4px; border-radius:6px;
                            color:white; font-size:0.77em; text-align:left'>
                    <b>{emoji}</b> {label}
                </div>
            """, unsafe_allow_html=True)
    st.markdown("---")

## Bulles tuto warning
nb_vides = sum(1 for t in st.session_state.sequences if not t or t == "❓")

if nb_vides > 0:
    st.warning(
        "🛠️ Avant de commencer à distribuer les automatismes :\n\n"
        "- 👉 Cliquez sur les boutons des semaines (**S1** à **S35**) pour choisir le thème de la semaine (changer les ❓) dans votre progression ou :\n"
        "- 📕 Chargez une progression prête (📘**Progression n°1** ou 📙**Progression n°2**) via la barre latérale. Vous pourrez la modifier.\n"
        "- 📚 Pour plus de détails, affichez le tutoriel en cochant la case ✅ 📚**Tutoriel** dans le volet latéral"
    )

# 📘 TUTORIEL DE DÉMARRAGE
if st.session_state.get("show_tuto", True):
    st.markdown("### 📚 Bienvenue dans cet outil de planification des automatismes")
    st.markdown("""
Cet outil vous permet de calculer et afficher un **calendrier de reprise des automatismes** mathématiques en 6e, en fonction de votre progression.

#### 🧩 Étapes à suivre :
1. **Choisissez les thèmes hebdomadaires** :
   - Cliquez sur les boutons `S1`, `S2`, etc. pour choisir le thème plus particulièrement travaillé en classe cette semaine.
   - Vous pouvez aussi charger une **progression enregistrée** dans la barre latérale (📘`Progression n°1` ou 📙 `Progression n°2`).

2. **Lancez la distribution des automatismes** :
   - Utilisez le bouton 👉 `🛠️ Algo. distribuer les automatismes`,
   - L’algorithme répartit les automatismes selon les thèmes et les rappels `↩` des années antérieures,
   - Il y a trois séries verticales (pour trois jours) de trois automatismes par semaine :
       - le 1er automatisme porte sur le thème actuel,
       - le 2e sur le thème à venir dans deux semaines et
       - le 3e est calculé de sorte à optimiser la répartition et ne porte que sur des thématiques abordées ou bien est un rappel des années précédentes (logo `↩`).

3. **Visualisez la répartition** 
    - Chaque intitulé d'automatisme est lisible par survol.
   - L’onglet **🔍Liste automatismes** vous montre l'intitulé et la répartition de chacun.
   - Des **graphiques interactifs** (avec filtres par **thème ou code**) permettent d’analyser la couverture semaine par semaine (✅ `Histogrammes`).

4. **Exportez** votre travail si besoin :
   - En HTML (Ctrl+S) ou tableur via les boutons d’export.

5. La fin de chaque période (début de vacances 🎉) est marquée par `🡆|` et on peut choisir sa zone de vacances scolaires (A,B,C).

#### Besoin de plus de détails ❓""")
    st.markdown("Consultez ce 📚 [Tutoriel détaillé](https://codimd.apps.education.fr/s/xd2gxRA1m) (en ligne)")
    st.markdown("---")

# ===== SIDEBAR =====
st.sidebar.checkbox("📚 Tutoriel", key="show_tuto", value=False)
#st.sidebar.markdown(
#    "<a href='https://codimd.apps.education.fr/s/xd2gxRA1m' target='_blank' style='text-decoration: none;'>"
#    "📚 Lien vers tutoriel </a>",
#    unsafe_allow_html=True
#)

#st.sidebar.markdown("### 🎯 Affichage")
# Affichage légende
if "show_legend" not in st.session_state:
    st.session_state.show_legend = True

st.sidebar.checkbox("📘 Afficher la légende", key="show_legend")

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
# Liste auto
st.sidebar.checkbox("🔍 Liste automatismes", key="show_recap")
# BOUTON ALGO tout en un avec check de validation.
# Initialisation au début
if 'btn_done' not in st.session_state:
    st.session_state.btn_done = False

# Vérifier si tous les thèmes sont définis
nb_vides = sum(1 for t in st.session_state.get("sequences", []) if not t or t == "❓")

# ✅ Afficher message tant que algo pas lancé
if nb_vides == 0 and not st.session_state.btn_done:
    st.sidebar.info("👍 Go go Algo!👇")

# ✅ Algo distrib : bouton unique
if st.sidebar.button("🛠️ Algo. distribuer les automatismes"):
    auto_weeks = defaultdict(list)
    used_codes = defaultdict(int)

    for i in range(35):
        if i < len(st.session_state.sequences):
            theme = st.session_state.sequences[i]
            if theme and theme != "❓":
                st.session_state.selection_by_week[i] = selection_q1q2.selectionner_q1q2(
                    data, i, theme, st.session_state.sequences, auto_weeks, used_codes
                )

    from selection_q3 import selectionner_q3, reconstruire_auto_weeks

    auto_weeks, used_codes = reconstruire_auto_weeks(st.session_state.selection_by_week)

    st.session_state.selection_by_week = selectionner_q3(
        data,
        st.session_state.selection_by_week,
        st.session_state.sequences,
        auto_weeks,
        used_codes
    )

    # ✅ Marquer que le bouton a été utilisé
    st.session_state.btn_done = True

    st.rerun()

# ✅ Message de confirmation si bouton déjà utilisé
if st.session_state.btn_done:
    #st.sidebar.success("✅ Distribution 🛠️")
    # 🔘 Affichage conditionnel de l’histogramme
    show_histogram = st.sidebar.checkbox("📊 Histogrammes", value=False)
    

#st.sidebar.markdown("### Affichages")

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

# ===================== AFFICHAGE PLANNING =====================

# Emojis numérotés S1 à S35
emoji_numeros = [f"S{i+1}" for i in range(35)]

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
            st.markdown(f"<div style='font-size: 1.5em; text-align:right; color: gold'>{vacances_txt}</div>", unsafe_allow_html=True)

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
                if code == "❓":
                    selection_df.append({
                        "Position": pos,
                        "Code": "❓",
                        "Automatisme": "À compléter",
                        "Couleur": "#cccccc"
                    })
                else:
                    ligne = data[data['Code'] == code]
                    if not ligne.empty:
                        row = ligne.iloc[0]
                        selection_df.append({
                            "Position": pos,
                            "Code": row['Code'],
                            "Automatisme": row['Automatisme'],
                            "Couleur": row['Couleur']
                        })
                    else:
                        selection_df.append({
                            "Position": pos,
                            "Code": code,
                            "Automatisme": "(inconnu)",
                            "Couleur": "#ff0000"
                        })

            selection_df = pd.DataFrame(selection_df)
            afficher_pastilles_compacte(selection_df, nb_auto_par_ligne=3, total_cases=9)
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

from collections import defaultdict
import pandas as pd

# Import du volet 2
auto_weeks, used_codes = selection_q3.reconstruire_auto_weeks(st.session_state.selection_by_week)
st.session_state.auto_weeks = auto_weeks

def afficher_lecture_et_export(data, subtheme_legend):
    st.markdown("---")
    st.markdown("#### 🔍 Liste et fréquence des automatismes")

    # Sécurité
    if not isinstance(st.session_state.auto_weeks, dict):
        st.session_state.auto_weeks, _ = selection_q3.reconstruire_auto_weeks(st.session_state.selection_by_week)

    recap_data = []
    for _, row in data.iterrows():
        code = row['Code']
        semaines = st.session_state.auto_weeks.get(code, [])
        semaines_str = [f"S{i+1}" for i in semaines]

        # Représentation visuelle de 35 semaines
        ligne_visuelle = ""
        for i in range(35):
            if i in semaines:
                ligne_visuelle += "🟢"
            else:
                ligne_visuelle += "⚪"
        ligne_visuelle = f"<div style='font-family:monospace; font-size:0.48em'>{ligne_visuelle}</div>"

        recap_data.append({
            "Code": code,
            "Automatisme": row['Automatisme'],
            "Semaines": ", ".join(semaines_str),
            "Couleur": row['Couleur'],
            "Timeline": ligne_visuelle
        })

    # Répartition en 3 colonnes équilibrées
    cols = st.columns(3)
    nb = len(recap_data)
    base = nb // 3
    reste = nb % 3
    sizes = [base + 1, base, nb - (base + 1 + base)]

    start = 0
    for j in range(3):
        end = start + sizes[j]
        for r in recap_data[start:end]:
            with cols[j]:
                st.markdown(
                    f"<div style='padding:2px; margin:2px; border: 3px solid {r['Couleur']}; "
                    f"background:transparent; border-radius:4px; font-size:0.8em;'>"
                    f"<b>{r['Code']}</b> : {r['Automatisme']}<br>"
                    f"<small><i>Semaine(s)</i> : {r['Semaines']}</small><br>"
                    f"{r['Timeline']}</div>",
                    unsafe_allow_html=True
                )
        start = end

    # ✅ Encapsulation du tableau dans un expander
    occur_df = pd.DataFrame([
        {
            "Code": code,
            "Occurrences": len(semaines),
            "Semaines": ", ".join([f"S{s+1}" for s in semaines])
        }
        for code, semaines in st.session_state.auto_weeks.items()
    ])

    if not occur_df.empty and "Occurrences" in occur_df.columns:
        occur_df = occur_df.sort_values(by="Occurrences", ascending=False)
        with st.expander("📊 Répartition tabulaire des automatismes par nombre d'occurrences ⤵", expanded=False):
            st.dataframe(occur_df, use_container_width=True)
    else:
        st.info("Aucune donnée d'automatismes à afficher. Placez une thème pour chaque semaine puis lancer 🛠 `Algo. distribuer automatismes` pour générer le planning.  Les dates apparaîtront ci-dessus et dans un tableau ci-dessous.")

    return recap_data

#----------------------------- 
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

# Recap par automatisme 
df_recap = pd.DataFrame(recap_data)
#EXPORT EXCEL
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
###-----   H I S T O
import plotly.express as px
import pandas as pd
from collections import defaultdict

if show_histogram:
    # Préparation des données
    rows = []
    cumul_counts = defaultdict(int)

    for semaine_index in range(35):
        semaine_label = f"S{semaine_index + 1}"
        codes = st.session_state.selection_by_week[semaine_index] if semaine_index < len(st.session_state.selection_by_week) else []

        for code in codes:
            if code != "❓":
                cumul_counts[code] += 1
                row = data[data['Code'] == code]
                if not row.empty:
                    couleur = row.iloc[0]['Couleur']
                    rows.append({
                        "Semaine": semaine_label,
                        "Code": code,
                        "Occurrences cumulées": cumul_counts[code],
                        "Couleur": couleur
                    })

    df_viz = pd.DataFrame(rows)

    # Ordre naturel des semaines (string), explicitement défini
    semaine_order = [f"S{i}" for i in range(1, 36)]
    df_viz["Semaine"] = pd.Categorical(df_viz["Semaine"], categories=semaine_order, ordered=True)

    # Trie par semaine et code pour que ça s’affiche bien
    df_viz = df_viz.sort_values(["Semaine", "Code"])

    # Mapping couleur précis par code unique
    couleur_map = df_viz.drop_duplicates(subset=["Code"]).set_index("Code")["Couleur"].to_dict()
       
    # 1. Structure pour garder l'ordre CSV et regrouper par thème
    # subtheme_legend est supposé : dict emoji -> nom
    # data est ton DataFrame CSV avec colonnes : 'Code', 'Thème', etc.
    # On part du principe que chaque 'Code' commence par emoji thème
    
    # Construire dict: emoji -> list de codes (dans l'ordre CSV)
    codes_by_theme = {}
    for emoji in subtheme_legend.keys():
        codes = data[data['Code'].str.startswith(emoji)]['Code'].tolist()
        if codes:
            codes_by_theme[emoji] = codes
    
    # 2. Initialiser la sélection dans st.session_state si non existante
    if 'codes_selectionnes' not in st.session_state:
        # Par défaut on sélectionne tous les codes
        st.session_state.codes_selectionnes = set(data['Code'].tolist())
    
    # 3. Afficher les filtres thématiques sous forme de sections
    st.markdown("### 🎛️ Filtrer par thème et codes")
    
    for emoji, codes in codes_by_theme.items():
        # Tout sélectionner ou tout désélectionner pour ce thème
        all_selected = all(code in st.session_state.codes_selectionnes for code in codes)
    
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            clicked = st.button(f"{emoji}", key=f"btn_toggle_{emoji}", help=f"Tout sélectionner/désélectionner {emoji}", use_container_width=True)
            if clicked:
                if all_selected:
                    for c in codes:
                        st.session_state.codes_selectionnes.discard(c)
                else:
                    for c in codes:
                        st.session_state.codes_selectionnes.add(c)
        
        with col2:
            max_cols = 10
            cols_codes = st.columns(max_cols)  # toujours 10 colonnes fixes
        
            for i in range(max_cols):
                if i < len(codes):
                    code = codes[i]
                    checked = code in st.session_state.codes_selectionnes
                    cb = cols_codes[i].checkbox(code, value=checked, key=f"cb_{code}")
                    if cb and not checked:
                        st.session_state.codes_selectionnes.add(code)
                    elif not cb and checked:
                        st.session_state.codes_selectionnes.discard(code)
                else:
                    # Colonne vide pour aligner la grille
                    cols_codes[i].markdown("&nbsp;")  # espace insécable pour la hauteur minimale
    # Après la boucle d'affichage des thèmes + cases à cocher

    # 4. Filtrer df_viz avant affichage selon sélection
    df_viz_filtered = df_viz[df_viz['Code'].isin(st.session_state.codes_selectionnes)]
    
    # 5. Affichage du graphique filtré
    import plotly.express as px
    
    fig = px.bar(
        df_viz_filtered,
        x="Semaine",
        y="Occurrences cumulées",
        color="Code",
        color_discrete_map=couleur_map,
        hover_name="Code",
        #title="📊 Histogramme cumulé par automatisme et semaine",
        category_orders={
        "Semaine": semaine_order,
        "Code": data["Code"].tolist()}  # 👈 ordre du CSV
    )
    with st.expander("📊 Histogramme : occurrences cumulées des automatismes par semaine ⤵", expanded=False):
            st.plotly_chart(fig, use_container_width=True)
## 2e histo non cumulé
    # 🔁 On prépare à nouveau les données, cette fois sans cumul
    rows_simple = []
    
    for semaine_index in range(35):
        semaine_label = f"S{semaine_index + 1}"
        codes = st.session_state.selection_by_week[semaine_index] if semaine_index < len(st.session_state.selection_by_week) else []
    
        for code in codes:
            if code != "❓":
                row = data[data['Code'] == code]
                if not row.empty:
                    couleur = row.iloc[0]['Couleur']
                    rows_simple.append({
                        "Semaine": semaine_label,
                        "Code": code,
                        "Occurrences": 1,  # Une unité par apparition
                        "Couleur": couleur
                    })
    
    # 📊 Création du DataFrame
    df_simple = pd.DataFrame(rows_simple)
    df_simple["Semaine"] = pd.Categorical(df_simple["Semaine"], categories=semaine_order, ordered=True)
    df_simple = df_simple.sort_values(["Semaine", "Code"])
    
    # 🧽 Filtrer selon sélection de l'utilisateur
    df_simple_filtered = df_simple[df_simple['Code'].isin(st.session_state.codes_selectionnes)]
    
    # 🎨 Graphique non cumulé
    fig_simple = px.bar(
        df_simple_filtered,
        x="Semaine",
        y="Occurrences",
        color="Code",
        color_discrete_map=couleur_map,
        hover_name="Code",
        #title="📊 Histogramme simple : apparition des automatismes par semaine",
        category_orders={
        "Semaine": semaine_order,
        "Code": data["Code"].tolist() } 
    )
    with st.expander("📊 Histogramme simple : apparition des automatismes par semaine ⤵", expanded=False):
        st.plotly_chart(fig_simple, use_container_width=True)
