# Mobile Cloaking API

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Backend service for iOS applications with geo-targeted cloaking mechanism. Determines mobile app operating mode at launch and serves configuration based on app settings and user region.

## Architecture

```
                    ┌──────────────────────────┐
                    │     iOS Application       │
                    │   (Swift / SwiftUI)       │
                    └────────────┬─────────────┘
                                 │
                    POST /api/v1/client/init
                    POST /api/v1/client/event
                                 │
                    ┌────────────▼─────────────┐
                    │   Mobile Cloaking API     │
                    │   FastAPI + Gunicorn      │
                    │   ┌───────────────────┐   │
                    │   │  Decision Engine   │   │
                    │   │  (mode + geo)      │   │
                    │   └───────────────────┘   │
                    │   ┌───────────────────┐   │
                    │   │  Admin Panel       │   │
                    │   │  (Starlette Admin) │   │
                    │   └───────────────────┘   │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   PostgreSQL 16 (async)   │
                    │   via asyncpg + SQLModel  │
                    └──────────────────────────┘
```

### Decision Flow

```
POST /api/v1/client/init (device.region = "EE")
        │
        ▼
   App.mode == CASINO ?
        │
   YES ─┤── NO ──▶ 200 { result: null }  (Native mode)
        │
        ▼
   Search Link: app_id + geo="EE"
        │
  FOUND ┤── NOT FOUND
        │        │
        │        ▼
        │   Search fallback: geo.is_default=true
        │        │
        │   FOUND ┤── NOT FOUND ──▶ 200 { result: null }
        │        │
        ▼        ▼
   200 { result: "https://casino-url.com" }  (Casino mode)
```

The client determines mode by checking the `result` field:
- `result: null` -- show native app content (legal game/app)
- `result: "url"` -- open WebView with the provided casino URL

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ with async support |
| **ORM** | SQLModel + SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 16 via asyncpg |
| **Migrations** | Alembic (async) |
| **Admin Panel** | Starlette Admin 0.14+ |
| **Server** | Gunicorn + UvicornWorker |
| **Logging** | Loguru |
| **Settings** | Pydantic Settings v2 |
| **Containerization** | Docker + Docker Compose |

## Quick Start

### Docker Compose (recommended)

```bash
# Clone and configure
git clone <repository-url>
cd mobile-cloaking
cp stack.env.example stack.env    # Edit with your credentials

# Start all services
docker compose up -d

# Verify
curl http://localhost:8100/health
# {"status": "ok"}
```

### Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env              # Edit with your credentials

# Start PostgreSQL in Docker
make db

# Run migrations
make migrate

# Start dev server with hot-reload
make up                           # http://localhost:8000
```

## API Endpoints

### Client API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/client/init` | App initialization -- returns mode config |
| `POST` | `/api/v1/client/event` | Event logging (analytics) |

### Health Checks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/ready` | Readiness probe (Docker/K8s) |

### Dashboard API (internal)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/dashboard/stats` | Dashboard statistics |
| `GET` | `/api/v1/dashboard/apps` | List apps |
| `GET` | `/api/v1/dashboard/offers` | List offers |
| `GET` | `/api/v1/dashboard/geos` | List geo regions |
| `GET` | `/api/v1/dashboard/matrix` | Links matrix |
| `POST` | `/api/v1/dashboard/links` | Create link |
| `DELETE` | `/api/v1/dashboard/links/{id}` | Delete link |
| `POST` | `/api/v1/dashboard/links/{id}/toggle` | Toggle link status |

### Usage Examples

**Initialize client:**

```bash
curl -X POST http://localhost:8100/api/v1/client/init \
  -H "Content-Type: application/json" \
  -H "X-Schema: 1" \
  -d '{
    "schema": 1,
    "app": {"bundle_id": "com.example.app", "version": "1.0"},
    "device": {"language": "en", "timezone": "Europe/Budapest", "region": "HU"},
    "privacy": {"att": "notDetermined"},
    "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"}
  }'
```

**Response (native mode):**

```json
{
  "result": null,
  "prompts": {"rate_delay_sec": 180, "push_delay_sec": 60},
  "update": null
}
```

**Response (casino mode):**

```json
{
  "result": "https://casino-partner.com/?click_id=abc123",
  "prompts": {"rate_delay_sec": 180, "push_delay_sec": 60},
  "update": null
}
```

**Log event:**

```bash
curl -X POST http://localhost:8100/api/v1/client/event \
  -H "Content-Type: application/json" \
  -H "X-Schema: 1" \
  -d '{
    "schema": 1,
    "app": {"bundle_id": "com.example.app", "version": "1.0"},
    "ids": {"internal_id": "550e8400-e29b-41d4-a716-446655440000"},
    "event": {"name": "rate_sheet_shown", "ts": 1734541234, "props": null}
  }'
```

## Project Structure

