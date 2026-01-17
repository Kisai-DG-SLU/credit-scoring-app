import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
DB_PATH = "data/database.sqlite"
LITE_DB_PATH = "data/database_lite.sqlite"
OUTPUT_DIR = "delivery/proof/screenshots"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_logs_proof():
    print("📸 Génération de la preuve de logs...")
    if not os.path.exists(DB_PATH):
        print(f"❌ Erreur: {DB_PATH} introuvable.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT timestamp, client_id, score, latency FROM prediction_logs ORDER BY timestamp DESC LIMIT 15",
            conn,
        )
        conn.close()

        if df.empty:
            print("⚠️ Attention: Table logs vide.")
            return

        # Création de l'image du tableau
        fig, ax = plt.subplots(figsize=(10, 6))  # Ajusté pour ~15 lignes
        ax.axis("tight")
        ax.axis("off")

        # Table
        table = ax.table(
            cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center"
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.2)

        plt.title(
            f"Preuve de Logging Automatique ({len(df)} derniers logs)",
            fontsize=14,
            pad=20,
        )
        plt.savefig(
            f"{OUTPUT_DIR}/prediction_logs_proof.png", bbox_inches="tight", dpi=150
        )
        plt.close()
        print(f"✅ Image générée : {OUTPUT_DIR}/prediction_logs_proof.png")

    except Exception as e:
        print(f"❌ Erreur lors de la génération des logs : {e}")


def generate_size_proof():
    print("📸 Génération de la preuve de taille BDD...")

    sizes = {}
    if os.path.exists(DB_PATH):
        sizes["Full DB (Local)"] = os.path.getsize(DB_PATH) / (1024 * 1024)  # MB

    if os.path.exists(LITE_DB_PATH):
        sizes["Lite DB (Prod)"] = os.path.getsize(LITE_DB_PATH) / (1024 * 1024)  # MB

    if not sizes:
        print("❌ Aucune base trouvée pour comparaison.")
        return

    names = list(sizes.keys())
    values = list(sizes.values())

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(names, values, color=["#1f77b4", "#2ca02c"])

    # Ajout des labels
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f} MB",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    plt.title("Comparaison Empreinte Mémoire (Optimisation Cloud)", fontsize=14)
    plt.ylabel("Taille (MB)")

    # Ajout d'un texte explicatif dans l'image
    plt.figtext(
        0.5,
        -0.05,
        "Lite DB permet le déploiement sur Hugging Face Spaces (RAM limitée)",
        ha="center",
        fontsize=10,
        style="italic",
    )

    plt.savefig(f"{OUTPUT_DIR}/lite_db_proof.png", bbox_inches="tight", dpi=150)
    plt.close()
    print(f"✅ Image générée : {OUTPUT_DIR}/lite_db_proof.png")


if __name__ == "__main__":
    generate_logs_proof()
    generate_size_proof()
