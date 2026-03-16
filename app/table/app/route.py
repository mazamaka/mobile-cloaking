"""Routes for App registration."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db
from app.ratelimit import limiter
from app.table.app.schemas import AppRegisterRequest, AppRegisterResponse
from app.table.app.service import AppRegistrationService
from config import SETTINGS

router = APIRouter(prefix="/app", tags=["app"])


async def verify_master_key(
    x_master_key: str | None = Header(None, alias="X-Master-Key"),
) -> str:
    """Verify X-Master-Key header against configured master_api_key.

    Raises:
        HTTPException: 403 if registration is disabled (no master key configured).
        HTTPException: 401 if the provided key is invalid.
    """
    if not SETTINGS.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration disabled",
        )
    if x_master_key != SETTINGS.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid master key",
        )
    return x_master_key


@router.post(
    "/register",
    summary="Register a new app",
    description="""
## Register a new iOS application

Creates an App record and optionally binds offers to geos (for casino mode).

### Authentication
Requires `X-Master-Key` header matching the server's `MASTER_API_KEY` env var.

### Offers binding
When `mode=casino` and `offers` list is provided, the service will create
Link records binding the app to existing offers and geos.
If an offer or geo is not found, it will be skipped with a warning.
    """,
    response_model=AppRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Invalid master key"},
        403: {"description": "Registration disabled (master key not configured)"},
        409: {"description": "App with this bundle_id already exists"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("10/minute")
async def register_app(
    request: Request,
    body: AppRegisterRequest,
    _master_key: str = Depends(verify_master_key),
    session: AsyncSession = Depends(get_db),
) -> AppRegisterResponse:
    """Register a new app with optional offer-geo bindings."""
    service = AppRegistrationService(session)
    return await service.register(body)