```
mobile-cloaking/
├── app/
│   ├── main.py                    # FastAPI app factory, lifespan, health checks
│   ├── admin/
│   │   ├── panel.py               # Starlette Admin setup & views registration
│   │   ├── stats.py               # Dashboard statistics & CRUD operations
│   │   ├── auth/provider.py       # Session-based authentication
│   │   └── templates/
│   │       └── dashboard.html     # Interactive Links Dashboard (JS SPA)
│   ├── api/v1/
│   │   ├── router.py              # API v1 router aggregator
│   │   ├── deps.py                # Shared dependencies (DB session, headers)
│   │   └── dashboard.py           # Dashboard REST API routes
│   ├── db/
│   │   ├── database.py            # AsyncEngine, session factory, Database class
│   │   └── base.py                # Model imports for Alembic discovery
│   ├── table/                     # Domain entities (each = folder)
│   │   ├── app/                   # iOS applications (bundle_id, mode, settings)
│   │   │   ├── model.py           # App SQLModel
│   │   │   ├── view.py            # Admin view with delete protection
│   │   │   └── enums.py           # AppMode (native/casino), UpdateMode
│   │   ├── offer/                 # Casino offers (name, URL, priority)
│   │   ├── geo/                   # Geographic regions (ISO codes, fallback)
│   │   ├── group/                 # Organizational groups (APP/OFFER types)
│   │   ├── link/                  # App <-> Offer <-> Geo bindings (unique per app+geo)
│   │   ├── client/                # User devices
│   │   │   ├── model.py           # Client SQLModel
│   │   │   ├── schemas.py         # Init request/response Pydantic models
│   │   │   ├── service.py         # InitService + DecisionEngine (core logic)
│   │   │   ├── route.py           # POST /client/init endpoint
│   │   │   └── view.py            # Admin view (read-only)
│   │   ├── event/                 # Analytics events (rate_us, push prompts)
│   │   └── init_log/              # Raw init request/response logs
│   ├── schemas/
│   │   └── common.py              # Shared enums (ATTStatus)
│   └── utils/
│       └── logger.py              # Loguru configuration
├── migrations/                    # Alembic migrations
├── tests/                         # Pytest async tests
├── config.py                      # Pydantic Settings (env-based config)
├── docker-compose.yml             # PostgreSQL + Adminer + App
├── Dockerfile                     # Python 3.12-slim, non-root user
├── Makefile                       # dev shortcuts (up, db, migrate)
├── requirements.txt               # Pinned dependencies
├── start-up.sh                    # Docker entrypoint (migrate + gunicorn)
└── alembic.ini                    # Alembic configuration
```

## Database Schema

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  groups   │     │   apps   │     │  offers  │
│──────────│     │──────────│     │──────────│
│ id       │◄────│ group_id │     │ group_id │────►│
│ name     │     │ bundle_id│     │ name     │     │
│ type     │     │ mode     │     │ url      │     │
│ (APP/    │     │ apple_id │     │ priority │     │
│  OFFER)  │     │ rate/push│     │ weight   │     │
└──────────┘     └────┬─────┘     └────┬─────┘
                      │                │
                      │   ┌────────┐   │
                      └──►│ links  │◄──┘
                          │────────│
                          │ app_id │
                          │offer_id│
                     ┌───►│ geo_id │
                     │    │priority│  (override)
                     │    │ weight │  (override)
                     │    └────────┘
                     │    UNIQUE(app_id, geo_id)
               ┌─────┴────┐
               │   geos    │
               │──────────│
               │ code (EE) │
               │ name      │
               │ is_default│
               └───────────┘

┌──────────┐     ┌──────────┐     ┌───────────┐
│ clients  │     │  events  │     │ init_logs │
│──────────│     │──────────│     │───────────│
│ internal │     │ client_id│     │ client_id │
│ _id (UUID│     │ app_id   │     │ req/resp  │
│ app_id   │     │ name     │     │ headers   │
│ region   │     │ props    │     │ body      │
│ att_status│    │ event_ts │     │ created_at│
│ sessions │     │received_at│    └───────────┘
└──────────┘     └──────────┘
```

## Configuration

All settings are loaded from environment variables via Pydantic Settings.

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `db` | Database host |
| `POSTGRES_PORT` | `5432` | Database port (internal) |
| `POSTGRES_EXTERNAL_PORT` | `5440` | Database port (mapped for local dev) |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | -- | Database password |
| `POSTGRES_DB` | `cloaking` | Database name |
| `DEBUG` | `false` | Enable debug mode (Swagger UI, verbose logs) |
| `WORKERS` | `4` | Gunicorn worker count |
| `PORT` | `8100` | External port mapping |
| `ADMIN_LOGIN` | -- | Admin panel username |
| `ADMIN_PASSWORD` | -- | Admin panel password |
| `AUTH_SECRET` | -- | Session signing key (32+ chars) |
| `TRUSTED_HOSTS` | `*` | Trusted proxy hosts (comma-separated) |
| `ADMINER_PORT` | `8180` | Adminer UI port |

## Services & Ports

| Service | Dev Port | Prod Port | URL |
|---------|----------|-----------|-----|
| API / Admin | 8000 | 8100 | `/admin`, `/api/v1/*` |
| PostgreSQL | 5440 | 5432 | -- |
| Adminer | 8180 | 8180 | Web UI |
| Swagger (debug) | -- | -- | `/docs` |
| ReDoc (debug) | -- | -- | `/redoc` |

## Migrations

```bash
# Apply all migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "description"
```

## Makefile Commands

```bash
make up       # Start DB + dev server with hot-reload
make db       # Start only PostgreSQL
make down     # Stop all Docker containers
make logs     # Stream PostgreSQL logs
make migrate  # Apply Alembic migrations
```

## Author

**Maksym Babenko**
- GitHub: [@mazamaka](https://github.com/mazamaka)
- Telegram: [@Mazamaka](https://t.me/Mazamaka)

## License

MIT License -- see [LICENSE](LICENSE) file.
