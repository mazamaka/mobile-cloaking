# Mobile Cloaking API

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Backend for iOS applications with cloaking mechanism for gambling vertical.

## Description

Service determines mobile application operating mode:
- **Native mode (200)** - show legal application/game (for Apple moderators)
- **Casino mode (400)** - open WebView with casino (for real users)

### GEO Targeting

System automatically selects offer by user region:
1. User comes with `region="EE"` (Estonia)
2. Search for offer for this GEO
3. If not found → use default offer
4. Return casino URL for this region

## Quick Start

### Docker Compose (recommended)

```bash
# Copy config
cp stack.env.example stack.env

# Run
docker compose up -d

# Check health
curl http://localhost:8100/health
```

### Local Development

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# PostgreSQL
docker compose up -d db

# Migrations
alembic upgrade head

# Server
uvicorn app.main:app --reload --port 8000
```

## Default Ports

| Service | Port | Access |
|---------|------|--------|
| API/Admin | 8100 | http://localhost:8100 |
| PostgreSQL | 5440 | localhost:5440 |
| Adminer | 8180 | http://localhost:8180 |

## API Endpoints

### POST /api/v1/client/init

Client initialization:
- `200 OK` - native mode
- `400 Bad Request` - casino mode (with `result` field containing offer URL)

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

### POST /api/v1/client/event

Event logging:

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

## Database

### Tables

| Table | Description |
|-------|-------------|
| `apps` | Applications (bundle_id, mode, settings) |
| `geos` | Regions/countries (ISO codes: EE, HU, PL) |
| `offers` | Casino offers (URL linked to App + Geo) |
| `clients` | User devices |
| `events` | Analytic events |
| `init_logs` | Initialization request logs |

### Offer Selection Flow

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
    │ Search Offer:       │    │ Return 200          │
    │ app_id + geo="EE"   │    │ Native mode         │
    └─────────┬───────────┘    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Found?              │
    └─────────┬───────────┘
              │
     ┌────────┴────────┐
     │ YES             │ NO
     ▼                 ▼
┌──────────┐   ┌─────────────────────┐
│ 400      │   │ Search default      │
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

## Configuration

Environment variables in `stack.env`:

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_EXTERNAL_PORT=5440
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<db_password>
POSTGRES_DB=cloaking

# App
DEBUG=true
WORKERS=4
PORT=8100

# Admin
ADMIN_LOGIN=<admin_username>
ADMIN_PASSWORD=<admin_password>
AUTH_SECRET=<secret_key>

# Ports
ADMINER_PORT=8180
```

## Migrations

```bash
# Apply
alembic upgrade head

# Rollback
alembic downgrade -1

# Create new
alembic revision --autogenerate -m "description"
```

## License

MIT License - see [LICENSE](LICENSE) file.

## Documentation

For detailed specifications, see [CLAUDE.md](./CLAUDE.md).
