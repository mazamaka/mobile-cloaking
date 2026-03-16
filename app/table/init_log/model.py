"""InitLog model -- raw init request/response logs."""

from datetime import datetime

from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel
from app.utils.helpers import utc_now

if TYPE_CHECKING:
    from app.table.client.model import Client


class InitLog(SQLModel, table=True):
    """Log entry for /client/init request-response pair."""

    __tablename__ = "init_logs"

    id: int | None = Field(default=None, primary_key=True)

    # Client relation
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Optional["Client"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Request data
    request_headers: dict[str, Any] = Field(sa_column=Column(JSONB))
    request_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Response
    response_code: int
    response_body: dict[str, Any] = Field(sa_column=Column(JSONB))

    # Timestamp
    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime
    )
