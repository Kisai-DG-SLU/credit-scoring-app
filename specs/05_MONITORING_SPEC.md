# Spécification : Monitoring du Data Drift (T018)

## 1. Objectif
Assurer la stabilité du modèle de scoring en détectant toute divergence statistique entre les données utilisées pour l'entraînement (Référence) et les données reçues en production (Current).

## 2. Source de Données
### 2.1. Données de Référence (Reference)
- **Source** : Base de données SQLite `data/database.sqlite`, table `clients`.
- **Échantillonnage** : Un échantillon aléatoire de 10 000 individus (pour limiter l'usage mémoire).
- **Prétraitement** : Exclusion de la colonne `TARGET` et `SK_ID_CURR`.

### 2.2. Données Actuelles (Current)
- **Source** : Identifiants clients (`SK_ID_CURR`) récupérés lors des appels API.
- **Recommandation** : Passer d'un log texte (`api.log`) à un stockage structuré (Table SQLite `prediction_logs`) pour faciliter l'extraction automatique des features associées.

## 3. Périmètre de l'Analyse (Features Clés)
Pour optimiser la lisibilité et la performance, le monitoring se concentrera sur le Top-10 des variables les plus importantes pour le modèle :
1. `EXT_SOURCE_1`
2. `EXT_SOURCE_2`
3. `EXT_SOURCE_3`
4. `PAYMENT_RATE`
5. `DAYS_BIRTH`
6. `DAYS_EMPLOYED`
7. `AMT_ANNUITY`
8. `AMT_CREDIT`
9. `AMT_INCOME_TOTAL`
10. `DAYS_REGISTRATION`

## 4. Méthodologie Evidently AI
- **Test Statistique** : Jensen-Shannon (pour les variables numériques) et Chi-squared (pour les variables catégorielles).
- **Seuil d'Alerte** : Drift détecté si p-value < 0.05.
- **Livrable attendu** : Rapport HTML interactif généré par `Evidently DataDriftPreset`.

## 5. Intégration
- **Fréquence** : Exécution hebdomadaire ou déclenchée manuellement via le Dashboard.
- **Visualisation** : Le rapport HTML doit être accessible via un lien ou une page dédiée dans le Dashboard Streamlit.

## 6. Actions Correctives
En cas de détection de dérive majeure (plus de 50% des features clés en dérive) :
1. Alerte automatique (Log/Email).
2. Analyse de la cause (Changement de segment client ? Problème de pipeline ?).
3. Planification d'un réentraînement du modèle.
