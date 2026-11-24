.PHONY: install lint format test cov run

install:
	pip install -r requirements-dev.txt

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	pytest

cov:
	pytest --cov --cov-report=term --cov-report=xml

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
