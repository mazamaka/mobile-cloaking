# Mobile Cloaking API - Инструкции для Claude Code

## Описание проекта

Backend для iOS-приложений с механизмом "клоаки" (cloaking) для гемблинг-вертикали.

**Бизнес-логика:**
- При проверке модератором Apple → возвращаем 200 (легальное приложение/игра)
- При заходе реального пользователя → возвращаем 400 с URL казино (открывается WebView)

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
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── provider.py            # CustomAuthProvider
│   │   │   └── deps.py                # require_auth_user
│   │   ├── middleware.py              # CORS, Session middleware
│   │   ├── events.py                  # startup/shutdown hooks
│   │   ├── routes.py                  # Кастомные API роуты
│   │   ├── views/
│   │   │   ├── __init__.py
│   │   │   └── base.py                # BaseModelView
│   │   ├── templates/
│   │   │   └── dashboard.html
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   │
│   ├── api/                           # Публичные API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # APIRouter prefix="/api/v1"
│   │   │   └── deps.py                # get_db, get_headers
│   │   └── health.py                  # /health, /ready
│   │
│   ├── table/                         # Каждая таблица = папка
│   │   ├── __init__.py
│   │   │
│   │   ├── app/                       # Приложения (bundle_id)
│   │   │   ├── __init__.py
│   │   │   ├── model.py               # App SQLModel
│   │   │   ├── view.py                # AppView для админки
│   │   │   ├── schemas.py             # Pydantic schemas
│   │   │   └── enums.py               # AppMode, UpdateMode
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

## API Endpoints

### 1. POST /api/v1/client/init

**Назначение:** "Фейс-контроль" при запуске приложения. Определяет режим работы.

#### Headers:
| Header | Тип | Required | Описание |
|--------|-----|----------|----------|
| `Content-Type` | string | Yes | `application/json` |
| `X-Schema` | int/string | Yes | Версия схемы (`1`) |
| `X-App-Bundle-Id` | string | No | Bundle ID (fallback на body) |
| `X-App-Version` | string | No | Версия (fallback на body) |

#### Request Body (Schema v1):

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
    "internal_id": "0D0FC887-C577-41EA-8C2D-D91E979AD357",
    "idfa": "AEBE52E7-03EE-455A-B3C4-E57283966239"
  },
  "attribution": {
    "appsflyer_id": "1765992827433-2791097"
  },
  "push": {
    "token": "abcd1234..."
  }
}
```

#### Валидация полей:

| Блок | Поле | Required | Тип | Описание |
|------|------|----------|-----|----------|
| root | `schema` | Yes | int | Ожидаем `1` |
| `app` | `bundle_id` | Yes | string | non-empty |
| `app` | `version` | Yes | string | non-empty |
| `device` | `language` | Yes | string | "en-EE", "en-US" |
| `device` | `timezone` | Yes | string | "Europe/Budapest" |
| `device` | `region` | Yes | string | "EE", "HU" |
| `privacy` | `att` | Yes | enum | см. ATTStatus |
| `ids` | `internal_id` | Yes | string | UUID v4 (Keychain) |
| `ids` | `idfa` | No | string/null | Только при `att=authorized` |
| `attribution` | `appsflyer_id` | No | string | AppsFlyer ID |
| `push` | `token` | No | string | Push-токен |

**ATTStatus Enum:**
- `authorized` - разрешён трекинг
- `denied` - запрещён
- `notDetermined` - не определён
- `restricted` - ограничен
- `legacy` - iOS < 14
- `unavailable` - tracking disabled

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
    "appstore_url": "itms-apps://itunes.apple.com/app/id123456789"
  }
}
```

#### Response 400 Bad Request (режим казино):

```json
{
  "result": "https://casino-link.com/?param=value",
  "prompts": {
    "rate_delay_sec": 180,
    "push_delay_sec": 60
  },
  "update": {
    "min_version": "1.0",
    "latest_version": "1.2",
    "mode": "soft",
    "appstore_url": "itms-apps://itunes.apple.com/app/id123456789"
  }
}
```

> **ВАЖНО:** Поле `result` ОБЯЗАТЕЛЬНО при 400 ответе!

---

### 2. POST /api/v1/client/event

**Назначение:** Логирование пользовательских событий (Rate Us, Push и др.)

#### Headers:
| Header | Тип | Описание |
|--------|-----|----------|
| `Content-Type` | string | `application/json` |
| `X-Schema` | int/string | `1` |
| `X-App-Bundle-Id` | string | Bundle ID |
| `X-App-Version` | string | Версия |

#### Request Body:

