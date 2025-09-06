# app.py
import os, io
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from rapidfuzz import fuzz

# ==============================
# Configuration et API Key
# ==============================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Clé OpenAI introuvable ! Vérifie ton fichier .env")

client = OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# Nettoyage texte
# ==============================
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    for char in ["-", "_", ".", ","]:
        text = text.replace(char, " ")
    return " ".join(text.split())

# ==============================
# Harmonisation
# ==============================
def harmonize_models(df, col_model, col_brand=None):
    df["normalized"] = df[col_model].apply(normalize_text)
    canonicals, results = {}, []

    for i, val in enumerate(df["normalized"]):
        if not val:
            results.append("")
            continue

        matched = None
        for canon in canonicals:
            if fuzz.ratio(val, canon) > 85:
                matched = canonicals[canon]
                break

        if matched:
            results.append(matched)
        else:
            brand = df[col_brand].iloc[i].upper() if col_brand else ""
            canon_name = val.upper().replace(" ", "_")
            if brand:
                canon_name = f"{brand}_{canon_name}"
            canonicals[val] = canon_name
            results.append(canon_name)

    df["model_canonique"] = results
    return df

def add_search_link(df):
    df["Lien_recherche"] = df["model_canonique"].apply(
        lambda x: f"https://www.google.com/search?q={x.replace(' ', '+')}" if x else ""
    )
    return df

# ==============================
# Interface Streamlit améliorée
# ==============================
st.set_page_config(page_title="Harmonisation PC", layout="wide")
st.title("💻 Nettoyage et harmonisation de modèles de PC")

uploaded_file = st.file_uploader("📂 Importer un fichier Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    with st.expander("📄 Aperçu du fichier original"):
        st.dataframe(df.head())

    # Sélection des colonnes
    col1, col2 = st.columns(2)
    with col1:
        col_model = st.selectbox("Colonne contenant **le modèle**", df.columns)
    with col2:
        col_brand = st.selectbox("Colonne contenant **la marque (optionnel**)", [None] + list(df.columns))

    # Harmonisation
    df_clean = harmonize_models(df, col_model, col_brand)
    df_clean = add_search_link(df_clean)

    with st.expander("✅ Aperçu après harmonisation"):
        st.dataframe(df_clean.head(), use_container_width=True)

    # Export et téléchargement
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_clean.to_excel(writer, index=False, sheet_name="Harmonized")
    output.seek(0)

    st.download_button(
        label="⬇️ Télécharger le fichier harmonisé",
        data=output,
        file_name="harmonized_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

import matplotlib.pyplot as plt
from pywaffle import Waffle
# ==============================
# Waffle Chart par modèle canonique
# ==============================

st.subheader("Make love ❤️ not the war 🪖")
