from starlette.requests import Request
from starlette_admin import BooleanField, HasMany, HasOne, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import ActionFailed

from app.table.offer.model import Offer


class OfferView(ModelView):
    """Admin view for Offer model.

    App-Geo assignments are managed through App-Offer-Geo Links.
    """

    name = "Offer"
    name_plural = "Offers"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор оффера"),
        HasOne("group", identity="group", label="Group", help_text="Группа для организации офферов"),
        StringField("name", label="Offer Name", help_text="Название оффера для идентификации"),
        StringField("url", label="Casino URL", help_text="URL казино для редиректа клиентов"),
        IntegerField("priority", label="Priority", help_text="Приоритет выбора (выше = важнее, по умолчанию)"),
        IntegerField("weight", label="Weight", help_text="Вес для A/B тестирования (по умолчанию 100)"),
        BooleanField("is_active", label="Active", help_text="Активен ли оффер (неактивные игнорируются)"),
        HasMany("app_offer_geos", identity="app-offer-geo", label="App-Geo Links", help_text="Связки оффера с приложениями и гео"),
        StringField("created_at", label="Created At", help_text="Дата и время создания записи"),
        StringField("updated_at", label="Updated At", help_text="Дата и время последнего обновления"),
    ]

    exclude_fields_from_list = ["url", "app_offer_geos", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "app_offer_geos", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "app_offer_geos", "created_at", "updated_at"]

    searchable_fields = ["name", "url"]
    sortable_fields = ["id", "name", "priority", "is_active"]

    async def before_delete(self, request: Request, obj: Offer) -> None:
        """Prevent deletion if offer has associated app-geo links."""
        from sqlalchemy import func, select

        from app.table.app_offer_geo.model import AppOfferGeo

        session = request.state.session
        count = session.scalar(
            select(func.count(AppOfferGeo.id)).where(AppOfferGeo.offer_id == obj.id)
        ) or 0

        if count > 0:
            raise ActionFailed(f"Cannot delete '{obj.name}': has {count} app-geo link(s)")


offer_view = OfferView(Offer, icon="fas fa-gift")
