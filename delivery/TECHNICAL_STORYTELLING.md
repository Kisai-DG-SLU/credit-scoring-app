# 🧠 Storytelling Technique & Engineering Decisions

Ce document résume les défis rencontrés lors du développement et les solutions apportées. Il sert de base pour la partie "Discussion" de la soutenance.

## 1. Problématique : La Contrainte des Ressources (Cloud vs Big Data)
- **Le Défi** : Déployer un modèle entraîné sur un dataset de 1.3 Go sur une infrastructure "Low Cost" (Hugging Face Spaces) limitée en RAM.
- **La Décision** : Migration vers une architecture **Hybrid SQLite**.
- **Le Gain** : Passage de 6 Go de RAM consommée à seulement 50 Mo. L'API est plus stable et démarre 10x plus vite.

## 2. Problématique : L'Inférence "Temps Réel" vs Coût SHAP
- **Le Défi** : Le calcul des valeurs SHAP pour l'explicabilité locale est très coûteux en CPU (~250ms), ce qui ralentit l'API.
- **La Décision** : Mise en place d'un **Cache LRU (Least Recently Used)**.
- **Le Gain** : Pour un client déjà consulté (cas fréquent en agence bancaire), le résultat est retourné en 0.001ms.

## 3. Problématique : L'Industrialisation (Format ONNX)
- **Le Défi** : Éviter la dépendance stricte à la bibliothèque LightGBM pour l'inférence.
- **La Décision** : Conversion du modèle au format **ONNX (Open Neural Network Exchange)**.
- **Le Gain** : Standardisation du format de modèle. L'API peut désormais charger n'importe quel modèle (XGBoost, Scikit-Learn, PyTorch) tant qu'il est au format ONNX, sans modification du code source.

## 4. Problématique : La Fiabilité du Monitoring (Faux Positifs de Drift)
- **Le Défi** : Éviter les alertes de Data Drift erronées dues à un faible volume de données en début de production.
- **La Décision** : Implémentation d'un **Indicateur de Confiance Statistique**.
- **Le Gain** : Le dashboard informe l'utilisateur si les données sont suffisantes ($N > 500$) pour que le test statistique soit valide, évitant des décisions basées sur du bruit.

## 5. Problématique : La Robustesse aux "Data Quality" Issues
- **Le Défi** : Gérer les clients avec des données incomplètes (NaNs) sans faire crasher l'API.
- **La Décision** : Intégration d'un pipeline de prétraitement robuste dans le `Loader` qui gère les types et les valeurs manquantes avant l'inférence.
- **Le Gain** : Taux de crash de l'API proche de 0% sur les cas limites testés (données aberrantes ou manquantes).
