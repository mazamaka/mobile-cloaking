from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.app.model import App
    from app.table.geo.model import Geo


class Offer(SQLModel, table=True):
    """Offer with geo-targeting for casino redirects."""

    __tablename__ = "offers"

    id: int | None = Field(default=None, primary_key=True)

    # App relation
    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship()

    # Geo relation
    geo_id: int = Field(foreign_key="geos.id", index=True)
    geo: Optional["Geo"] = Relationship()

    # Offer info
    name: str  # "Pin-Up Hungary", "1win Estonia"
    url: str  # https://casino.com/?sub=...

    # Priority & weight for selection
    priority: int = Field(default=0, index=True)  # Higher = more priority
    weight: int = Field(default=100)  # For A/B testing (0-100)

    # Status
    is_active: bool = Field(default=True, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
