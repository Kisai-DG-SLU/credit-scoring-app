import streamlit as st
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Credit Scoring Dashboard", layout="wide")

st.title("🏦 Dashboard de Scoring Crédit")
st.markdown("---")

# Configuration de l'API
API_URL = st.sidebar.text_input("URL de l'API", "http://localhost:8000")

st.sidebar.header("Paramètres Client")
client_id = st.sidebar.number_input("ID Client", min_value=100001, value=100001, step=1)

if st.sidebar.button("Prédire"):
    with st.spinner("Requête à l'API en cours..."):
        try:
            response = requests.get(f"{API_URL}/predict/{client_id}")

            if response.status_code == 200:
                data = response.json()

                # Mise en page des résultats
                col1, col2 = st.columns(2)

                with col1:
                    st.header(f"Client {client_id}")
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

                with col2:
                    st.header("Analyse de risque")
                    # Visualisation simple du score vs seuil
                    fig, ax = plt.subplots(figsize=(5, 2))
                    ax.barh(["Probabilité"], [score], color=color, alpha=0.6)
                    ax.axvline(threshold, color="black", linestyle="--", label="Seuil")
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

st.markdown("---")
st.info(
    "Ce dashboard interagit avec l'API FastAPI pour fournir une aide à la décision en temps réel."
)
