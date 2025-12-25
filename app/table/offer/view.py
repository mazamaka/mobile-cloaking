from starlette.requests import Request
from starlette_admin import BooleanField, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.offer.model import Offer


class OfferView(ModelView):
    """Admin view for Offer model."""

    name = "Offer"
    name_plural = "Offers"
    icon = "fa fa-gift"

    fields = [
        "id",
        "app_id",
        "geo_id",
        StringField("name", label="Offer Name"),
        StringField("url", label="Casino URL"),
        IntegerField("priority", label="Priority", help_text="Higher = more priority"),
        IntegerField("weight", label="Weight", help_text="For A/B testing (0-100)"),
        BooleanField("is_active", label="Active"),
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list = ["url", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["name", "url"]
    sortable_fields = ["id", "app_id", "geo_id", "name", "priority", "is_active"]


offer_view = OfferView(Offer)
