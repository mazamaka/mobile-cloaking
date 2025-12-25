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
        description="Backend for iOS apps with cloaking mechanism",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if SETTINGS.debug else None,
        redoc_url="/redoc" if SETTINGS.debug else None,
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
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}

    # API v1 routes
    app.include_router(api_v1_router)

    # Admin panel
    setup_admin(app)

    return app


app = create_app()
