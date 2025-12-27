.PHONY: up db down logs migrate

# Запуск админки локально с hot-reload (БД в Docker)
up: db
	uvicorn app.main:app --reload --port 8000

# Только PostgreSQL в Docker
db:
	docker compose up -d db

# Остановить все контейнеры
down:
	docker compose down

# Логи PostgreSQL
logs:
	docker compose logs -f db

# Применить миграции
migrate:
	alembic upgrade head
