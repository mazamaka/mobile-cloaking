from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.common import ATTStatus

if TYPE_CHECKING:
    from app.table.app.model import App


class Client(SQLModel, table=True):
    __tablename__ = "clients"

    id: int | None = Field(default=None, primary_key=True)
    internal_id: str = Field(unique=True, index=True)

    # App relation
    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship()

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

    # Activity
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    sessions_count: int = Field(default=1)
