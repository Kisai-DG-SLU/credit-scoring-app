.PHONY: install test run view chat save-brain

install:
	pip install -r requirements.txt

test:
	pytest tests/

run:
	python src/main.py

view:
	grip docs/ -b

# Lance l'interface interactive BMAD
chat:
	@gemini

# Sauvegarde intelligente vers le Cerveau
save-brain:
	@echo "🧠 Sauvegarde Stealth vers Guesdon-Brain..."
	@mkdir -p "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_8/credit-scoring-app"
	@cp GEMINI.md "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_8/credit-scoring-app/" 2>/dev/null || true
	@cp -r specs/ "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_8/credit-scoring-app/specs/" 2>/dev/null || true
	@# On sauvegarde aussi la config BMAD locale (agents custom)
	@cp -r _bmad/ "/Users/daminou/Dev/Guesdon-Brain/Formation_IA/Projet_8/credit-scoring-app/_bmad/" 2>/dev/null || true
	@cd "/Users/daminou/Dev/Guesdon-Brain" && git add . && git commit -m "Backup: credit-scoring-app" && git push origin master && echo "✅ Brain Synced!"
