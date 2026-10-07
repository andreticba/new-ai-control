# Makefile | AI-Control SDD v0.6.0 | 27-09-2026 20:00(GMT-04:00)

.PHONY: up down migrate worker shell test

up:
	docker compose up -d
	@echo "Serviços em Docker rodando."
	@echo "Iniciando Daphne localmente..."
	daphne -b 0.0.0.0 -p 8000 config.asgi:application

down:
	docker compose down

migrate:
	python manage.py migrate

worker:
	celery -A config worker -l INFO

shell:
	python manage.py shell

test:
	pytest --cov=core --cov-report=term-missing
