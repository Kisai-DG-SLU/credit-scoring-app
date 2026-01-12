# Utiliser une image de base officielle Miniconda
FROM continuumio/miniconda3:latest

# Métadonnées
LABEL maintainer="Damien Guesdon"
LABEL description="API de Scoring Crédit (Projet 8)"

# Définir le répertoire de travail
WORKDIR /app

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copier le fichier de configuration de l'environnement
COPY environment.yml .

# Installer les dépendances et nettoyer le cache pour réduire la taille de l'image
RUN conda env create -f environment.yml && \
    conda clean -afy

# Copier le code source de l'application et les données
COPY src/ src/
COPY data/ data/
COPY .env.template .env
COPY entrypoint.sh .

# S'assurer que l'utilisateur non-root a les droits sur le répertoire de travail
# et rendre le script d'entrypoint exécutable
RUN chown -R appuser:appuser /app && chmod +x entrypoint.sh

# Passer à l'utilisateur non-root
USER appuser

# Variables d'environnement pour l'utilisateur non-root
ENV HOME=/app
ENV PYTHONPATH=/app
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Exposer les ports (API + Dashboard)
EXPOSE 8000
EXPOSE 8501

# Utiliser conda run pour exécuter le script d'entrypoint
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "credit-scoring-app", "./entrypoint.sh"]
