from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.app.model import App
    from app.table.client.model import Client


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)

    # Relations
    client_id: int = Field(foreign_key="clients.id", index=True)
    client: Optional["Client"] = Relationship()

    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship()

    # Event data
    name: str = Field(index=True)
    event_ts: datetime  # Device time
    props: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    # App context
    app_version: str

    # Server time
    received_at: datetime = Field(default_factory=datetime.utcnow)
