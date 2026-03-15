"""Request/response Pydantic schemas for /api/v1/client/init endpoint."""

from pydantic import BaseModel, Field

from app.schemas.common import ATTStatus
from app.table.app.enums import UpdateMode


# --- Request schemas ---


class AppInfo(BaseModel):
    """Application metadata sent by the iOS client."""

    bundle_id: str = Field(
        ...,
        max_length=255,
        pattern=r"^[a-zA-Z0-9.\-]+$",
        description="Bundle ID (e.g., com.company.app)",
        examples=["com.example.game"],
    )
    version: str = Field(
        ...,
        max_length=20,
        description="App version string",
        examples=["1.0.0", "2.1.3"],
    )


class DeviceInfo(BaseModel):
    """Device information from the iOS client."""

    language: str = Field(
        ...,
        max_length=10,
        description="Device language in ISO format (e.g., en-US, ru-RU)",
        examples=["en-US", "ru-RU", "en-EE"],
    )
    timezone: str = Field(
        ...,
        max_length=50,
        description="Device timezone identifier",
        examples=["Europe/Moscow", "Europe/Budapest", "America/New_York"],
    )
    region: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Device region (ISO 3166-1 alpha-2)",
        examples=["RU", "EE", "HU", "US"],
    )


class PrivacyInfo(BaseModel):
    """Privacy settings from the iOS client."""

    att: ATTStatus = Field(
        ...,
        description=(
            "App Tracking Transparency status (iOS 14+): "
            "authorized, denied, notDetermined, restricted, legacy, unavailable"
        ),
    )


class IdsInfo(BaseModel):
    """Device identifiers."""

    internal_id: str = Field(
        ...,
        max_length=36,
        pattern=r"^[0-9a-fA-F\-]{36}$",
        description="Unique device ID (UUID v4 stored in Keychain)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    idfa: str | None = Field(
        default=None,
        description="IDFA (Identifier for Advertisers). Available only when att=authorized",
        examples=["AEBE52E7-03EE-455A-B3C4-E57283966239"],
    )


class AttributionInfo(BaseModel):
    """Attribution data from AppsFlyer or similar SDK."""

    appsflyer_id: str | None = Field(
        default=None,
        description="AppsFlyer ID for install attribution",
        examples=["1765992827433-2791097"],
    )


class PushInfo(BaseModel):
    """Push notification data."""

    token: str | None = Field(  # noqa: S105
        default=None,
        description="APNs push notification identifier",
    )


class InitRequest(BaseModel):
    """Request body for POST /api/v1/client/init.

    Sent on every app launch to determine operating mode.
    """

    schema_: int = Field(
        alias="schema",
        description="API schema version (currently always 1)",
        examples=[1],
    )
    app: AppInfo = Field(..., description="Application metadata")
    device: DeviceInfo = Field(..., description="Device information")
    privacy: PrivacyInfo = Field(..., description="Privacy settings (ATT status)")
    ids: IdsInfo = Field(..., description="Device identifiers")
    attribution: AttributionInfo | None = Field(
        default=None, description="Attribution data (optional)"
    )
    push: PushInfo | None = Field(default=None, description="Push data (optional)")

    model_config = {"extra": "ignore", "populate_by_name": True}


# --- Response schemas ---


class PromptsConfig(BaseModel):
    """Prompt timing configuration for Rate Us and Push dialogs."""

    rate_delay_sec: int = Field(
        ...,
        description="Delay before showing Rate App dialog (seconds)",
        examples=[180],
    )
    push_delay_sec: int = Field(
        ...,
        description="Delay before push notification permission request (seconds)",
        examples=[60],
    )


class UpdateConfig(BaseModel):
    """App update configuration."""

    min_version: str | None = Field(
        default=None,
        description="Minimum supported app version",
        examples=["1.0.0"],
    )
    latest_version: str | None = Field(
        default=None,
        description="Latest available app version",
        examples=["1.2.0"],
    )
    mode: UpdateMode | None = Field(
        default=None,
        description="Update mode: soft (suggestion) or force (mandatory)",
    )
    appstore_url: str | None = Field(
        default=None,
        description="App Store URL for update",
    )


class InitResponse(BaseModel):
    """Response for /client/init.

    Mode is determined by the result field:
    - result is a URL string -- Casino mode (open WebView)
    - result is null -- Native mode (show legal content)
    """

    result: str | None = Field(
        default=None,
        description="Casino URL for WebView. If null -- show native content.",
    )
    prompts: PromptsConfig = Field(..., description="Prompt timing configuration")
    update: UpdateConfig | None = Field(
        default=None, description="Update info (if available)"
    )
    icon: str | None = Field(
        default=None,
        description="Alternative icon name (e.g., icon_white, icon_dark). Null = don't change.",
    )
