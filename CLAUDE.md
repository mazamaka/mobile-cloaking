# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Описание проекта

Backend для iOS-приложений с механизмом "клоаки" (cloaking) для гемблинг-вертикали.

**Ключевая бизнес-логика (всегда 200 OK):**
- `App.mode == NATIVE` → `result: null` (нативный режим)
- `App.mode == CASINO` + найден оффер → `result: "url"` (открыть WebView)
- `App.mode == CASINO` + оффер не найден → `result: null` (fallback на native)

Режим определяется клиентом по наличию поля `result` в ответе.

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
├── ratelimit.py            # SlowAPI limiter (Redis-backed)
├── admin/
│   ├── panel.py            # Starlette Admin setup, TimezoneConfig
│   ├── stats.py            # Dashboard CRUD/stats
│   ├── auth/provider.py    # Session auth (login/password)
│   └── templates/          # base.html, layout.html (dark theme), dashboard.html (SPA)
├── api/v1/
│   ├── router.py           # Агрегатор sub-routers
│   ├── deps.py             # get_db, verify_master_key, verify_master_key_or_session
│   └── dashboard.py        # Dashboard REST API
├── cache/redis.py          # RedisCache singleton
├── db/database.py          # AsyncEngine + AsyncSession (asyncpg)
├── schemas/common.py       # ATTStatus enum
├── utils/
│   ├── helpers.py          # get_enum_value() и общие хелперы
│   ├── logger.py           # Loguru setup
│   └── version.py          # Semver comparison
└── table/                  # Каждая таблица = папка с model/view/route/service
    ├── app/                # Приложения (model, view, route, service, schemas, enums)
    ├── offer/              # Офферы (model, view, route, schemas)
    ├── geo/                # Регионы (model, view, route, schemas)
    ├── group/              # Группы (model, view)
    ├── link/               # Связка App ↔ Offer ↔ Geo (model, view)
    ├── client/             # Устройства (model, view, route, service, schemas)
    │   └── service.py      # InitService + DecisionEngine (основная логика)
    ├── event/              # События (model, view, route, service, schemas)
    └── init_log/           # Логи запросов (model, view)
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
- `DecisionEngine.decide()` — логика выбора ответа (result=url или null)
- `InitService.get_offer_for_geo()` — поиск оффера по региону

## API Endpoints

### Client (без auth)
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| POST | `/api/v1/client/init` | Инициализация клиента (result=null → native, result=url → casino) |
| POST | `/api/v1/client/event` | Логирование событий |

### App Management (X-Master-Key)
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| POST | `/api/v1/app/register` | Регистрация нового приложения |
| GET | `/api/v1/app/list` | Список приложений (фильтры: mode, is_active, group_id) |
| GET | `/api/v1/app/{bundle_id}` | Детали приложения |
| PUT | `/api/v1/app/{bundle_id}` | Обновление приложения |
| PUT | `/api/v1/app/{bundle_id}/mode` | Быстрое переключение mode |
| DELETE | `/api/v1/app/{bundle_id}` | Soft-delete (is_active=false) |
| POST | `/api/v1/app/{bundle_id}/links` | Добавить link (offer+geo) |
| GET | `/api/v1/app/{bundle_id}/test-init?geo=XX` | Dry-run: что вернёт init |
| POST | `/api/v1/app/bulk-mode` | Массовое переключение mode |
| POST | `/api/v1/app/cache/flush` | Сброс Redis кэша |

### Offer Management (X-Master-Key)
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | `/api/v1/offer/list` | Список офферов |
| POST | `/api/v1/offer` | Создание оффера |
| PUT | `/api/v1/offer/{offer_id}` | Обновление оффера |

### Geo Management (X-Master-Key)
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | `/api/v1/geo/list` | Список гео |
| POST | `/api/v1/geo` | Создание гео |

### Dashboard (X-Master-Key)
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | `/api/v1/dashboard/stats` | Общая статистика |
| GET | `/api/v1/dashboard/matrix` | Матрица links |
| GET | `/api/v1/dashboard/events-stats` | Статистика событий |
| GET | `/api/v1/dashboard/push-tokens/export` | Экспорт push-токенов CSV |

### Health
| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe |
| GET | `/health/deep` | Deep check (DB + Redis) |

## Важные замечания

1. **НЕ создавай миграции автоматически** — только по явному запросу
2. **НЕ деплой на сервер** без подтверждения пользователя
3. Проект использует async PostgreSQL через asyncpg
4. Config загружается из `stack.env` или `.env` через Pydantic Settings
5. В Docker хост БД = `db`, локально автоматически переключается на `127.0.0.1`
