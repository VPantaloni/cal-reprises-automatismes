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
# Bouton de redistribution :
if st.sidebar.button("🔄 Recalculer la répartition"):
    selectionner_automatismes(data, semaine_idx, theme, auto_weeks, used_codes, next_index_by_theme)
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
    """
    Sélectionne exactement 6 automatismes pour une semaine :
    - 2 automatismes du thème courant (nouveaux) en positions 1 et 4
    - 4 automatismes en rappel (déjà vus les semaines précédentes)
    
    Contraintes :
    - Maximum 3 occurrences par automatisme sur l'année
    - Espacement temporel selon nombre de vues précédentes
    - Rappels uniquement depuis thèmes déjà abordés
    """
    selection_finale = [None] * 6
    codes_selectionnes = set()
    
    # 1. AUTOMATISMES DU THÈME COURANT (POSITIONS 1 ET 4) - OBLIGATOIRES
    if theme:
        # Récupérer tous les automatismes du thème (y compris rappels ↩)
        theme_autos = data[data['Code'].str.startswith(theme)].sort_values('Num')
        
        if not theme_autos.empty:
            # Séparer selon le besoin de vues minimales pour prioriser
            candidats_prioritaires = []
            tous_candidats = []
            
            for _, row in theme_autos.iterrows():
                code = row['Code']
                nb_vues = used_codes[code]
                tous_candidats.append(row)
                
                # Vérifier si l'automatisme a encore besoin d'être vu
                if row['Rappel']:  # Rappel (↩) : minimum 2 vues
                    if nb_vues < 2:
                        candidats_prioritaires.append(row)
                else:  # Non-rappel : minimum 3 vues
                    if nb_vues < 3:
                        candidats_prioritaires.append(row)
            
            # Choisir les 2 premiers automatismes du thème
            # Priorité 1 : Ceux qui ont encore besoin d'être vus (par ordre Num)
            # Priorité 2 : Tous les automatismes du thème (par ordre Num)
            if len(candidats_prioritaires) >= 2:
                auto1 = candidats_prioritaires[0]['Code']
                auto2 = candidats_prioritaires[1]['Code']
            elif len(candidats_prioritaires) == 1:
                auto1 = candidats_prioritaires[0]['Code']
                # Prendre le 2e dans tous les candidats (en évitant le doublon)
                auto2 = None
                for candidat in tous_candidats:
                    if candidat['Code'] != auto1:
                        auto2 = candidat['Code']
                        break
                if auto2 is None:  # Si tous sont identiques, répéter
                    auto2 = auto1
            else:
                # Aucun candidat prioritaire : prendre les 2 premiers du thème
                auto1 = tous_candidats[0]['Code']
                auto2 = tous_candidats[1]['Code'] if len(tous_candidats) > 1 else auto1
            
            # PLACER OBLIGATOIREMENT en positions 1 et 2 (première ligne)
            selection_finale[0] = auto1  # Position 1
            selection_finale[1] = auto2  # Position 2
            codes_selectionnes.add(auto1)
            codes_selectionnes.add(auto2)
    
    # 2. AUTOMATISMES EN RAPPEL (POSITIONS 3, 4, 5, 6)
    # Récupérer les thèmes déjà abordés les semaines précédentes
    themes_deja_abordes = set()
    for k in range(semaine_idx):
        if k < len(st.session_state.sequences) and st.session_state.sequences[k]:
            themes_deja_abordes.add(st.session_state.sequences[k])
    
    # Pool de candidats pour les rappels
    candidats_rappel = []
    
    # Parcourir tous les automatismes pour trouver ceux qui ont besoin d'être revus
    for _, row in data.iterrows():
        code = row['Code']
        nb_vues = used_codes[code]
        
        # Éviter les doublons avec les automatismes du thème courant
        if code in codes_selectionnes:
            continue
        
        # Vérifier si l'automatisme a besoin d'être encore vu
        besoin_revu = False
        if row['Rappel']:  # Rappel (↩) : minimum 2 vues
            besoin_revu = (nb_vues > 0 and nb_vues < 2)
        else:  # Non-rappel : minimum 3 vues
            besoin_revu = (nb_vues > 0 and nb_vues < 3)
        
        if besoin_revu:
            # Vérifier si c'est d'un thème déjà abordé OU un rappel ancien
            theme_de_lauto = code[0]
            if (theme_de_lauto in themes_deja_abordes) or row['Rappel']:
                # Vérifier contraintes d'espacement
                if respecte_espacement(auto_weeks[code], semaine_idx, row['Rappel']):
                    candidats_rappel.append(row)
    
    # Trier les candidats par priorité
    # Priorité 1 : Moins d'occurrences
    # Priorité 2 : Éviter le thème courant pour diversité
    # Priorité 3 : Préférer non-rappels aux rappels anciens
    # Priorité 4 : Ordre numérique
    candidats_rappel.sort(key=lambda r: (
        used_codes[r['Code']],           # Moins vus d'abord
        r['Code'][0] == theme,           # Éviter thème courant
        r['Rappel'],                     # Préférer automatismes normaux
        r['Num']                         # Ordre numérique
    ))
    
    # 3. COMPLÉTER LES POSITIONS DE RAPPEL
    positions_rappel = [i for i in range(6) if selection_finale[i] is None]
    
    candidat_idx = 0
    for pos in positions_rappel:
        if candidat_idx < len(candidats_rappel):
            candidat = candidats_rappel[candidat_idx]
            selection_finale[pos] = candidat['Code']
            codes_selectionnes.add(candidat['Code'])
            candidat_idx += 1
            
            # Retirer tous les automatismes avec le même code
            candidats_rappel = [c for c in candidats_rappel[candidat_idx:] 
                              if c['Code'] != candidat['Code']]
            candidat_idx = 0
    
    # 4. COMPLÉTER SI POSITIONS ENCORE VIDES (cas d'urgence)
    for i in range(6):
        if selection_finale[i] is None:
            # Relâcher les contraintes : prendre n'importe quel automatisme
            candidats_urgence = [
                row for _, row in data.iterrows()
                if (row['Code'] not in codes_selectionnes and 
                    used_codes[row['Code']] < 5)  # Limite élargie en urgence
            ]
            
            if candidats_urgence:
                # Prendre le moins utilisé
                candidat = min(candidats_urgence, key=lambda r: used_codes[r['Code']])
                selection_finale[i] = candidat['Code']
                codes_selectionnes.add(candidat['Code'])
            elif codes_selectionnes:
                # Répéter un code déjà sélectionné
                selection_finale[i] = next(iter(codes_selectionnes))
            else:
                # Cas extrême : premier automatisme disponible
                selection_finale[i] = data.iloc[0]['Code']
    
    return selection_finale   
#--------------------------------------------------------------------------
## FIN select
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
