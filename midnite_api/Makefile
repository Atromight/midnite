ENTRY_POINT := "midnite_api.main:app"
SERVER_PORT := 5000

run:
	poetry run uvicorn --host 0.0.0.0 --port ${SERVER_PORT} --reload ${ENTRY_POINT}
