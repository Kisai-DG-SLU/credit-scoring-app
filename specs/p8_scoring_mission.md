# Mission : Scoring de Crédit - "Prêt à dépenser"

## Contexte
L'entreprise "Prêt à dépenser" souhaite développer un **outil de scoring crédit** pour calculer la probabilité qu'un client rembourse son crédit, puis classer la demande en crédit accordé ou refusé. Elle souhaite donc développer un algorithme de classification en s'appuyant sur des sources de données variées (données comportementales, données provenant d'autres institutions financières, etc.).

## Objectifs du Projet
1. **Modélisation** : Construire un modèle de classification pour prédire le risque de défaut de paiement.
2. **Interprétabilité** : Analyser les variables qui ont le plus de poids dans le modèle (feature importance globale et locale).
3. **API** : Mettre en place une API pour exposer le modèle de scoring.
4. **Dashboard** : Créer un dashboard interactif à destination des chargés de relation client pour expliquer de manière transparente les décisions d'octroi de crédit.
5. **MLOps** : Mettre en place une démarche de type MLOps (tracking d'expérimentations, tests unitaires, CI/CD).

## Données
Les données sont issues du dataset [Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk/data) sur Kaggle.

## Livrables Attendus
- Un notebook (ou script) de préparation des données et de feature engineering.
- Un notebook (ou script) d'entraînement du modèle et de sélection du meilleur modèle.
- Une note méthodologique décrivant la démarche.
- Le code de l'API déployée.
- Le code du Dashboard interactif.
- Un repo GitHub avec :
    - Le code source.
    - Un fichier `requirements.txt`.
    - Des tests unitaires (via Pytest).
    - Une configuration CI/CD (GitHub Actions).
