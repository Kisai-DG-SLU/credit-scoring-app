import gc
import sys
from pathlib import Path

# On importe nos fonctions définies dans features.py
import features as ft


def check_integrity(df, step_name):
    """
    Vérification critique des doublons et de la clé primaire.
    Arrête le script immédiatement si une incohérence est détectée.
    """
    print(f"--- 🛡️ Vérification intégrité : {step_name} ---")

    # Vérification des doublons sur la clé primaire (SK_ID_CURR)
    # Note : Si SK_ID_CURR est dans l'index, on vérifie l'index.
    if "SK_ID_CURR" in df.columns:
        n_dupes = df.duplicated(subset="SK_ID_CURR").sum()
    else:
        n_dupes = df.index.duplicated().sum()

    if n_dupes > 0:
        print(f"❌ ERREUR CRITIQUE : {n_dupes} doublons détectés après {step_name} !")
        sys.exit(1)  # On arrête tout pour ne pas corrompre le dataset final
    else:
        print("✅ Aucun doublon client détecté.")

    print(f"   Forme actuelle : {df.shape}")
    print("-" * 40)


def main():
    # Configuration des chemins
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_RAW_DIR = BASE_DIR / "data" / "raw"
    DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

    # Pour le dev, on peut mettre un sample. Mettre None pour la prod.
    SAMPLE_SIZE = None

    print("--- 🏗️ Démarrage du Pipeline de Preprocessing ---")

    # 1. Traitement de la table principale (Application)
    df = ft.preprocess_application_train_test(DATA_RAW_DIR, SAMPLE_SIZE)
    # Si SK_ID_CURR est une colonne, on la met en index pour faciliter les joins
    if "SK_ID_CURR" in df.columns:
        df.set_index("SK_ID_CURR", inplace=True)

    check_integrity(df, "Chargement Application")

    # 2. Bureau & Balance
    bureau = ft.preprocess_bureau_and_balance(DATA_RAW_DIR, SAMPLE_SIZE)
    df = df.join(bureau, how="left")  # Join sur l'index (SK_ID_CURR)
    del bureau
    gc.collect()
    check_integrity(df, "Join Bureau")

    # 3. Previous Applications
    prev = ft.preprocess_previous_applications(DATA_RAW_DIR, SAMPLE_SIZE)
    df = df.join(prev, how="left")
    del prev
    gc.collect()
    check_integrity(df, "Join Previous App")

    # 4. POS CASH
    pos = ft.preprocess_pos_cash_balance(DATA_RAW_DIR, SAMPLE_SIZE)
    df = df.join(pos, how="left")
    del pos
    gc.collect()
    check_integrity(df, "Join POS CASH")

    # 5. Installments
    ins = ft.preprocess_installments_payments(DATA_RAW_DIR, SAMPLE_SIZE)
    df = df.join(ins, how="left")
    del ins
    gc.collect()
    check_integrity(df, "Join Installments")

    # 6. Credit Card
    cc = ft.preprocess_credit_card_balance(DATA_RAW_DIR, SAMPLE_SIZE)
    df = df.join(cc, how="left")
    del cc
    gc.collect()
    check_integrity(df, "Join Credit Card")

    # Reset index pour sauvegarder SK_ID_CURR comme colonne
    df.reset_index(inplace=True)

    # Sauvegarde
    output_file = DATA_PROCESSED_DIR / "final_dataset.csv"
    print(f"💾 Sauvegarde du fichier unifié vers : {output_file}")
    df.to_csv(output_file, index=False)
    print("--- ✅ Terminé avec succès ! ---")


if __name__ == "__main__":
    main()
