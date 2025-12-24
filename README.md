# Mobile Cloaking API

Backend для iOS-приложений с механизмом cloaking для гемблинг-вертикали.

## Описание

Сервис определяет режим работы мобильного приложения:
- **Native mode (200)** - показываем легальное приложение/игру (для модераторов Apple)
- **Casino mode (400)** - открываем WebView с казино (для реальных пользователей)

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# Копируем конфиг
cp stack.env.example stack.env

# Запускаем
docker compose up -d

# Проверяем
curl http://localhost:8000/health
```

### Локальная разработка

```bash
# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt

# PostgreSQL
docker compose up -d db

# Миграции
alembic upgrade head

# Сервер
uvicorn app.main:app --reload --port 8000
```

## Доступы

| Сервис | URL | Логин / Пароль |
|--------|-----|----------------|
| API Docs | http://localhost:8000/docs | - |
| Admin Panel | http://localhost:8000/admin | admin / admin |
| Adminer (DB) | http://localhost:8080 | postgres / postgres |

## API Endpoints

### POST /api/v1/client/init

Инициализация клиента:
- `200 OK` - native mode
- `400 Bad Request` - casino mode (с полем `result`)

```bash
curl -X POST http://localhost:8000/api/v1/client/init \
  -H "Content-Type: application/json" \
  -H "X-Schema: 1" \
  -d '{
    "schema": 1,
    "app": {"bundle_id": "com.test.app", "version": "1.0"},
    "device": {"language": "en", "timezone": "Europe/Budapest", "region": "HU"},
    "privacy": {"att": "notDetermined"},
    "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"}
  }'
```

### POST /api/v1/client/event

Логирование событий:

```bash
curl -X POST http://localhost:8000/api/v1/client/event \
  -H "Content-Type: application/json" \
  -H "X-Schema: 1" \
  -d '{
    "schema": 1,
    "app": {"bundle_id": "com.test.app", "version": "1.0"},
    "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"},
    "event": {"name": "rate_sheet_shown", "ts": 1734541234, "props": null}
  }'
```

## Структура проекта

```
mobile-cloaking/
├── app/
│   ├── main.py              # FastAPI app
│   ├── admin/               # Starlette Admin
│   ├── api/v1/              # API routes
│   ├── db/                  # Database
│   ├── table/               # Models & Views
│   │   ├── app/             # Apps (bundle_id, mode, casino_url)
│   │   ├── client/          # Clients (devices)
│   │   ├── event/           # Events
│   │   └── init_log/        # Init logs
│   ├── schemas/             # Common schemas
│   └── utils/               # Logger, helpers
├── migrations/              # Alembic
├── config.py                # Settings
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Конфигурация

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cloaking

# App
DEBUG=true
WORKERS=4
PORT=8000

# Admin
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin
AUTH_SECRET=change-me-in-production
```

## Миграции

```bash
# Применить
alembic upgrade head

# Откатить
alembic downgrade -1

# Создать новую
alembic revision --autogenerate -m "description"
```

## Документация

Подробное ТЗ: [CLAUDE.md](./CLAUDE.md)
