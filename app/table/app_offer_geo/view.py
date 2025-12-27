from starlette.requests import Request
from starlette_admin import BooleanField, HasOne, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import FormValidationError

from app.table.app_offer_geo.model import AppOfferGeo


class AppOfferGeoView(ModelView):
    """Admin view for AppOfferGeo triple link.

    Manages app-offer-geo assignments with uniqueness validation.
    """

    name = "App-Offer-Geo"
    name_plural = "App-Offer-Geo Links"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор связки"),
        HasOne("app", identity="app", label="App", help_text="Приложение для которого настраивается оффер"),
        HasOne("offer", identity="offer", label="Offer", help_text="Оффер который будет показан клиентам"),
        HasOne("geo", identity="geo", label="Geo", help_text="Регион для таргетинга (одно гео = один оффер в приложении)"),
        IntegerField("priority", label="Priority Override", help_text="Переопределение приоритета оффера (пусто = использовать из оффера)"),
        IntegerField("weight", label="Weight Override", help_text="Переопределение веса для A/B (пусто = использовать из оффера)"),
        BooleanField("is_active", label="Active", help_text="Активна ли связка (неактивные игнорируются)"),
        StringField("created_at", label="Created At", help_text="Дата и время создания записи"),
    ]

    exclude_fields_from_list = ["priority", "weight", "created_at"]
    exclude_fields_from_create = ["id", "created_at"]
    exclude_fields_from_edit = ["id", "created_at"]

    async def _validate_geo_uniqueness(
        self,
        request: Request,
        app_id: int,
        geo_id: int,
        exclude_id: int | None = None,
    ) -> None:
        """Validate that geo is not already assigned to another offer in this app."""
        from sqlalchemy import select

        from app.table.app.model import App
        from app.table.geo.model import Geo

        session = request.state.session

        if not await session.get(App, app_id):
            raise FormValidationError({"app": "App not found"})

        # Check if geo already assigned in this app
        stmt = select(AppOfferGeo).where(
            AppOfferGeo.app_id == app_id,
            AppOfferGeo.geo_id == geo_id,
        )
        if exclude_id:
            stmt = stmt.where(AppOfferGeo.id != exclude_id)

        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            geo = await session.get(Geo, geo_id)
            raise FormValidationError(
                {"geo": f"Geo '{geo.code if geo else geo_id}' already assigned to another offer"}
            )

    async def before_create(
        self, request: Request, data: dict, obj: AppOfferGeo
    ) -> None:
        """Validate uniqueness before create."""
        app_id = data.get("app")
        geo_id = data.get("geo")

        if app_id and geo_id:
            await self._validate_geo_uniqueness(request, app_id, geo_id)

    async def before_edit(
        self, request: Request, data: dict, obj: AppOfferGeo
    ) -> None:
        """Validate uniqueness when editing."""
        app_id = data.get("app", obj.app_id)
        geo_id = data.get("geo", obj.geo_id)

        if app_id and geo_id:
            await self._validate_geo_uniqueness(request, app_id, geo_id, exclude_id=obj.id)


app_offer_geo_view = AppOfferGeoView(AppOfferGeo, icon="fas fa-project-diagram")
