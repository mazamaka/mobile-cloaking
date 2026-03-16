"""Schemas for Geo API endpoints."""

from pydantic import BaseModel, field_validator


class GeoCreateRequest(BaseModel):
    """Request body for POST /geo."""

    code: str
    name: str
    is_default: bool = False

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or len(v) > 10:
            msg = "code must be 1-10 characters"
            raise ValueError(msg)
        return v.upper()


class GeoDetailResponse(BaseModel):
    """Full geo details."""

    id: int
    code: str
    name: str
    is_default: bool
    is_active: bool
    links_count: int


class GeoListResponse(BaseModel):
    """List of geos."""

    items: list[GeoDetailResponse]
    total: int


class GeoCreatedResponse(BaseModel):
    """Response for geo creation."""

    geo_id: int
    code: str
    name: str