```json
{
  "schema": 1,
  "app": {
    "bundle_id": "com.company.app",
    "version": "1.0"
  },
  "ids": {
    "internal_id": "0D0FC887-C577-41EA-8C2D-D91E979AD357"
  },
  "event": {
    "name": "rate_sheet_shown",
    "ts": 1734541234,
    "props": null
  }
}
```

#### Валидация:

| Блок | Поле | Required | Тип |
|------|------|----------|-----|
| root | `schema` | Yes | int (1) |
| `app` | `bundle_id` | Yes | string |
| `app` | `version` | Yes | string |
| `ids` | `internal_id` | Yes | string |
| `event` | `name` | Yes | string |
| `event` | `ts` | Yes | int (Unix timestamp) |
| `event` | `props` | No | object/null |

#### Типы событий (v1):

| Event Name | Описание |
|------------|----------|
| `rate_sheet_shown` | Показан Rate Us popup |
| `rate_slider_completed` | Пользователь оценил |
| `rate_sheet_closed` | Закрыл popup |
| `push_prompt_shown` | Показан Push popup |
| `push_prompt_accepted` | Принял push |
| `push_prompt_declined` | Отказал push |

#### Response:

```
HTTP 200 OK
Body: {} (пустой объект)
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
    casino_url: str | None = None                     # URL казино

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

    # Relationships
    clients: list["Client"] = Relationship(back_populates="app")
    events: list["Event"] = Relationship(back_populates="app")
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

### Table: clients

```python
class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: int | None = Field(default=None, primary_key=True)
    internal_id: str = Field(unique=True, index=True)  # UUID из Keychain

    # Связь с приложением
    app_id: int = Field(foreign_key="apps.id")
    app: App = Relationship(back_populates="clients")

    # Версия приложения
    app_version: str

    # Device info
    language: str
    timezone: str
    region: str

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

    # Relationships
    events: list["Event"] = Relationship(back_populates="client")
```

### Table: events

```python
class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)

    # Связи
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Client = Relationship(back_populates="events")

    app_id: int = Field(foreign_key="apps.id", index=True)
    app: App = Relationship(back_populates="events")

    # Event data
    name: str = Field(index=True)                      # rate_sheet_shown
    event_ts: datetime                                  # Время на устройстве
    props: dict | None = Field(default=None, sa_type=JSONB)

    # App context
    app_version: str

    # Server time
    received_at: datetime = Field(default_factory=datetime.utcnow)
```

### Table: init_logs (опционально)

```python
class InitLog(SQLModel, table=True):
    __tablename__ = "init_logs"

    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="clients.id")

    # Request data
    request_headers: dict = Field(sa_type=JSONB)
    request_body: dict = Field(sa_type=JSONB)

    # Response
    response_code: int                                  # 200 / 400
    response_body: dict = Field(sa_type=JSONB)

    created_at: datetime
```

---

## Бизнес-логика

### Decision Engine (Логика принятия решений)

MVP версия - простой переключатель в админке:

```python
class DecisionEngine:
    async def decide(self, app: App, client_data: InitRequest) -> tuple[int, BaseModel]:
        """
        Возвращает (status_code, response_body)
        """
        if app.mode == AppMode.CASINO and app.casino_url:
            return 400, InitResponseCasino(
                result=app.casino_url,
                prompts=self._build_prompts(app),
                update=self._build_update(app),
            )
        else:
            return 200, InitResponseNative(
                prompts=self._build_prompts(app),
                update=self._build_update(app),
            )

    def _build_prompts(self, app: App) -> PromptsConfig:
        return PromptsConfig(
            rate_delay_sec=app.rate_delay_sec,
            push_delay_sec=app.push_delay_sec,
        )

    def _build_update(self, app: App) -> UpdateConfig | None:
        if not any([app.min_version, app.latest_version]):
            return None
        return UpdateConfig(
            min_version=app.min_version,
            latest_version=app.latest_version,
            mode=app.update_mode.value if app.update_mode else None,
            appstore_url=app.appstore_url,
        )
