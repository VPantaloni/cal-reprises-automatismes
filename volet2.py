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
