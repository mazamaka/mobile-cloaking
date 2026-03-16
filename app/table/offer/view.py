from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    DateTimeField,
    HasMany,
    HasOne,
    IntegerField,
    StringField,
)
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import ActionFailed

from app.table.offer.model import Offer


class OfferView(ModelView):
    """Admin view for Offer model."""

    name = "Offer"
    name_plural = "Offers"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор оффера"),
        HasOne(
            "group",
            identity="group",
            label="Group",
            help_text="Группа для организации офферов",
        ),
        StringField(
            "name", label="Offer Name", help_text="Название оффера для идентификации"
        ),
        StringField(
            "url", label="Casino URL", help_text="URL казино для редиректа клиентов"
        ),
        IntegerField(
            "priority",
            label="Priority",
            help_text="Приоритет выбора (выше = важнее, по умолчанию)",
        ),
        IntegerField(
            "weight",
            label="Weight",
            help_text="Вес для A/B тестирования (по умолчанию 100)",
        ),
        BooleanField(
            "is_active",
            label="Active",
            help_text="Активен ли оффер (неактивные игнорируются)",
        ),
        HasMany(
            "links",
            identity="link",
            label="Links",
            help_text="Связки оффера с приложениями и гео",
        ),
        DateTimeField(
            "created_at", label="Created At", help_text="Дата и время создания записи"
        ),
        DateTimeField(
            "updated_at",
            label="Updated At",
            help_text="Дата и время последнего обновления",
        ),
    ]

    exclude_fields_from_list = ["url", "links", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "links", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "links", "created_at", "updated_at"]

    searchable_fields = ["name", "url"]
    sortable_fields = ["id", "name", "priority", "is_active"]

    async def before_delete(self, request: Request, obj: Offer) -> None:
        """Prevent deletion if offer has associated links."""
        from sqlalchemy import func, select

        from app.table.link.model import Link

        session = request.state.session
        result = await session.execute(
            select(func.count(Link.id)).where(Link.offer_id == obj.id)
        )
        count = result.scalar() or 0

        if count > 0:
            raise ActionFailed(f"Cannot delete '{obj.name}': has {count} link(s)")


offer_view = OfferView(Offer, icon="fas fa-gift")
