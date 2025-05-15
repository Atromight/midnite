.PHONY: format lint test check

ENTRY_POINT := "midnite_api.main:app"
SERVER_PORT := 5000

run:
	poetry run uvicorn --host 0.0.0.0 --port ${SERVER_PORT} ${ENTRY_POINT}

format:
	poetry run black .

lint:
	poetry run flake8 .

test:
	poetry run pytest

check: format lint test

clean:
	rm -rf midnite_api/__pycache__ midnite_api/app.db
