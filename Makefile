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