```

### Tolerant Reader (Устойчивость к ошибкам)

1. **Не падать** при отсутствии optional полей
2. **Не падать** при `props = null`
3. **Игнорировать** неизвестные поля (forward compatibility)
4. **Fallback** на headers → body для `bundle_id`, `version`
5. **Принимать** `X-Schema` как string или int

---

## Админ-панель

### Функционал:

**Apps (Приложения):**
- CRUD для приложений
- Переключение режима (native/casino)
- Настройка casino_url
- Настройки prompts и update policy
- Статистика по приложению (кол-во клиентов, событий)

**Clients (Устройства):**
- Просмотр всех клиентов
- Фильтрация по app, region, att_status
- Детали устройства
- История событий клиента

**Events (События):**
- Лог всех событий
- Фильтрация по типу, дате, клиенту
- Агрегация статистики

**Dashboard:**
- Общее количество клиентов
- Активные сегодня
- События по типам
- График активности

### Авторизация:

Простая авторизация через login/password (как в 1-google-admin):
- `ADMIN_LOGIN` и `ADMIN_PASSWORD` в env
- Session-based auth
- CustomAuthProvider для Starlette Admin

---

## Конфигурация

### config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

def _is_docker() -> bool:
    return Path("/.dockerenv").exists()

IS_DOCKER = _is_docker()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # Database
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "cloaking"

    # App
    debug: bool = False
    workers: int = 4
    port: int = 8000

    # Admin
    admin_login: str = "admin"
    admin_password: str = "admin"
    auth_secret: str = "change-me-in-production"

    # Defaults
    default_rate_delay_sec: int = 180
    default_push_delay_sec: int = 60

    @property
    def effective_host(self) -> str:
        return self.postgres_host if IS_DOCKER else "127.0.0.1"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.effective_host}:{self.postgres_port}/{self.postgres_db}"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

SETTINGS = get_settings()
```

### stack.env.example

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=cloaking

# App
DEBUG=false
WORKERS=4
PORT=8000

# Admin
ADMIN_LOGIN=admin
ADMIN_PASSWORD=your-admin-password
AUTH_SECRET=your-secret-key-change-in-production

# Ports (for docker-compose)
ADMINER_PORT=8080
```

---

## Docker

### docker-compose.yml

```yaml
version: "3.8"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-cloaking}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  adminer:
    image: adminer:latest
    ports:
      - "${ADMINER_PORT:-8080}:8080"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  api:
    build: .
    env_file: stack.env
    ports:
      - "${PORT:-8000}:8000"
    depends_on:
      db:
        condition: service_healthy
    entrypoint: ["/app/start-up.sh"]
    restart: unless-stopped

volumes:
  pgdata:

networks:
  default:
    name: cloaking-net
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Make scripts executable
RUN chmod +x /app/start-up.sh

# Create non-root user
RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/start-up.sh"]
```

### start-up.sh

```bash
#!/bin/bash
set -e

# Run migrations
alembic upgrade head

# Start server
exec gunicorn app.main:app \
    --bind 0.0.0.0:8000 \
    --workers ${WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --access-logfile - \
    --error-logfile -
```

---

## Тестовые примеры

### INIT 200 (минимальный):

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

### INIT 400 (казино):

```bash
# Ответ когда app.mode = "casino"
{
  "result": "https://casino.example.com/game",
  "prompts": {"rate_delay_sec": 180, "push_delay_sec": 60}
}
```

### EVENT:

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

---

## Этапы реализации

### Этап 1 - Базовая инфраструктура:
- [ ] Структура проекта (папки, __init__.py)
- [ ] config.py с Pydantic Settings
- [ ] Docker Compose + Dockerfile + start-up.sh
- [ ] requirements.txt
- [ ] Database setup (db/database.py)
- [ ] Alembic init

### Этап 2 - Модели и миграции:
- [ ] table/app/model.py + enums.py
- [ ] table/client/model.py
- [ ] table/event/model.py + enums.py
- [ ] table/init_log/model.py
- [ ] db/base.py (import all models)
- [ ] Создать первую миграцию

### Этап 3 - API endpoints:
- [ ] api/v1/deps.py (get_db, get_headers)
- [ ] api/v1/router.py
- [ ] table/client/schemas.py
- [ ] table/client/route.py (POST /init)
- [ ] table/client/service.py (InitService)
- [ ] table/event/schemas.py
- [ ] table/event/route.py (POST /event)
- [ ] table/event/service.py (EventService)
- [ ] api/health.py

### Этап 4 - Админка:
- [ ] admin/auth/provider.py
- [ ] admin/panel.py
- [ ] admin/middleware.py
- [ ] admin/events.py
- [ ] table/app/view.py
- [ ] table/client/view.py
- [ ] table/event/view.py
- [ ] admin/templates/dashboard.html

### Этап 5 - Финализация:
- [ ] Тестирование endpoints
- [ ] Проверка Docker build
- [ ] README.md обновление

---

## Важные замечания

1. **НЕ создавай миграции автоматически** - только по запросу пользователя
2. **НЕ деплой на сервер** без явного подтверждения
3. Используй паттерны из проекта 1-google-admin (`/Users/admin/PycharmProjects/1-google-admin/`)
4. Для актуальных примеров библиотек смотри в `/Users/admin/PycharmProjects/DOCS/`
5. Используй MCP context7 для получения актуальной документации

---

## Ссылки на референсы

- Проект-пример: `/Users/admin/PycharmProjects/1-google-admin/`
- Документация библиотек: `/Users/admin/PycharmProjects/DOCS/`
