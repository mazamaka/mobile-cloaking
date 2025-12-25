from starlette.requests import Request
from starlette_admin import BooleanField, StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.geo.model import Geo


class GeoView(ModelView):
    """Admin view for Geo model."""

    name = "Geo"
    name_plural = "Geos"
    icon = "fas fa-globe"

    fields = [
        "id",
        StringField("code", label="Code (ISO)", help_text="ISO 3166-1 alpha-2: EE, HU, PL"),
        StringField("name", label="Country Name"),
        BooleanField("is_default", label="Default (fallback)"),
        BooleanField("is_active", label="Active"),
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list = ["created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["code", "name"]
    sortable_fields = ["id", "code", "name", "is_default", "is_active"]


geo_view = GeoView(Geo)
