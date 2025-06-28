# volet2.py
import streamlit as st
import pandas as pd
from io import BytesIO

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
    
    # Affichage en 3 colonnes avec surplus dans la dernière
    cols = st.columns(3)
    nb = len(recap_data)
    chunk_size = nb // 3
    for j in range(3):
        start = j * chunk_size
        end = (j + 1) * chunk_size if j < 2 else nb  # Dernière colonne prend le reste
        for r in recap_data[start:end]:
            with cols[j]:
                st.markdown(
                    f"<div style='padding:2px; margin:2px; border: 3px solid {r['Couleur']}; "
                    f"background:transparent; border-radius:4px; font-size:0.8em;'>"
                    f"<b>{r['Code']}</b> : {r['Automatisme']}<br>"
                    f"<small><i>Semaine(s)</i> : {r['Semaines']}</small></div>",
                    unsafe_allow_html=True
                )
    
    # Génération export Excel
    buffer = BytesIO()
    grille_data = []
    
    # Déterminer le nombre de semaines et d'automatismes selon le mode
    nb_semaines = 32 if st.session_state.mode_affichage == "32_semaines" else 35
    nb_automatismes = 6 if st.session_state.mode_affichage == "32_semaines" else 9
    
    for i in range(nb_semaines):
        semaine = f"S{i+1}"
        theme_emoji = st.session_state.sequences[i] if i < len(st.session_state.sequences) and st.session_state.sequences[i] else ""
        theme_label = subtheme_legend.get(theme_emoji, "")
        auto_codes = st.session_state.selection_by_week[i] if i < len(st.session_state.selection_by_week) else []
        
        # Compléter ou tronquer la liste pour avoir exactement nb_automatismes éléments
        auto_codes = auto_codes[:nb_automatismes] + [""] * (nb_automatismes - len(auto_codes))
        
        grille_data.append([semaine, f"{theme_emoji} {theme_label}"] + auto_codes)
    
    # Créer les colonnes selon le mode
    colonnes = ["Semaine", "Thème semaine"] + [f"Auto{i+1}" for i in range(nb_automatismes)]
    df_grille = pd.DataFrame(grille_data, columns=colonnes)
    df_recap = pd.DataFrame(recap_data)
    
    # Export Excel
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_grille.to_excel(writer, index=False, sheet_name='Grille')
        df_recap.to_excel(writer, index=False, sheet_name='Lecture_par_automatisme')
    
    # Nom du fichier selon le mode
    mode_text = "32sem_6auto" if st.session_state.mode_affichage == "32_semaines" else "35sem_9auto"
    filename = f"planning_reprises_{mode_text}.xlsx"
    
    st.download_button(
        label=f"📅 Télécharger le planning Excel ({mode_text})",
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
