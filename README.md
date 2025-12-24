# Mobile Cloaking API

Backend для iOS-приложений с механизмом cloaking для гемблинг-вертикали.

## Описание

Сервис определяет режим работы мобильного приложения:
- **Native mode (200)** - показываем легальное приложение/игру (для модераторов Apple)
- **Casino mode (400)** - открываем WebView с казино (для реальных пользователей)

## Стек

- FastAPI + Uvicorn
- PostgreSQL 16
- SQLModel + SQLAlchemy (async)
- Starlette Admin
- Docker Compose

## Быстрый старт

```bash
# Клонировать репозиторий
git clone git@github.com:your-org/mobile-cloaking.git
cd mobile-cloaking

# Скопировать env файл
cp stack.env.example stack.env

# Отредактировать stack.env (пароли, секреты)
nano stack.env

# Запустить
docker-compose up -d
```

## Endpoints

| Method | Path | Описание |
|--------|------|----------|
| POST | `/api/v1/client/init` | Инициализация клиента |
| POST | `/api/v1/client/event` | Логирование событий |
| GET | `/health` | Health check |
| GET | `/admin` | Админ-панель |

## Документация

Подробное ТЗ и инструкции для разработки находятся в файле [CLAUDE.md](./CLAUDE.md).

## Структура проекта

```
mobile-cloaking/
├── app/
│   ├── admin/          # Starlette Admin
│   ├── api/            # API endpoints
│   ├── table/          # Models, Views, Schemas, Routes
│   ├── db/             # Database
│   └── utils/          # Utilities
├── migrations/         # Alembic
├── config.py
├── docker-compose.yml
└── Dockerfile
```

## Лицензия

Private
