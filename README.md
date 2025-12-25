# Mobile Cloaking API

Backend для iOS-приложений с механизмом cloaking для гемблинг-вертикали.

## Описание

Сервис определяет режим работы мобильного приложения:
- **Native mode (200)** - показываем легальное приложение/игру (для модераторов Apple)
- **Casino mode (400)** - открываем WebView с казино (для реальных пользователей)

### GEO-таргетинг

Система автоматически подбирает оффер по региону пользователя:
1. Юзер приходит с `region="EE"` (Эстония)
2. Ищем оффер для этого GEO
3. Если не найден → используем default оффер
4. Возвращаем URL казино для этого региона

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# Копируем конфиг
cp stack.env.example stack.env

# Запускаем
docker compose up -d

# Проверяем
curl http://localhost:8100/health
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
| API Docs | http://localhost:8100/docs | - |
| Admin Panel | http://localhost:8100/admin | mazamaka / Zxcvbn321 |
| Adminer (DB) | http://localhost:8180 | postgres / postgres |

## API Endpoints

### POST /api/v1/client/init

Инициализация клиента:
- `200 OK` - native mode
- `400 Bad Request` - casino mode (с полем `result` содержащим URL оффера)

```bash
curl -X POST http://localhost:8100/api/v1/client/init \
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
curl -X POST http://localhost:8100/api/v1/client/event \
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
│   │   ├── app/             # Apps (bundle_id, mode)
│   │   ├── geo/             # GEO regions (EE, HU, PL)
│   │   ├── offer/           # Offers (casino URLs per GEO)
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

## База данных

### Основные таблицы

| Таблица | Описание |
|---------|----------|
| `apps` | Приложения (bundle_id, mode, настройки) |
| `geos` | Регионы/страны (ISO коды: EE, HU, PL) |
| `offers` | Офферы казино (URL привязан к App + Geo) |
| `clients` | Устройства пользователей |
| `events` | Аналитические события |
| `init_logs` | Логи инициализаций |

### Логика выбора оффера

```
App (mode=casino) + Client (region=EE)
         ↓
   Поиск Offer где:
   - app_id = App.id
   - geo.code = "EE"
   - is_active = true
         ↓
   Найден? → 400 + offer.url
   Не найден? → Fallback на geo.is_default=true
   Нет default? → 200 (native mode)
```

## Конфигурация

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
ADMIN_LOGIN=admin
ADMIN_PASSWORD=admin
AUTH_SECRET=change-me-in-production

# Ports (for docker-compose)
ADMINER_PORT=8180
```

## Порты (по умолчанию)

| Сервис | Порт |
|--------|------|
| API/Admin | 8100 |
| PostgreSQL | 5440 |
| Adminer | 8180 |

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
