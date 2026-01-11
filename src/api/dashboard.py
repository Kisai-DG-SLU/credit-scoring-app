import streamlit as st
import requests
import matplotlib.pyplot as plt
import os

from src.model.monitoring import generate_drift_report

st.set_page_config(page_title="Credit Scoring Dashboard", layout="wide")

st.title("🏦 Dashboard de Scoring Crédit")
st.markdown("---")

# Configuration de l'API (Sidebar commune)
API_URL = st.sidebar.text_input("URL de l'API", "http://localhost:8000")

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
                response = requests.get(f"{API_URL}/predict/{client_id}")

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
    st.header("Monitoring du Modèle (Data Drift)")
    st.markdown(
        "Analyse de la dérive des données entre l'entraînement (Reference) et la production (Current)."
    )

    DB_PATH = "data/database.sqlite"
    REPORT_PATH = "data/drift_report.html"

    if st.button("🔄 Générer le rapport de dérive"):
        with st.spinner("Analyse de la dérive en cours (Evidently AI)..."):
            # On génère le rapport
            result = generate_drift_report(DB_PATH, REPORT_PATH)

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
