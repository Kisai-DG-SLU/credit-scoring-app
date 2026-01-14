# Utiliser une image de base Python légère
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="Damien Guesdon"
LABEL description="API de Scoring Crédit (Projet 8) - Optimized Build"

# Définir le répertoire de travail
WORKDIR /app

# Installation des dépendances système minimales (nécessaires pour lightgbm/shap)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances via pip
RUN pip install --no-cache-dir -r requirements.txt

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

# Variables d'environnement
ENV HOME=/app
ENV PYTHONPATH=/app
ENV MPLCONFIGDIR=/tmp/matplotlib
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Exposer les ports (API + Dashboard)
EXPOSE 8000
EXPOSE 8501

# Lancer le script d'entrypoint directement
ENTRYPOINT ["./entrypoint.sh"]