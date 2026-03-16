from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db
from config import SETTINGS


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async for session in db.get_session():
        yield session


async def verify_master_key(
    x_master_key: str | None = Header(None, alias="X-Master-Key"),
) -> str:
    """Verify X-Master-Key header against configured master_api_key."""
    if not SETTINGS.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management API disabled (master key not configured)",
        )
    if x_master_key != SETTINGS.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid master key",
        )
    return x_master_key


@dataclass
class RequestHeaders:
    """Parsed request headers."""

    schema_version: int | None
    bundle_id: str | None
    app_version: str | None
    api_key: str | None


async def get_headers(
    request: Request,
    x_schema: str | None = Header(None, alias="X-Schema"),
    x_app_bundle_id: str | None = Header(None, alias="X-App-Bundle-Id"),
    x_app_version: str | None = Header(None, alias="X-App-Version"),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> RequestHeaders:
    """Parse and validate request headers."""
    schema_version = None
    if x_schema:
        try:
            schema_version = int(x_schema)
        except ValueError:
            pass

    return RequestHeaders(
        schema_version=schema_version,
        bundle_id=x_app_bundle_id,
        app_version=x_app_version,
        api_key=x_api_key,
    )
