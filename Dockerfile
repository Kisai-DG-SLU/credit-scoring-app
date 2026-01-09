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

# Copier le code source de l'application
COPY src/ src/
COPY .env.template .env

# S'assurer que l'utilisateur non-root a les droits sur le répertoire de travail
RUN chown -R appuser:appuser /app

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port de l'API
EXPOSE 8000

# Utiliser conda run pour exécuter l'application dans l'environnement activé
# L'option --no-capture-output permet de voir les logs en temps réel
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "credit-scoring-app", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
