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

# === BLOC ALGORITHMIQUE À VENIR ===

# (Ce bloc sera complété avec :
#   - chargement CSV (Auto-6e.csv)
#   - initialisation des variables et états
#   - calcul automatique des automatismes placés
#   - affichage dynamique des pastilles et export Excel)
