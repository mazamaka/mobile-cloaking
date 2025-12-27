from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.app_offer_geo.model import AppOfferGeo
    from app.table.group.model import Group


class Offer(SQLModel, table=True):
    """Offer for casino redirects. Can be used in multiple apps."""

    __tablename__ = "offers"

    id: int | None = Field(default=None, primary_key=True)

    # Offer info
    name: str
    url: str

    # Priority & weight for selection (defaults, can be overridden per app-geo)
    priority: int = Field(default=0, index=True)
    weight: int = Field(default=100)

    # Group
    group_id: int | None = Field(default=None, foreign_key="groups.id", index=True)
    group: Optional["Group"] = Relationship(back_populates="offers")

    # Status
    is_active: bool = Field(default=True, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    app_offer_geos: list["AppOfferGeo"] = Relationship(back_populates="offer")

    def __admin_repr__(self, request) -> str:
        return self.name
