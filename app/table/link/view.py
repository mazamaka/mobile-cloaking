from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    DateTimeField,
    HasOne,
    IntegerField,
    StringField,
)
from starlette_admin.exceptions import FormValidationError

from app.admin.base_view import BaseModelView
from app.table.link.model import Link


class LinkView(BaseModelView):
    """Admin view для связок App + Offer + Geo."""

    name = "Link"
    name_plural = "Links"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор связки"),
        HasOne(
            "app",
            identity="app",
            label="App",
            help_text="Приложение для которого настраивается оффер",
        ),
        HasOne(
            "offer",
            identity="offer",
            label="Offer",
            help_text="Оффер который будет показан клиентам",
        ),
        HasOne(
            "geo",
            identity="geo",
            label="Geo",
            help_text="Регион для таргетинга (одно гео = один оффер в приложении)",
        ),
        IntegerField(
            "priority",
            label="Priority Override",
            help_text="Переопределение приоритета оффера (пусто = использовать из оффера)",
        ),
        IntegerField(
            "weight",
            label="Weight Override",
            help_text="Переопределение веса для A/B (пусто = использовать из оффера)",
        ),
        StringField(
            "language",
            label="Language Filter",
            help_text="Фильтр по языку устройства (en, ru). Пусто = любой язык",
        ),
        StringField(
            "min_version",
            label="Min Version",
            help_text="Минимальная версия приложения для этого линка (пусто = любая)",
        ),
        StringField(
            "max_version",
            label="Max Version",
            help_text="Максимальная версия приложения для этого линка (пусто = любая)",
        ),
        StringField(
            "att_status",
            label="ATT Status Filter",
            help_text="Фильтр по ATT статусу (authorized, denied, notDetermined). Пусто = любой",
        ),
        IntegerField(
            "rate_delay_sec",
            label="Rate Delay Override",
            help_text="Переопределение задержки Rate App (пусто = из приложения)",
        ),
        IntegerField(
            "push_delay_sec",
            label="Push Delay Override",
            help_text="Переопределение задержки Push (пусто = из приложения)",
        ),
        StringField(
            "icon_name",
            label="Icon Override",
            help_text="Переопределение иконки (пусто = из приложения)",
        ),
        BooleanField(
            "is_active",
            label="Active",
            help_text="Активна ли связка (неактивные игнорируются)",
        ),
        DateTimeField(
            "created_at",
            label="Created At",
            help_text="Дата и время создания записи",
            output_format="dd.MM.yyyy HH:mm",
        ),
    ]

    exclude_fields_from_list = [
        "priority",
        "weight",
        "language",
        "min_version",
        "max_version",
        "att_status",
        "rate_delay_sec",
        "push_delay_sec",
        "icon_name",
        "created_at",
    ]
    exclude_fields_from_create = ["id", "created_at"]
    exclude_fields_from_edit = ["id", "created_at"]

    async def before_create(self, request: Request, data: dict, obj: Link) -> None:
        """Validate app exists before create."""
        from app.table.app.model import App

        app_id = data.get("app")
        if app_id:
            session = request.state.session
            if not await session.get(App, app_id):
                raise FormValidationError({"app": "App not found"})


link_view = LinkView(Link, icon="fas fa-link")
