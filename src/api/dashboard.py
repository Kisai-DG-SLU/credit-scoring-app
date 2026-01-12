import streamlit as st
import requests
import matplotlib.pyplot as plt
import os
import shap
import numpy as np
import plotly.express as px
import pandas as pd
import sqlite3

from src.model.monitoring import generate_drift_report
from src.model.loader import loader


def get_cached_drift_report(db_path, report_path):
    return generate_drift_report(db_path, report_path)


st.set_page_config(page_title="Credit Scoring Dashboard", layout="wide")

st.title("🏦 Dashboard de Scoring Crédit")
st.markdown("---")

# Configuration de l'API (Sidebar commune)
API_URL = st.sidebar.text_input("URL de l'API", "http://localhost:8000")


@st.cache_data(show_spinner=False)
def get_prediction(api_url, client_id):
    return requests.get(f"{api_url}/predict/{client_id}")


# Onglets
tab_scoring, tab_monitoring = st.tabs(["Scoring Client", "Monitoring Data Drift"])

# --- ONGLET 1 : SCORING ---
with tab_scoring:
    st.header("Prédiction de Solvabilité")

    col_input, col_res = st.columns([1, 2])

    with col_input:
        st.subheader("Paramètres")
        client_id = st.number_input("ID Client", min_value=100001, value=100001, step=1)
        predict_btn = st.button("Prédire", type="primary")

    if predict_btn:
        with st.spinner("Requête à l'API en cours..."):
            try:
                response = get_prediction(API_URL, client_id)

                if response.status_code == 200:
                    data = response.json()

                    with col_res:
                        # Mise en page des résultats
                        col_metrics, col_chart = st.columns(2)

                        with col_metrics:
                            st.subheader(f"Résultat Client {client_id}")
                            score = data["score"]
                            threshold = data["threshold"]
                            decision = data["decision"]

                            color = "red" if decision == "Refusé" else "green"
                            st.markdown(
                                f"### Décision : <span style='color:{color}'>{decision}</span>",
                                unsafe_allow_html=True,
                            )
                            st.metric("Probabilité de défaut", f"{score:.2%}")

                            # Barre de score
                            st.progress(score)
                            st.caption(f"Seuil de refus : {threshold:.2f}")

                        with col_chart:
                            st.subheader("Analyse de risque")
                            # Visualisation simple du score vs seuil
                            fig, ax = plt.subplots(figsize=(5, 2))
                            ax.barh(["Probabilité"], [score], color=color, alpha=0.6)
                            ax.axvline(
                                threshold, color="black", linestyle="--", label="Seuil"
                            )
                            ax.set_xlim(0, 1)
                            ax.legend()
                            st.pyplot(fig)

                    # --- EXPLICABILITÉ (SHAP) ---
                    st.markdown("---")
                    st.subheader("🔍 Explication de la décision (Waterfall SHAP)")

                    if "shap_values" in data and data["shap_values"]:
                        shap_vals_dict = data["shap_values"]
                        base_val = data.get("base_value", 0.0)

                        # Reconstitution d'un objet Explanation pour shap.plots.waterfall
                        # comme utilisé dans le notebook du Projet 6
                        features_names = list(shap_vals_dict.keys())
                        values = list(shap_vals_dict.values())

                        # Création de l'objet Explanation conforme à l'API SHAP
                        exp = shap.Explanation(
                            values=np.array(values),
                            base_values=base_val,
                            data=np.array([0] * len(values)),
                            feature_names=features_names,
                        )

                        fig_shap = plt.figure(figsize=(10, 6))
                        # Appel exact identifié dans le notebook P6
                        shap.plots.waterfall(exp, max_display=15, show=False)
                        st.pyplot(plt.gcf())

                        st.info(
                            "💡 Ce graphique Waterfall (identique au Projet 6) montre l'impact de chaque caractéristique sur la décision finale."
                        )
                    else:
                        st.warning(
                            "Aucune donnée d'explicabilité disponible pour ce client."
                        )

                elif response.status_code == 404:
                    st.error(f"Client {client_id} non trouvé dans la base.")
                else:
                    st.error(f"Erreur API ({response.status_code}) : {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Impossible de contacter l'API. Assurez-vous qu'elle est lancée sur "
                    + API_URL
                )

# --- ONGLET 2 : MONITORING ---
with tab_monitoring:
    st.header("Monitoring du Modèle (Production)")

    # --- NOUVELLE SECTION : STATISTIQUES DE PRODUCTION ---
    st.subheader("📈 Statistiques de Production (Temps Réel)")

    DB_PATH = loader.db_path

    try:
        conn = sqlite3.connect(DB_PATH)
        df_logs = pd.read_sql_query(
            "SELECT score, latency, timestamp FROM prediction_logs", conn
        )
        conn.close()

        if not df_logs.empty:
            df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])

            col_stat1, col_stat2 = st.columns(2)

            with col_stat1:
                st.markdown("**Distribution des Scores (Production)**")
                fig_score = px.histogram(
                    df_logs,
                    x="score",
                    nbins=20,
                    color_discrete_sequence=["#008bfb"],
                    labels={"score": "Probabilité de défaut"},
                )
                fig_score.add_vline(
                    x=0.49, line_dash="dash", line_color="red", annotation_text="Seuil"
                )
                st.plotly_chart(fig_score, width="stretch")

            with col_stat2:
                st.markdown("**Latence des Prédictions (ms)**")
                if "latency" in df_logs.columns and df_logs["latency"].notnull().any():
                    df_logs["latency_ms"] = df_logs["latency"] * 1000
                    fig_lat = px.line(
                        df_logs.sort_values("timestamp"),
                        x="timestamp",
                        y="latency_ms",
                        color_discrete_sequence=["#ff0051"],
                    )
                    st.plotly_chart(fig_lat, width="stretch")
                else:
                    st.info("Données de latence en attente de collecte.")
        else:
            st.info("Aucun log de prédiction disponible pour le moment.")
    except Exception as e:
        st.error(f"Erreur lors de la lecture des statistiques : {e}")

    st.markdown("---")
    st.subheader("🔍 Analyse de la dérive (Data Drift)")
    st.markdown(
        "Analyse de la dérive des données entre l'entraînement (Reference) et la production (Current)."
    )

    DB_PATH = loader.db_path
    REPORT_PATH = "data/drift_report.html"

    if st.button("🔄 Générer le rapport de dérive"):
        with st.spinner("Analyse de la dérive en cours (Evidently AI)..."):
            # On génère le rapport (caché)
            result = get_cached_drift_report(DB_PATH, REPORT_PATH)

            if result:
                st.success(f"Rapport généré avec succès ! ({result})")
            else:
                st.error(
                    "Erreur lors de la génération du rapport. Vérifiez qu'il y a des données dans 'prediction_logs' et 'clients'."
                )

    st.markdown("---")

    if os.path.exists(REPORT_PATH):
        st.subheader("Visualisation du Rapport")
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as f:
                html_content = f.read()
            # Affichage HTML scrollable
            st.components.v1.html(html_content, height=1000, scrolling=True)

            # Bouton de téléchargement
            st.download_button(
                label="📥 Télécharger le rapport HTML",
                data=html_content,
                file_name="drift_report.html",
                mime="text/html",
            )
        except Exception as e:
            st.error(f"Erreur lors de la lecture du rapport : {e}")
    else:
        st.info("Aucun rapport disponible pour le moment.")
