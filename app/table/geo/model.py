"""Geo model -- geographic regions for offer targeting."""

from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel
from app.utils.helpers import utc_now

if TYPE_CHECKING:
    from app.table.link.model import Link


class Geo(SQLModel, table=True):
    """Geographic region (country) for offer targeting.

    One geo can be marked as is_default=True to serve as fallback
    when no exact region match is found.
    """

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
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime)
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime)

    # Relationships
    links: list["Link"] = Relationship(
        back_populates="geo", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def flag(self) -> str:
        """Convert ISO alpha-2 code to flag emoji (e.g. 'HU' -> '🇭🇺')."""
        if not self.code or len(self.code) != 2:
            return "🌐"
        return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in self.code.upper())

    def __admin_repr__(self, request: object) -> str:
        """Return '🇭🇺 HU (Hungary)' for admin panel."""
        return f"{self.flag} {self.code} ({self.name})"
