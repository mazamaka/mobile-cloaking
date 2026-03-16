"""Offer model -- casino URLs for geo-targeted redirects."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.group.model import Group
    from app.table.link.model import Link


class Offer(SQLModel, table=True):
    """Casino offer with URL, priority, and weight for A/B testing."""

    __tablename__ = "offers"

    id: int | None = Field(default=None, primary_key=True)

    # Offer info
    name: str
    url: str

    # Priority & weight for selection (defaults, can be overridden per link)
    priority: int = Field(default=0, index=True)
    weight: int = Field(default=100)

    # Group
    group_id: int | None = Field(default=None, foreign_key="groups.id", index=True)
    group: Optional["Group"] = Relationship(
        back_populates="offers", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Status
    is_active: bool = Field(default=True, index=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime
    )

    # Relationships
    links: list["Link"] = Relationship(
        back_populates="offer", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __admin_repr__(self, request: object) -> str:
        """Return human-readable representation for admin panel."""
        return self.name
