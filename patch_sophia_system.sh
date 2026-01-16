#!/bin/bash

# 1. MISE À JOUR DU SCRIPT PYTHON
cat << 'EOF' > ~/Dev/tools/sophia_brain.py
import os
import sys
import argparse
import google.generativeai as genai
from google.generativeai import caching
import datetime

# Configuration API
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def list_caches():
    print(f"\n{'='*60}")
    print(f"📊 ÉTAT DES CONTEXT CACHES (GOOGLE AI)")
    print(f"{'='*60}")
    found = False
    try:
        for c in caching.CachedContent.list():
            found = True
            expire_time = c.expire_time.strftime('%Y-%m-%d %H:%M:%S')
            tokens = c.usage_metadata.total_token_count
            print(f"ID      : {c.name}")
            print(f"Modèle  : {c.model}")
            print(f"Tokens  : {tokens:,}")
            print(f"Expire  : {expire_time}")
            print(f"{'-'*60}")
    except Exception as e:
        print(f"Erreur lors de la lecture du cache : {e}")
    if not found:
        print("Aucun cache actif trouvé.")

def clear_caches():
    print("🧹 Nettoyage des caches en cours...")
    for c in caching.CachedContent.list():
        caching.CachedContent.delete(c.name)
        print(f"✅ Cache supprimé : {c.name}")

def run_chat(prompt, cache_id=None):
    try:
        if cache_id:
            cache = caching.CachedContent.get(cache_id)
            model = genai.GenerativeModel(model_name=cache.model)
            response = model.generate_content(prompt)
        else:
            model = genai.GenerativeModel(model_name="gemini-1.5-pro")
            response = model.generate_content(prompt)

        # TÉLÉMÉTRIE
        m = response.usage_metadata
        print(f"\n{'—'*40}")
        print(f"⚡ [TÉLÉMÉTRIE SOPHIA]")
        print(f"  └─ Tokens CACHE (réutilisés) : {m.cached_content_token_count:,}")
        print(f"  └─ Tokens INPUT (nouveaux)    : {m.prompt_token_count:,}")
        print(f"  └─ Tokens OUTPUT (réponse)   : {m.candidates_token_count:,}")
        print(f"  └─ Coût total de l'appel     : {m.total_token_count:,} tokens")
        print(f"{'—'*40}\n")
        
        print(response.text)
    except Exception as e:
        print(f"❌ Erreur lors du chat : {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sophia Brain Interface')
    parser.add_argument('prompt', nargs='?', help='Ta question')
    parser.add_argument('--cache-id', help='ID du cache')
    parser.add_argument('--list', action='store_true', help='Lister')
    parser.add_argument('--clear', action='store_true', help='Nettoyer')
    
    args = parser.parse_args()

    if args.list:
        list_caches()
    elif args.clear:
        clear_caches()
    elif args.prompt:
        run_chat(args.prompt, args.cache_id)
    else:
        parser.print_help()
EOF

# 2. AJOUT DES FONCTIONS ZSH (sans doublons)
if ! grep -q "brain-cache" ~/.zsh_custom/03_functions.zsh; then
cat << 'EOF' >> ~/.zsh_custom/03_functions.zsh

# --- SOPHIA CACHE MANAGEMENT ---
brain-cache() {
    if [[ "$1" == "--list" ]]; then
        python3 ~/Dev/tools/sophia_brain.py --list
    elif [[ "$1" == "--clear" ]]; then
        python3 ~/Dev/tools/sophia_brain.py --clear
    else
        echo "Usage: brain-cache [--list | --clear]"
    fi
}
EOF
fi

echo "✅ Mise à jour de Sophia terminée."
echo "👉 Tape 'source ~/.zsh_custom/03_functions.zsh' pour activer les changements."
