import streamlit as st
import pandas as pd
from io import BytesIO
from urllib.parse import quote

def render_ui(df_harmonized: pd.DataFrame):
    st.set_page_config(
        page_title="💻 Harmonisation PC",
        page_icon="💻",
        layout="wide"
    )

    # --- HEADER ---
    st.markdown("<h1 style='text-align:center; color:#4B8BBE;'>💻 Nettoyeur de Modèles PC</h1>", unsafe_allow_html=True)
    st.markdown(
        "Importez votre fichier Excel, choisissez la colonne contenant les modèles, "
        "et cliquez sur Harmoniser pour obtenir la version canonique avec liens de recherche.", 
        unsafe_allow_html=True
    )
    st.markdown("---")

    # --- SIDEBAR ---
    st.sidebar.header("Options")
    if not df_harmonized.empty:
        column_to_use = st.sidebar.selectbox("Colonne à afficher", df_harmonized.columns)
    st.sidebar.info(f"Nombre de PC traités : {len(df_harmonized)}")

    # --- DATAFRAME ---
    if not df_harmonized.empty:
        st.subheader("Aperçu des données harmonisées")

        # Génération des liens cliquables Google
        if "model_canonique" in df_harmonized.columns:
            df_harmonized["Lien_recherche"] = df_harmonized["model_canonique"].apply(
                lambda x: f"[🔍 Rechercher](https://www.google.com/search?q={quote(str(x))})"
            )

        # Affichage colonnes sélectionnées
        display_cols = ["model_canonique", "Lien_recherche"]
        if column_to_use:
            display_cols = [column_to_use] + display_cols

        st.dataframe(df_harmonized[display_cols], use_container_width=True)

        # --- BOUTON DE TÉLÉCHARGEMENT EXCEL ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_harmonized.to_excel(writer, index=False, sheet_name="Harmonisation")
            writer.close()
        output.seek(0)

        st.download_button(
            label="📥 Télécharger le fichier harmonisé",
            data=output,
            file_name="fichier_harmonisé.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --- BARRE DE PROGRESSION ---
        st.subheader("Progression du traitement")
        progress_bar = st.progress(0)
        for i in range(1, 101):
            progress_bar.progress(i)
