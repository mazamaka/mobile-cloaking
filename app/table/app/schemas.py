"""Schemas for App API endpoints."""

import re

from pydantic import BaseModel, field_validator

from app.table.app.enums import AppMode

BUNDLE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9.\-]+$")

_ALLOWED_MODES = {e.value for e in AppMode}


def _validate_mode_value(v: str) -> str:
    """Validate mode field value against AppMode enum."""
    if v not in _ALLOWED_MODES:
        msg = f"Invalid mode: {v}. Allowed: {', '.join(sorted(_ALLOWED_MODES))}"
        raise ValueError(msg)
    return v


# --- Registration ---


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
        """Validate mode is allowed."""
        return _validate_mode_value(v)


class AppRegisterResponse(BaseModel):
    """Response body for POST /app/register."""

    app_id: int
    bundle_id: str
    api_key: str | None
    mode: str
    links_created: int
    warnings: list[str]


# --- Detail / List ---


class AppDetailResponse(BaseModel):
    """Full app details."""

    id: int
    bundle_id: str
    apple_id: str | None
    name: str | None
    api_key: str | None
    group_id: int | None
    mode: str
    rate_delay_sec: int
    push_delay_sec: int
    min_version: str | None
    latest_version: str | None
    update_mode: str | None
    appstore_url: str | None
    icon_name: str | None
    is_active: bool
    links_count: int


class AppListResponse(BaseModel):
    """Paginated list of apps."""

    items: list[AppDetailResponse]
    total: int


# --- Update ---


class AppUpdateRequest(BaseModel):
    """Request body for PUT /app/{bundle_id}."""

    name: str | None = None
    apple_id: str | None = None
    mode: str | None = None
    api_key: str | None = None
    group_name: str | None = None
    rate_delay_sec: int | None = None
    push_delay_sec: int | None = None
    min_version: str | None = None
    latest_version: str | None = None
    update_mode: str | None = None
    appstore_url: str | None = None
    icon_name: str | None = None
    is_active: bool | None = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str | None) -> str | None:
        if v is not None:
            _validate_mode_value(v)
        return v

    @field_validator("update_mode")
    @classmethod
    def validate_update_mode(cls, v: str | None) -> str | None:
        if v is not None and v not in ("soft", "force"):
            msg = "update_mode must be 'soft' or 'force'"
            raise ValueError(msg)
        return v


# --- Mode switch ---


class AppModeRequest(BaseModel):
    """Request body for PUT /app/{bundle_id}/mode."""

    mode: str

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        return _validate_mode_value(v)


class AppModeResponse(BaseModel):
    """Response for mode switch."""

    bundle_id: str
    old_mode: str
    new_mode: str


# --- Bulk mode ---


class AppBulkModeRequest(BaseModel):
    """Request body for POST /app/bulk-mode."""

    bundle_ids: list[str]
    mode: str

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        return _validate_mode_value(v)


class AppBulkModeResponse(BaseModel):
    """Response for bulk mode switch."""

    updated: int
    not_found: list[str]


# --- Add link ---


class AppAddLinkRequest(BaseModel):
    """Request body for POST /app/{bundle_id}/links."""

    offer_name: str
    geo_code: str
    priority: int | None = None
    weight: int | None = None


class AppAddLinkResponse(BaseModel):
    """Response for adding a link."""

    link_id: int
    app_id: int
    offer_id: int
    geo_id: int


# --- Test init ---


class TestInitResponse(BaseModel):
    """Response for test-init dry run."""

    mode: str
    would_return: str | None
    offer_name: str | None = None
    geo_code: str | None = None
    geo_matched: str | None = None


# --- Simple message ---


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
