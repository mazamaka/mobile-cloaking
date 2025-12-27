from starlette.requests import Request
from starlette_admin import BooleanField, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import ActionFailed

from app.table.geo.model import Geo


class GeoView(ModelView):
    """Admin view for Geo model."""

    name = "Geo"
    name_plural = "Geos"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор региона"),
        StringField("code", label="Code (ISO)", help_text="ISO 3166-1 alpha-2 код страны: EE, HU, PL, US и т.д."),
        StringField("name", label="Country Name", help_text="Полное название страны/региона"),
        BooleanField("is_default", label="Default (fallback)", help_text="Использовать как fallback, если точное гео не найдено"),
        BooleanField("is_active", label="Active", help_text="Активен ли регион (неактивные игнорируются)"),
        StringField("created_at", label="Created At", help_text="Дата и время создания записи"),
        StringField("updated_at", label="Updated At", help_text="Дата и время последнего обновления"),
    ]

    exclude_fields_from_list = ["created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["code", "name"]
    sortable_fields = ["id", "code", "name", "is_default", "is_active"]

    async def before_delete(self, request: Request, obj: Geo) -> None:
        """Prevent deletion if geo has associated app-offer links."""
        from sqlalchemy import func, select

        from app.table.app_offer_geo.model import AppOfferGeo

        session = request.state.session
        stmt = select(func.count(AppOfferGeo.id)).where(AppOfferGeo.geo_id == obj.id)
        result = await session.execute(stmt)
        count = result.scalar() or 0

        if count > 0:
            raise ActionFailed(
                f"Cannot delete geo '{obj.code}': "
                f"it has {count} app-offer link(s). "
                f"Delete the links first or deactivate the geo."
            )


geo_view = GeoView(Geo, icon="fas fa-globe")
