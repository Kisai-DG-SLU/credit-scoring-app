import os
from google import genai

# Récupère ta clé depuis l'env (supporte GEMINI_ ou GOOGLE_)
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("❌ Pas de clé API trouvée. Vérifie ton env.")
    exit(1)

client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

print("🔍 Recherche des modèles Gemini 3 disponibles...")
print("-" * 40)

try:
    # Liste tous les modèles
    for m in client.models.list():
        # Filtre pour n'afficher que les pertinents (3 + flash)
        if "gemini" in m.name and "3" in m.name:
            print(f"✅ Trouvé : {m.name}")
            print(f"   Display: {m.display_name}")
            print("-" * 20)

    print(
        "\n(Si la liste est vide, vérifie que tu as accès à la preview via ce projet GCP/Clé API)"
    )

except Exception as e:
    print(f"❌ Erreur API : {e}")
