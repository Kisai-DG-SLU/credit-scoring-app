# Guide pour les Captures d'Écran (Preuve T047)

Ce dossier doit contenir les preuves visuelles de la solution de stockage des données.

## 1. Preuve de la collecte des logs (prediction_logs_proof.png)
**Action :** 
1. Ouvrez `data/database.sqlite` avec un outil comme "DB Browser for SQLite".
2. Ouvrez l'onglet "Parcourir les données" et sélectionnez la table `prediction_logs`.
3. **IMPORTANT** : Assurez-vous que la colonne `latency` est bien visible sur la capture (scrollez horizontalement si nécessaire).
4. Vérifiez que des données sont présentes (générées par la simulation).
5. **Prenez une capture d'écran** montrant clairement les colonnes (`client_id`, `score`, `timestamp`, `latency`).
6. Enregistrez l'image ici : `delivery/proof/screenshots/prediction_logs_proof.png`.

## 2. Preuve de l'optimisation Database Lite (lite_db_proof.png)
**Action :**
1. Dans votre explorateur de fichiers, montrez le dossier `data/`.
2. Mettez en évidence la différence de taille entre `database.sqlite` (~800 Mo) et `database_lite.sqlite` (<10 Mo).
3. **Prenez une capture d'écran**.
4. Enregistrez l'image ici : `delivery/proof/screenshots/lite_db_proof.png`.

## Justification de la stratégie (à inclure dans le rapport)
- **Pourquoi SQLite ?** : Performance (lecture <10ms), simplicité (fichier unique), et compatibilité parfaite avec l'environnement conteneurisé stateless (Hugging Face) via la version Lite.
- **Pourquoi Database Lite ?** : Réduction de l'empreinte mémoire pour le déploiement cloud gratuit (limite RAM), tout en conservant un échantillon représentatif pour le monitoring de base.
- **Log Table** : Permet un suivi granulaire des entrées (Features), sorties (Score) et performances (Latence) pour l'analyse de Data Drift ultérieure.