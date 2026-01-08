.PHONY: install test run view

install:
	pip install -r requirements.txt

test:
	pytest tests/

run:
	python src/main.py

view:
	grip docs/ -b
