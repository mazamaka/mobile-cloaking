"""Event model -- analytics events from iOS clients."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.app.model import App
    from app.table.client.model import Client


class Event(SQLModel, table=True):
    """Analytics event recorded from client device."""

    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)

    # Relations
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Optional["Client"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    # Event data
    name: str = Field(index=True)
    event_ts: datetime  # Device time
    props: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    # App context
    app_version: str

    # Server time
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime
    )
