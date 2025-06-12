.PHONY: test format run migrate-create migrate-up migrate-down

test:
	pytest

format:
	black app/ tests/

run:
	uvicorn app.main:app --reload

# Usage: make migrate-create m="Your message"
migrate-create:
	alembic revision --autogenerate -m "$(m)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1
	
# Set API_TOKEN for make commands. User must source .env or set it manually.
# Usage: make export-sample API_TOKEN=$(shell sed -n 's/^API_TOKEN=//p' .env)
export-sample:
ifndef API_TOKEN
	$(error API_TOKEN is not set. Usage: make export-sample API_TOKEN=<your_token>)
endif
	@echo "Exporting CSV sample..."
	@curl -s -H "Authorization: Bearer $(API_TOKEN)" "http://127.0.0.1:8000/api/v1/unsubscribed_emails/export?format=csv" -o sample_export.csv
	@echo "Exporting JSON sample..."
	@curl -s -H "Authorization: Bearer $(API_TOKEN)" "http://127.0.0.1:8000/api/v1/unsubscribed_emails/export?format=json" -o sample_export.json
	@echo "Done. See sample_export.csv and sample_export.json"