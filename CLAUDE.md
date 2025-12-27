# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Описание проекта

Backend для iOS-приложений с механизмом "клоаки" (cloaking) для гемблинг-вертикали.

**Ключевая бизнес-логика:**
- `App.mode == NATIVE` + любой запрос → `200 OK` (для модераторов Apple)
- `App.mode == CASINO` + найден оффер → `400 Bad Request` с URL казино
- `App.mode == CASINO` + оффер не найден → `200 OK` (fallback на native)

**GEO-таргетинг:** Офферы привязаны к регионам. Поиск оффера: точное совпадение `geo.code` → fallback на `geo.is_default=true` → null.

## Команды разработки

```bash
# Разработка (рекомендуется) - БД в Docker, приложение локально с hot-reload
make up                                 # Запускает db + uvicorn --reload на порту 8000

# Только БД
make db                                 # docker compose up -d db

# Продакшен (весь стек в Docker)
docker compose up -d                    # Запуск всего стека (db + admin + adminer)

# Миграции (ТОЛЬКО по запросу пользователя!)
make migrate                            # alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```

**ВАЖНО для агента:** При разработке используется `make up` — приложение запущено ЛОКАЛЬНО (не в Docker).
НЕ запускай контейнер `admin` командой `docker compose up admin` — это только для продакшена!

## Порты

| Режим | Сервис | Порт | URL |
|-------|--------|------|-----|
| Dev | API/Admin | 8000 | http://localhost:8000/admin |
| Dev | PostgreSQL | 5440 | localhost:5440 |
| Dev | Adminer | 8180 | http://localhost:8180 |
| Prod | API/Admin | 8100 | http://localhost:8100/admin |

## Архитектура

```
app/
├── main.py                 # create_app() factory, lifespan, health endpoints
├── admin/panel.py          # Starlette Admin setup
├── api/v1/router.py        # APIRouter prefix="/api/v1"
├── db/database.py          # AsyncEngine + AsyncSession (asyncpg)
└── table/                  # Каждая таблица = папка с model/view/route/service
    ├── app/                # Приложения (bundle_id, mode, настройки)
    ├── offer/              # Офферы казино (name, url, priority)
    ├── geo/                # Регионы (code, is_default)
    ├── group/              # Группы для организации App и Offer
    ├── link/               # Связка App ↔ Offer ↔ Geo (одно гео = один оффер)
    ├── client/             # Устройства пользователей
    │   └── service.py      # InitService + DecisionEngine (основная логика)
    ├── event/              # Аналитические события
    └── init_log/           # Логи запросов /client/init
```

**Паттерн table/:** Каждая сущность имеет свою папку с:
- `model.py` — SQLModel таблица
- `view.py` — Starlette Admin view (icon передавать в конструктор!)
- `route.py` + `service.py` — для endpoint'ов (client, event)
- `schemas.py` — Pydantic схемы запросов/ответов

**Ключевые связи:**
- `App` ↔ `Offer` ↔ `Geo` связаны через `Link` (одно гео = один оффер в приложении)
- `Group` организует `App` и `Offer` (тип: APP или OFFER)

**Ключевые классы:**
- `InitService.process_init()` — точка входа обработки `/client/init`
- `DecisionEngine.decide()` — логика выбора ответа (200/400)
- `InitService.get_offer_for_geo()` — поиск оффера по региону

## API Endpoints

| Метод | Endpoint | Назначение |
|-------|----------|------------|
| POST | `/api/v1/client/init` | Инициализация клиента (200=native, 400=casino) |
| POST | `/api/v1/client/event` | Логирование событий |
| GET | `/health`, `/ready` | Health checks |

## Важные замечания

1. **НЕ создавай миграции автоматически** — только по явному запросу
2. **НЕ деплой на сервер** без подтверждения пользователя
3. Проект использует async PostgreSQL через asyncpg
4. Config загружается из `stack.env` или `.env` через Pydantic Settings
5. В Docker хост БД = `db`, локально автоматически переключается на `127.0.0.1`
