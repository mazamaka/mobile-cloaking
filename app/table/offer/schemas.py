"""Schemas for Offer API endpoints."""

from pydantic import BaseModel


class OfferCreateRequest(BaseModel):
    """Request body for POST /offer."""

    name: str
    url: str
    priority: int = 0
    weight: int = 100
    group_name: str | None = None


class OfferUpdateRequest(BaseModel):
    """Request body for PUT /offer/{offer_id}."""

    name: str | None = None
    url: str | None = None
    priority: int | None = None
    weight: int | None = None
    group_name: str | None = None
    is_active: bool | None = None


class OfferDetailResponse(BaseModel):
    """Full offer details."""

    id: int
    name: str
    url: str
    priority: int
    weight: int
    group_id: int | None
    is_active: bool
    links_count: int


class OfferListResponse(BaseModel):
    """List of offers."""

    items: list[OfferDetailResponse]
    total: int


class OfferCreatedResponse(BaseModel):
    """Response for offer creation."""

    offer_id: int
    name: str
    warnings: list[str]
