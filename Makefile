.PHONY: install test lint format run-api clean rotate-logs

# --- Maintenance ---
rotate-logs:
	@./scripts/rotate_logs.sh

# --- Installation & Setup ---
install: rotate-logs
	conda env update --file environment.yml --prune

# --- Development ---
lint: rotate-logs
	ruff check .
	black --check .

format: rotate-logs
	black .
	ruff check . --fix

test: rotate-logs
	pytest --cov=src --cov-report=term-missing --cov-report=html

# --- Execution ---
run-api: rotate-logs
	uvicorn src.api.main:app --reload

# --- Cleanup ---
clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache coverage.html
	find . -type d -name "__pycache__" -exec rm -rf {} +