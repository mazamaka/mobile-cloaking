from typing import Any

from pydantic import BaseModel, Field


class EventAppInfo(BaseModel):
    bundle_id: str
    version: str


class EventIdsInfo(BaseModel):
    internal_id: str


class EventData(BaseModel):
    name: str
    ts: int  # Unix timestamp
    props: dict[str, Any] | None = None


class EventRequest(BaseModel):
    """POST /api/v1/client/event request body."""

    schema_: int = Field(alias="schema")
    app: EventAppInfo
    ids: EventIdsInfo
    event: EventData

    model_config = {"extra": "ignore", "populate_by_name": True}


class EventResponse(BaseModel):
    """Empty response for event endpoint."""

    pass
