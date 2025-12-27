from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.table.link.model import Link


class Geo(SQLModel, table=True):
    """Geographic regions/countries for offer targeting."""

    __tablename__ = "geos"

    id: int | None = Field(default=None, primary_key=True)

    # ISO 3166-1 alpha-2 code (EE, HU, PL, US, etc.)
    code: str = Field(unique=True, index=True, max_length=10)

    # Human-readable name
    name: str

    # Is this a default/fallback geo (matches any country)
    is_default: bool = Field(default=False, index=True)

    # Status
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    links: list["Link"] = Relationship(back_populates="geo")

    def __admin_repr__(self, request) -> str:
        return f"{self.code} ({self.name})"
