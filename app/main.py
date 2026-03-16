"""FastAPI application factory and core endpoints."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin.panel import setup_admin
from app.api.v1.router import router as api_v1_router
from app.db.database import db
from app.ratelimit import limiter
from app.utils.logger import logger
from config import SETTINGS

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    logger.info("Starting application...")
    logger.info(f"Debug mode: {SETTINGS.debug}")
    yield
    logger.info("Shutting down application...")
    await db.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Mobile Cloaking API",
        description="""
## Backend for iOS apps with cloaking mechanism

### Business Logic
Service determines operating mode on app launch:
- **Native** (`result: null`) -- show legal app content
- **Casino** (`result: "url"`) -- open WebView with casino URL

### Main Endpoints
| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/client/init` | Client initialization on app launch |
| `POST /api/v1/client/event` | Event logging (Rate Us, Push, etc.) |
| `GET /health` | Service health check |

### Authorization
API requires no auth. Client is identified by `internal_id` (UUID from Keychain).
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "client",
                "description": "Endpoints for mobile client (iOS app)",
            },
            {
                "name": "health",
                "description": "Service health checks",
            },
        ],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # Trust proxy headers (X-Forwarded-Proto, X-Forwarded-For)
    trusted = (
        SETTINGS.trusted_hosts.split(",") if SETTINGS.trusted_hosts != "*" else ["*"]
    )
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=trusted)

    # CORS: allow all origins but no credentials (safe combination)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "X-Schema",
            "X-App-Bundle-Id",
            "X-App-Version",
            "X-API-Key",
            "X-Master-Key",
            "Content-Type",
        ],
    )

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        return FileResponse(STATIC_DIR / "favicon.ico", media_type="image/x-icon")

    @app.get("/", include_in_schema=False)
    async def root_redirect() -> RedirectResponse:
        """Redirect root to admin panel."""
        return RedirectResponse(url="/admin")

    @app.get(
        "/health",
        tags=["health"],
        summary="Health check",
        description="Simple check that the service is running and responding.",
    )
    async def health() -> dict[str, str]:
        """Return 'ok' status if service is alive."""
        return {"status": "ok"}

    @app.get(
        "/ready",
        tags=["health"],
        summary="Readiness probe",
        description="Check service readiness to accept traffic (for Kubernetes/Docker).",
    )
    async def ready() -> dict[str, str]:
        """Return 'ready' status if service can handle requests."""
        return {"status": "ready"}

    @app.get(
        "/health/deep",
        tags=["health"],
        summary="Deep health check",
        description="Checks DB connectivity.",
    )
    async def health_deep() -> dict:
        """Check DB connection and return detailed status."""
        from sqlalchemy import text

        checks: dict[str, str] = {}

        # DB check
        try:
            async for session in db.get_session():
                await session.execute(text("SELECT 1"))
            checks["db"] = "ok"
        except Exception as e:
            checks["db"] = f"error: {e}"

        all_ok = all(v == "ok" for v in checks.values())
        return {"status": "ok" if all_ok else "degraded", "checks": checks}

    app.include_router(api_v1_router)
    setup_admin(app)

    return app


app: FastAPI = create_app()
