"""App model -- iOS applications managed by the system."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from app.table.app.enums import AppMode, UpdateMode

if TYPE_CHECKING:
    from app.table.group.model import Group
    from app.table.link.model import Link


class App(SQLModel, table=True):
    """iOS application with mode, prompt settings, and update configuration."""

    __tablename__ = "apps"

    id: int | None = Field(default=None, primary_key=True)
    bundle_id: str = Field(unique=True, index=True)
    apple_id: str | None = Field(default=None, index=True)
    name: str | None = Field(default=None)
    api_key: str | None = Field(default=None, index=True)

    # Group
    group_id: int | None = Field(default=None, foreign_key="groups.id", index=True)
    group: Optional["Group"] = Relationship(back_populates="apps")

    # Mode - stored as VARCHAR in DB
    mode: AppMode = Field(
        default=AppMode.NATIVE,
        sa_column=Column(String(10), nullable=False, default="native"),
    )

    # Prompts settings
    rate_delay_sec: int = Field(default=180)
    push_delay_sec: int = Field(default=60)

    # Update settings
    min_version: str | None = Field(default=None)
    latest_version: str | None = Field(default=None)
    update_mode: UpdateMode | None = Field(
        default=None, sa_column=Column(String(10), nullable=True)
    )
    appstore_url: str | None = Field(default=None)

    # Icon
    icon_name: str | None = Field(default=None)

    # Meta
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    links: list["Link"] = Relationship(back_populates="app")

    def __admin_repr__(self, request: object) -> str:
        """Return human-readable representation for admin panel."""
        return self.name or self.bundle_id
