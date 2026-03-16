from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    DateTimeField,
    EnumField,
    HasMany,
    HasOne,
    IntegerField,
    StringField,
)
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin.exceptions import ActionFailed

from app.table.app.enums import AppMode, UpdateMode
from app.table.app.model import App


class AppView(ModelView):
    """Admin view for App model."""

    name = "App"
    name_plural = "Apps"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор приложения"),
        HasOne(
            "group",
            identity="group",
            label="Group",
            help_text="Группа для организации приложений",
        ),
        StringField(
            "bundle_id",
            label="Bundle ID",
            help_text="Уникальный идентификатор пакета (com.example.app)",
        ),
        StringField(
            "apple_id",
            label="Apple ID",
            help_text="ID приложения в App Store (например, 123456789)",
        ),
        StringField(
            "name", label="Name", help_text="Человекочитаемое название приложения"
        ),
        StringField(
            "api_key",
            label="API Key",
            help_text="Ключ авторизации для X-API-Key (пусто = без проверки)",
        ),
        EnumField(
            "mode",
            enum=AppMode,
            label="Mode",
            help_text="NATIVE = 200 OK для модераторов, CASINO = редирект на казино",
        ),
        IntegerField(
            "rate_delay_sec",
            label="Rate Delay (sec)",
            help_text="Задержка перед показом Rate App диалога (секунды)",
        ),
        IntegerField(
            "push_delay_sec",
            label="Push Delay (sec)",
            help_text="Задержка перед запросом Push-уведомлений (секунды)",
        ),
        StringField(
            "min_version",
            label="Min Version",
            help_text="Минимальная поддерживаемая версия приложения",
        ),
        StringField(
            "latest_version",
            label="Latest Version",
            help_text="Последняя доступная версия приложения",
        ),
        EnumField(
            "update_mode",
            enum=UpdateMode,
            label="Update Mode",
            help_text="SOFT = предложение, FORCE = принудительное обновление",
        ),
        StringField(
            "appstore_url",
            label="App Store URL",
            help_text="Ссылка на приложение в App Store",
        ),
        StringField(
            "icon_name",
            label="Icon Name",
            help_text="Имя альтернативной иконки (icon_white, icon_dark, icon_bonus). Пусто = не менять",
        ),
        BooleanField(
            "is_active",
            label="Active",
            help_text="Активно ли приложение (неактивные игнорируются)",
        ),
        HasMany(
            "links",
            identity="link",
            label="Links",
            help_text="Связки приложения с офферами и гео",
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

    exclude_fields_from_list = [
        "api_key",
        "appstore_url",
        "icon_name",
        "links",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_create = ["id", "links", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "links", "created_at", "updated_at"]

    searchable_fields = ["bundle_id", "apple_id", "name"]
    sortable_fields = ["id", "bundle_id", "name", "mode", "is_active", "created_at"]

    async def before_delete(self, request: Request, obj: App) -> None:
        """Prevent deletion if app has associated clients or offer-geo links."""
        from sqlalchemy import func, select

        from app.table.client.model import Client
        from app.table.link.model import Link

        session = request.state.session

        # Check clients
        result = await session.execute(
            select(func.count(Client.id)).where(Client.app_id == obj.id)
        )
        clients_count = result.scalar() or 0

        if clients_count > 0:
            raise ActionFailed(
                f"Cannot delete '{obj.name or obj.bundle_id}': "
                f"has {clients_count} client(s)"
            )

        # Check links
        result = await session.execute(
            select(func.count(Link.id)).where(Link.app_id == obj.id)
        )
        links_count = result.scalar() or 0

        if links_count > 0:
            raise ActionFailed(
                f"Cannot delete '{obj.name or obj.bundle_id}': "
                f"has {links_count} link(s)"
            )


app_view = AppView(App, icon="fas fa-mobile-alt")
