from pydantic import BaseModel, Field

from app.schemas.common import ATTStatus
from app.table.app.enums import UpdateMode


# Request schemas
class AppInfo(BaseModel):
    bundle_id: str
    version: str


class DeviceInfo(BaseModel):
    language: str
    timezone: str
    region: str


class PrivacyInfo(BaseModel):
    att: ATTStatus


class IdsInfo(BaseModel):
    internal_id: str
    idfa: str | None = None


class AttributionInfo(BaseModel):
    appsflyer_id: str | None = None


class PushInfo(BaseModel):
    token: str | None = None


class InitRequest(BaseModel):
    """POST /api/v1/client/init request body."""

    schema_: int = Field(alias="schema")
    app: AppInfo
    device: DeviceInfo
    privacy: PrivacyInfo
    ids: IdsInfo
    attribution: AttributionInfo | None = None
    push: PushInfo | None = None

    model_config = {"extra": "ignore", "populate_by_name": True}


# Response schemas
class PromptsConfig(BaseModel):
    rate_delay_sec: int
    push_delay_sec: int


class UpdateConfig(BaseModel):
    min_version: str | None = None
    latest_version: str | None = None
    mode: UpdateMode | None = None
    appstore_url: str | None = None


class InitResponseNative(BaseModel):
    """200 OK response - native mode."""

    prompts: PromptsConfig
    update: UpdateConfig | None = None


class InitResponseCasino(BaseModel):
    """400 Bad Request response - casino mode."""

    result: str
    prompts: PromptsConfig
    update: UpdateConfig | None = None
