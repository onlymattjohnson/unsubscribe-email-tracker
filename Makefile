.PHONY: test format run migrate

test:
	pytest tests/

format:
	black app/ tests/

run:
	uvicorn app.main:app --reload

migrate:
	alembic upgrade head