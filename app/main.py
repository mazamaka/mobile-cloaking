from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin.panel import setup_admin
from app.api.v1.router import router as api_v1_router
from app.db.database import db
from app.utils.logger import logger
from config import SETTINGS


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    logger.info(f"Debug mode: {SETTINGS.debug}")
    yield
    logger.info("Shutting down application...")
    await db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Mobile Cloaking API",
        description="""
## 🎰 Backend для iOS-приложений с механизмом клоаки

### Бизнес-логика
Сервис определяет тип пользователя при запуске приложения:
- **Модератор Apple** → возвращаем `200 OK` (показываем легальное приложение/игру)
- **Реальный пользователь** → возвращаем `400 Bad Request` с URL казино (открывается WebView)

### Основные эндпоинты
| Эндпоинт | Описание |
|----------|----------|
| `POST /api/v1/client/init` | Инициализация клиента при запуске приложения |
| `POST /api/v1/client/event` | Логирование событий (Rate Us, Push и др.) |
| `GET /health` | Проверка здоровья сервиса |

### Режимы работы приложения
- **Native** (`200 OK`) — показываем нативное приложение/игру
- **Casino** (`400 Bad Request`) — открываем WebView с URL казино

### Авторизация
API не требует авторизации. Клиент идентифицируется по `internal_id` (UUID из Keychain).
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "client",
                "description": "Эндпоинты для мобильного клиента (iOS приложение)",
            },
            {
                "name": "health",
                "description": "Проверка состояния сервиса",
            },
        ],
    )

    # Trust proxy headers (X-Forwarded-Proto, X-Forwarded-For)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Redirect root to admin
    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/admin")

    # Health check endpoints
    @app.get(
        "/health",
        tags=["health"],
        summary="Проверка здоровья",
        description="Простая проверка что сервис запущен и отвечает на запросы.",
    )
    async def health() -> dict[str, str]:
        """Возвращает статус 'ok' если сервис работает."""
        return {"status": "ok"}

    @app.get(
        "/ready",
        tags=["health"],
        summary="Готовность к работе",
        description="Проверка готовности сервиса принимать трафик (для Kubernetes/Docker).",
    )
    async def ready() -> dict[str, str]:
        """Возвращает статус 'ready' если сервис готов обрабатывать запросы."""
        return {"status": "ready"}

    # API v1 routes
    app.include_router(api_v1_router)

    # Admin panel
    setup_admin(app)

    return app


app = create_app()
