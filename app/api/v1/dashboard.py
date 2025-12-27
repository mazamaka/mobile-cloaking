"""Dashboard API routes."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.stats import (
    create_app,
    create_app_offer_geo_link,
    create_geo,
    create_offer,
    delete_app_offer_geo_link,
    get_app_offer_geo_matrix,
    get_apps_list,
    get_dashboard_stats,
    get_geos_list,
    get_groups_list,
    get_offers_list,
    toggle_app_offer_geo_link,
)
from app.db.database import get_db
from app.table.group.model import GroupType

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class CreateLinkRequest(BaseModel):
    app_id: int
    offer_id: int
    geo_id: int
    priority: int | None = None
    weight: int | None = None


class CreateAppRequest(BaseModel):
    bundle_id: str
    name: str | None = None
    apple_id: str | None = None
    mode: str = "native"
    group_id: int | None = None


class CreateOfferRequest(BaseModel):
    name: str
    url: str
    priority: int = 0
    weight: int = 100
    group_id: int | None = None


class CreateGeoRequest(BaseModel):
    code: str
    name: str
    is_default: bool = False


@router.get("/stats")
async def get_stats(session: AsyncSession = Depends(get_db)):
    """Get dashboard statistics."""
    return await get_dashboard_stats(session)


@router.get("/apps")
async def get_apps(session: AsyncSession = Depends(get_db)):
    """Get all apps for dropdown."""
    return await get_apps_list(session)


@router.get("/offers")
async def get_offers(session: AsyncSession = Depends(get_db)):
    """Get all offers for dropdown."""
    return await get_offers_list(session)


@router.get("/geos")
async def get_geos(session: AsyncSession = Depends(get_db)):
    """Get all geos for dropdown."""
    return await get_geos_list(session)


@router.get("/matrix")
async def get_matrix(session: AsyncSession = Depends(get_db)):
    """Get App-Offer-Geo matrix."""
    return await get_app_offer_geo_matrix(session)


@router.post("/links")
async def create_link(
    request: CreateLinkRequest,
    session: AsyncSession = Depends(get_db),
):
    """Create a new App-Offer-Geo link."""
    try:
        result = await create_app_offer_geo_link(
            session,
            app_id=request.app_id,
            offer_id=request.offer_id,
            geo_id=request.geo_id,
            priority=request.priority,
            weight=request.weight,
        )
        await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        error_msg = str(e)
        if "uq_app_offer_geo_app_geo" in error_msg:
            return {"success": False, "error": "This Geo is already assigned in this App"}
        return {"success": False, "error": str(e)}


@router.delete("/links/{link_id}")
async def delete_link(
    link_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Delete an App-Offer-Geo link."""
    result = await delete_app_offer_geo_link(session, link_id)
    await session.commit()
    return result


@router.post("/links/{link_id}/toggle")
async def toggle_link(
    link_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Toggle is_active status of a link."""
    result = await toggle_app_offer_geo_link(session, link_id)
    await session.commit()
    return result


@router.get("/groups")
async def get_groups(
    type: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """Get groups for dropdown."""
    group_type = GroupType(type) if type else None
    return await get_groups_list(session, group_type)


@router.post("/apps")
async def create_new_app(
    request: CreateAppRequest,
    session: AsyncSession = Depends(get_db),
):
    """Create a new App."""
    try:
        result = await create_app(
            session,
            bundle_id=request.bundle_id,
            name=request.name,
            apple_id=request.apple_id,
            mode=request.mode,
            group_id=request.group_id,
        )
        if result.get("success"):
            await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": str(e)}


@router.post("/offers")
async def create_new_offer(
    request: CreateOfferRequest,
    session: AsyncSession = Depends(get_db),
):
    """Create a new Offer."""
    try:
        result = await create_offer(
            session,
            name=request.name,
            url=request.url,
            priority=request.priority,
            weight=request.weight,
            group_id=request.group_id,
        )
        if result.get("success"):
            await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": str(e)}


@router.post("/geos")
async def create_new_geo(
    request: CreateGeoRequest,
    session: AsyncSession = Depends(get_db),
):
    """Create a new Geo."""
    try:
        result = await create_geo(
            session,
            code=request.code,
            name=request.name,
            is_default=request.is_default,
        )
        if result.get("success"):
            await session.commit()
        return result
    except Exception as e:
        await session.rollback()
        return {"success": False, "error": str(e)}
