"""Routes for Geo management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db, verify_master_key
from app.table.geo.model import Geo
from app.table.geo.schemas import (
    GeoCreatedResponse,
    GeoCreateRequest,
    GeoDetailResponse,
    GeoListResponse,
)

router = APIRouter(
    prefix="/geo",
    tags=["geo"],
    dependencies=[Depends(verify_master_key)],
)


def _geo_to_detail(geo: Geo) -> GeoDetailResponse:
    return GeoDetailResponse(
        id=geo.id,  # type: ignore[arg-type]
        code=geo.code,
        name=geo.name,
        is_default=geo.is_default,
        is_active=geo.is_active,
        links_count=len(geo.links) if geo.links else 0,
    )


@router.get(
    "/list",
    summary="List all geos",
    response_model=GeoListResponse,
)
async def list_geos(
    is_active: bool | None = None,
    session: AsyncSession = Depends(get_db),
) -> GeoListResponse:
    """List geos with optional filters."""
    stmt = select(Geo)
    if is_active is not None:
        stmt = stmt.where(Geo.is_active == is_active)
    stmt = stmt.order_by(Geo.code)

    result = await session.execute(stmt)
    geos = result.scalars().all()
    return GeoListResponse(
        items=[_geo_to_detail(g) for g in geos],
        total=len(geos),
    )


@router.post(
    "",
    summary="Create a new geo",
    response_model=GeoCreatedResponse,
    status_code=201,
    responses={409: {"description": "Geo with this code already exists"}},
)
async def create_geo(
    body: GeoCreateRequest,
    session: AsyncSession = Depends(get_db),
) -> GeoCreatedResponse:
    """Create a new geo."""
    stmt = select(Geo).where(Geo.code == body.code)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Geo '{body.code}' already exists",
        )

    geo = Geo(code=body.code, name=body.name, is_default=body.is_default)
    session.add(geo)
    await session.commit()

    return GeoCreatedResponse(
        geo_id=geo.id,  # type: ignore[arg-type]
        code=geo.code,
        name=geo.name,
    )
