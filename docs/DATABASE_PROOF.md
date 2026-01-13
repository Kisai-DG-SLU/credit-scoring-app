# Dossier de Preuve : Base de Données & Traçabilité

Ce document prouve la mise en place d'un système de stockage structuré pour les données clients et les logs de prédiction, conformément aux exigences MLOps.

## 1. Structure de la Base de Données (SQLite)

Le projet utilise SQLite pour optimiser l'accès aux données. Voici le schéma des tables principales :

### Table `clients` (Données de référence)
Cette table contient les features pré-calculées pour les 307 511 clients du dataset. Un index est présent sur `SK_ID_CURR` pour garantir des performances optimales.

### Table `prediction_logs` (Traçabilité)
Cette table enregistre chaque prédiction effectuée par l'API pour permettre le monitoring ultérieur du Data Drift.

```sql
CREATE TABLE prediction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    score REAL,
    decision TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    EXT_SOURCE_1 REAL, 
    EXT_SOURCE_2 REAL, 
    EXT_SOURCE_3 REAL, 
    PAYMENT_RATE REAL, 
    DAYS_BIRTH REAL, 
    DAYS_EMPLOYED REAL, 
    AMT_ANNUITY REAL, 
    AMT_CREDIT REAL, 
    AMT_INCOME_TOTAL REAL, 
    DAYS_REGISTRATION REAL,
    LATENCY REAL
);
CREATE INDEX idx_prediction_logs_client_id ON prediction_logs(client_id);
```

## 2. Preuve de Fonctionnement (Logs Temps Réel)

Voici un extrait des dernières prédictions enregistrées dans la base de données (générées lors du test d'intégration du 12/01/2026) :

| Client ID | Score | Décision | Timestamp |
| :--- | :--- | :--- | :--- |
| 100004 | 0.2792 | Accordé | 2026-01-12 20:56:15 |
| 100431 | 0.7453 | Refusé | 2026-01-12 20:56:15 |

## 3. Optimisation Performance

- **Indexation** : L'accès à un client parmi 300 000 se fait en moins de 1ms.
- **Empreinte** : La base de données `database_lite.sqlite` (utilisée pour la démo) pèse moins de 10 Mo.
- **Hybridation** : Le système bascule automatiquement sur la base complète (850 Mo) si elle est présente en local.
