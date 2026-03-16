from starlette.requests import Request
from starlette_admin import BooleanField, DateTimeField, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import ActionFailed

from app.table.geo.model import Geo


class GeoView(ModelView):
    """Admin view for Geo model."""

    name = "Geo"
    name_plural = "Geos"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор региона"),
        StringField(
            "code",
            label="Code (ISO)",
            help_text="ISO 3166-1 alpha-2 код страны: EE, HU, PL, US и т.д.",
        ),
        StringField(
            "name", label="Country Name", help_text="Полное название страны/региона"
        ),
        BooleanField(
            "is_default",
            label="Default (fallback)",
            help_text="Использовать как fallback, если точное гео не найдено",
        ),
        BooleanField(
            "is_active",
            label="Active",
            help_text="Активен ли регион (неактивные игнорируются)",
        ),
        DateTimeField(
            "created_at",
            label="Created At",
            help_text="Дата и время создания записи",
            output_format="dd.MM.yyyy HH:mm",
        ),
        DateTimeField(
            "updated_at",
            label="Updated At",
            help_text="Дата и время последнего обновления",
            output_format="dd.MM.yyyy HH:mm",
        ),
    ]

    exclude_fields_from_list = ["created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["code", "name"]
    sortable_fields = ["id", "code", "name", "is_default", "is_active"]

    async def before_delete(self, request: Request, obj: Geo) -> None:
        """Prevent deletion if geo has associated links."""
        from sqlalchemy import func, select

        from app.table.link.model import Link

        session = request.state.session
        result = await session.execute(
            select(func.count(Link.id)).where(Link.geo_id == obj.id)
        )
        count = result.scalar() or 0

        if count > 0:
            raise ActionFailed(f"Cannot delete '{obj.code}': has {count} link(s)")


geo_view = GeoView(Geo, icon="fas fa-globe")
