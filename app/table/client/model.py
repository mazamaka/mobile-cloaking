"""Client model -- user devices identified by internal_id (UUID from Keychain)."""

from datetime import datetime

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel
from app.utils.helpers import utc_now

from app.schemas.common import ATTStatus

if TYPE_CHECKING:
    from app.table.app.model import App


class Client(SQLModel, table=True):
    """User device record, created on first /client/init request."""

    __tablename__ = "clients"

    id: int | None = Field(default=None, primary_key=True)
    internal_id: str = Field(unique=True, index=True)

    # App relation
    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship(sa_relationship_kwargs={"lazy": "selectin"})

    # App version
    app_version: str

    # Device info
    language: str
    timezone: str
    region: str

    # Privacy - stored as VARCHAR in DB
    att_status: ATTStatus = Field(sa_column=Column(String(20), nullable=False))
    idfa: str | None = Field(default=None)

    # Attribution
    appsflyer_id: str | None = Field(default=None)

    # Push
    push_token: str | None = Field(default=None)
    push_enabled: bool = Field(default=False)

    # Activity
    first_seen_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime
    )
    last_seen_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime
    )
    sessions_count: int = Field(default=1)
