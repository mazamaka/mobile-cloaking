from datetime import datetime

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel

from app.table.app.enums import AppMode, UpdateMode


class App(SQLModel, table=True):
    __tablename__ = "apps"

    id: int | None = Field(default=None, primary_key=True)
    bundle_id: str = Field(unique=True, index=True)
    name: str | None = Field(default=None)

    # Mode - stored as VARCHAR in DB
    mode: AppMode = Field(default=AppMode.NATIVE, sa_column=Column(String(10), nullable=False, default="native"))

    # Prompts settings
    rate_delay_sec: int = Field(default=180)
    push_delay_sec: int = Field(default=60)

    # Update settings
    min_version: str | None = Field(default=None)
    latest_version: str | None = Field(default=None)
    update_mode: UpdateMode | None = Field(default=None, sa_column=Column(String(10), nullable=True))
    appstore_url: str | None = Field(default=None)

    # Meta
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
