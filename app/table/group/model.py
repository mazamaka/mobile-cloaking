"""Group model -- organizational groups for apps and offers."""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.app.model import App
    from app.table.offer.model import Offer


class GroupType(str, Enum):
    """Type of group: APP or OFFER."""

    APP = "app"
    OFFER = "offer"


class Group(SQLModel, table=True):
    """Organizational group for apps or offers."""

    __tablename__ = "groups"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: GroupType = Field(sa_column=Column(String(10), nullable=False, index=True))
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime
    )

    # Relationships
    apps: list["App"] = Relationship(
        back_populates="group", sa_relationship_kwargs={"lazy": "selectin"}
    )
    offers: list["Offer"] = Relationship(
        back_populates="group", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __admin_repr__(self, request: object) -> str:
        """Return 'Name (type)' for admin panel."""
        type_val = self.type.value if hasattr(self.type, "value") else self.type
        return f"{self.name} ({type_val})"
