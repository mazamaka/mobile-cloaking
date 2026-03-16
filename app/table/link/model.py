"""Link model -- binding between App, Offer, and Geo."""

from datetime import datetime

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from app.utils.helpers import utc_now

if TYPE_CHECKING:
    from app.table.app.model import App
    from app.table.geo.model import Geo
    from app.table.offer.model import Offer


class Link(SQLModel, table=True):
    """Binding of App + Offer + Geo.

    CONSTRAINT: Within one App, each Geo can be bound
    to only one Offer. Enforced by UNIQUE(app_id, geo_id).
    """

    __tablename__ = "links"
    __table_args__ = (UniqueConstraint("app_id", "geo_id", name="uq_link_app_geo"),)

    id: int | None = Field(default=None, primary_key=True)

    # App relation
    app_id: int = Field(foreign_key="apps.id", index=True)
    app: Optional["App"] = Relationship(
        back_populates="links", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Offer relation
    offer_id: int = Field(foreign_key="offers.id", index=True)
    offer: Optional["Offer"] = Relationship(
        back_populates="links", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Geo relation
    geo_id: int = Field(foreign_key="geos.id", index=True)
    geo: Optional["Geo"] = Relationship(
        back_populates="links", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Override priority/weight per link (nullable = use offer defaults)
    priority: int | None = Field(default=None)
    weight: int | None = Field(default=None)

    # Routing filters (null = any value matches)
    language: str | None = Field(default=None)
    min_version: str | None = Field(default=None)
    max_version: str | None = Field(default=None)
    att_status: str | None = Field(
        default=None, sa_column=Column(String(20), nullable=True)
    )

    # Per-link overrides (null = use app defaults)
    rate_delay_sec: int | None = Field(default=None)
    push_delay_sec: int | None = Field(default=None)
    icon_name: str | None = Field(default=None)

    # Status
    is_active: bool = Field(default=True, index=True)

    created_at: datetime = Field(
        default_factory=utc_now, sa_type=DateTime
    )

    def __admin_repr__(self, request: object) -> str:
        """Return 'App | Offer | Geo' for admin panel."""
        app_name = getattr(self.app, "name", None) or f"App #{self.app_id}"
        offer_name = getattr(self.offer, "name", None) or f"Offer #{self.offer_id}"
        geo_code = getattr(self.geo, "code", None) or f"Geo #{self.geo_id}"
        return f"{app_name} | {offer_name} | {geo_code}"
