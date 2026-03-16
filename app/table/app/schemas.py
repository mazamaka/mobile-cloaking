"""Schemas for App registration endpoint."""

import re

from pydantic import BaseModel, field_validator


BUNDLE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9.\-]+$")


class OfferGeoBinding(BaseModel):
    """Binding of an existing offer to a geo for the new app."""

    offer_name: str
    geo_code: str
    priority: int | None = None
    weight: int | None = None


class AppRegisterRequest(BaseModel):
    """Request body for POST /app/register."""

    bundle_id: str
    name: str | None = None
    apple_id: str | None = None
    mode: str = "native"
    api_key: str | None = None
    group_name: str | None = None
    offers: list[OfferGeoBinding] | None = None

    @field_validator("bundle_id")
    @classmethod
    def validate_bundle_id(cls, v: str) -> str:
        """Validate bundle_id matches iOS format."""
        if not BUNDLE_ID_PATTERN.match(v):
            msg = "bundle_id must match ^[a-zA-Z0-9.\\-]+$"
            raise ValueError(msg)
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate mode is 'native' or 'casino'."""
        if v not in ("native", "casino"):
            msg = "mode must be 'native' or 'casino'"
            raise ValueError(msg)
        return v


class AppRegisterResponse(BaseModel):
    """Response body for POST /app/register."""

    app_id: int
    bundle_id: str
    api_key: str | None
    mode: str
    links_created: int
    warnings: list[str]
