"""InitLog model -- raw init request/response logs."""

from datetime import datetime

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel
from app.utils.helpers import utc_now

if TYPE_CHECKING:
    from app.table.client.model import Client
    from app.table.geo.model import Geo  # noqa: F401


class InitLog(SQLModel, table=True):
    """Log entry for /client/init request-response pair."""

    __tablename__ = "init_logs"

    id: int | None = Field(default=None, primary_key=True)

    # Client relation
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Optional["Client"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Geo relation (resolved geo at request time)
    geo_id: int | None = Field(default=None, foreign_key="geos.id", index=True)
    geo: Optional["Geo"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    # Quick-filter fields (denormalized from JSONB for fast queries)
    ip: str | None = Field(default=None, max_length=45)
    cf_country: str | None = Field(default=None, max_length=10, index=True)
    bundle_id: str | None = Field(default=None, max_length=255, index=True)
    result_mode: str | None = Field(default=None, max_length=10)  # "casino" / "native"
    geo_source: str | None = Field(
        default=None, max_length=15
    )  # "cloudflare" / "device"

    # Request data
    request_headers: dict[str, Any] = Field(sa_column=Column(JSONB))
    request_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Response
    response_code: int
    response_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Timestamp
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime)
