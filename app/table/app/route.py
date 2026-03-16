"""Routes for App management."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db, verify_master_key
from app.ratelimit import limiter
from app.table.app.schemas import (
    AppAddLinkRequest,
    AppAddLinkResponse,
    AppBulkModeRequest,
    AppBulkModeResponse,
    AppDetailResponse,
    AppListResponse,
    AppModeRequest,
    AppModeResponse,
    AppRegisterRequest,
    AppRegisterResponse,
    AppUpdateRequest,
    MessageResponse,
    TestInitResponse,
)
from app.table.app.service import AppService

router = APIRouter(prefix="/app", tags=["app"])


# --- Registration (rate-limited) ---


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
    status_code=201,
    dependencies=[Depends(verify_master_key)],
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
    session: AsyncSession = Depends(get_db),
) -> AppRegisterResponse:
    """Register a new app with optional offer-geo bindings."""
    service = AppService(session)
    return await service.register(body)


# --- List ---


@router.get(
    "/list",
    summary="List all apps",
    response_model=AppListResponse,
    dependencies=[Depends(verify_master_key)],
)
async def list_apps(
    mode: str | None = None,
    is_active: bool | None = None,
    group_id: int | None = None,
    session: AsyncSession = Depends(get_db),
) -> AppListResponse:
    """List apps with optional filters."""
    service = AppService(session)
    return await service.list_apps(mode=mode, is_active=is_active, group_id=group_id)


# --- Bulk mode ---


@router.post(
    "/bulk-mode",
    summary="Mass mode switch",
    response_model=AppBulkModeResponse,
    dependencies=[Depends(verify_master_key)],
)
async def bulk_mode(
    body: AppBulkModeRequest,
    session: AsyncSession = Depends(get_db),
) -> AppBulkModeResponse:
    """Switch mode for multiple apps at once."""
    service = AppService(session)
    return await service.bulk_mode(body)


# --- Detail ---


@router.get(
    "/{bundle_id}",
    summary="Get app details",
    response_model=AppDetailResponse,
    dependencies=[Depends(verify_master_key)],
    responses={404: {"description": "App not found"}},
)
async def get_app(
    bundle_id: str,
    session: AsyncSession = Depends(get_db),
) -> AppDetailResponse:
    """Get full app details by bundle_id."""
    service = AppService(session)
    return await service.get_detail(bundle_id)


# --- Update ---


@router.put(
    "/{bundle_id}",
    summary="Update app",
    response_model=AppDetailResponse,
    dependencies=[Depends(verify_master_key)],
    responses={404: {"description": "App not found"}},
)
async def update_app(
    bundle_id: str,
    body: AppUpdateRequest,
    session: AsyncSession = Depends(get_db),
) -> AppDetailResponse:
    """Update app fields."""
    service = AppService(session)
    return await service.update(bundle_id, body)


# --- Mode switch ---


@router.put(
    "/{bundle_id}/mode",
    summary="Quick mode switch",
    response_model=AppModeResponse,
    dependencies=[Depends(verify_master_key)],
    responses={404: {"description": "App not found"}},
)
async def switch_mode(
    bundle_id: str,
    body: AppModeRequest,
    session: AsyncSession = Depends(get_db),
) -> AppModeResponse:
    """Switch app mode (native/casino). Use for emergency toggling."""
    service = AppService(session)
    return await service.switch_mode(bundle_id, body)


# --- Soft delete ---


@router.delete(
    "/{bundle_id}",
    summary="Deactivate app",
    response_model=MessageResponse,
    dependencies=[Depends(verify_master_key)],
    responses={404: {"description": "App not found"}},
)
async def delete_app(
    bundle_id: str,
    session: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Soft-delete: sets is_active=false."""
    service = AppService(session)
    return await service.soft_delete(bundle_id)


# --- Add link ---


@router.post(
    "/{bundle_id}/links",
    summary="Add link to app",
    response_model=AppAddLinkResponse,
    status_code=201,
    dependencies=[Depends(verify_master_key)],
    responses={
        404: {"description": "App, offer, or geo not found"},
        409: {"description": "Link for this geo already exists"},
    },
)
async def add_link(
    bundle_id: str,
    body: AppAddLinkRequest,
    session: AsyncSession = Depends(get_db),
) -> AppAddLinkResponse:
    """Add offer+geo link to an existing app."""
    service = AppService(session)
    return await service.add_link(bundle_id, body)


# --- Test init (dry run) ---


@router.get(
    "/{bundle_id}/test-init",
    summary="Test init (dry run)",
    response_model=TestInitResponse,
    dependencies=[Depends(verify_master_key)],
    responses={404: {"description": "App not found"}},
)
async def test_init(
    bundle_id: str,
    geo: str = "US",
    session: AsyncSession = Depends(get_db),
) -> TestInitResponse:
    """Dry-run: shows what /client/init would return for this app+geo."""
    service = AppService(session)
    return await service.test_init(bundle_id, geo)
