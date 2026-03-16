"""Routes for Offer management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db, verify_master_key
from app.table.group.model import Group, GroupType
from app.table.offer.model import Offer
from app.table.offer.schemas import (
    OfferCreatedResponse,
    OfferDetailResponse,
    OfferListResponse,
    OfferUpdateRequest,
    OfferCreateRequest,
)

router = APIRouter(
    prefix="/offer",
    tags=["offer"],
    dependencies=[Depends(verify_master_key)],
)


def _offer_to_detail(offer: Offer) -> OfferDetailResponse:
    return OfferDetailResponse(
        id=offer.id,  # type: ignore[arg-type]
        name=offer.name,
        url=offer.url,
        priority=offer.priority,
        weight=offer.weight,
        group_id=offer.group_id,
        is_active=offer.is_active,
        links_count=len(offer.links) if offer.links else 0,
    )


@router.get(
    "/list",
    summary="List all offers",
    response_model=OfferListResponse,
)
async def list_offers(
    is_active: bool | None = None,
    group_id: int | None = None,
    session: AsyncSession = Depends(get_db),
) -> OfferListResponse:
    """List offers with optional filters."""
    stmt = select(Offer)
    if is_active is not None:
        stmt = stmt.where(Offer.is_active == is_active)
    if group_id is not None:
        stmt = stmt.where(Offer.group_id == group_id)
    stmt = stmt.order_by(Offer.id.desc())

    result = await session.execute(stmt)
    offers = result.scalars().all()
    return OfferListResponse(
        items=[_offer_to_detail(o) for o in offers],
        total=len(offers),
    )


@router.post(
    "",
    summary="Create a new offer",
    response_model=OfferCreatedResponse,
    status_code=201,
    responses={409: {"description": "Offer with this name already exists"}},
)
async def create_offer(
    body: OfferCreateRequest,
    session: AsyncSession = Depends(get_db),
) -> OfferCreatedResponse:
    """Create a new offer."""
    warnings: list[str] = []

    # Check duplicate
    stmt = select(Offer).where(Offer.name == body.name)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Offer '{body.name}' already exists",
        )

    group_id: int | None = None
    if body.group_name:
        stmt = select(Group).where(
            Group.name == body.group_name, Group.type == GroupType.OFFER
        )
        result = await session.execute(stmt)
        group = result.scalar_one_or_none()
        if group:
            group_id = group.id
        else:
            warnings.append(f"Group '{body.group_name}' not found")

    offer = Offer(
        name=body.name,
        url=body.url,
        priority=body.priority,
        weight=body.weight,
        group_id=group_id,
    )
    session.add(offer)
    await session.commit()

    return OfferCreatedResponse(
        offer_id=offer.id,  # type: ignore[arg-type]
        name=offer.name,
        warnings=warnings,
    )


@router.put(
    "/{offer_id}",
    summary="Update an offer",
    response_model=OfferDetailResponse,
    responses={404: {"description": "Offer not found"}},
)
async def update_offer(
    offer_id: int,
    body: OfferUpdateRequest,
    session: AsyncSession = Depends(get_db),
) -> OfferDetailResponse:
    """Update offer fields."""
    from datetime import UTC, datetime

    stmt = select(Offer).where(Offer.id == offer_id)
    result = await session.execute(stmt)
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail=f"Offer #{offer_id} not found")

    if body.name is not None:
        offer.name = body.name
    if body.url is not None:
        offer.url = body.url
    if body.priority is not None:
        offer.priority = body.priority
    if body.weight is not None:
        offer.weight = body.weight
    if body.is_active is not None:
        offer.is_active = body.is_active
    if body.group_name is not None:
        stmt = select(Group).where(
            Group.name == body.group_name, Group.type == GroupType.OFFER
        )
        result = await session.execute(stmt)
        group = result.scalar_one_or_none()
        offer.group_id = group.id if group else None

    offer.updated_at = datetime.now(UTC)
    await session.commit()

    return _offer_to_detail(offer)
