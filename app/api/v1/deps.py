from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async for session in db.get_session():
        yield session


@dataclass
class RequestHeaders:
    """Parsed request headers."""

    schema_version: int | None
    bundle_id: str | None
    app_version: str | None


async def get_headers(
    request: Request,
    x_schema: str | None = Header(None, alias="X-Schema"),
    x_app_bundle_id: str | None = Header(None, alias="X-App-Bundle-Id"),
    x_app_version: str | None = Header(None, alias="X-App-Version"),
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
    )
