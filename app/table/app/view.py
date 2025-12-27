from starlette.requests import Request
from starlette_admin import BooleanField, EnumField, HasMany, HasOne, IntegerField, StringField
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
        HasOne("group", identity="group", label="Group", help_text="Группа для организации приложений"),
        StringField("bundle_id", label="Bundle ID", help_text="Уникальный идентификатор пакета (com.example.app)"),
        StringField("apple_id", label="Apple ID", help_text="ID приложения в App Store (например, 123456789)"),
        StringField("name", label="Name", help_text="Человекочитаемое название приложения"),
        EnumField("mode", enum=AppMode, label="Mode", help_text="NATIVE = 200 OK для модераторов, CASINO = редирект на казино"),
        IntegerField("rate_delay_sec", label="Rate Delay (sec)", help_text="Задержка перед показом Rate App диалога (секунды)"),
        IntegerField("push_delay_sec", label="Push Delay (sec)", help_text="Задержка перед запросом Push-уведомлений (секунды)"),
        StringField("min_version", label="Min Version", help_text="Минимальная поддерживаемая версия приложения"),
        StringField("latest_version", label="Latest Version", help_text="Последняя доступная версия приложения"),
        EnumField("update_mode", enum=UpdateMode, label="Update Mode", help_text="SOFT = предложение, FORCE = принудительное обновление"),
        StringField("appstore_url", label="App Store URL", help_text="Ссылка на приложение в App Store"),
        BooleanField("is_active", label="Active", help_text="Активно ли приложение (неактивные игнорируются)"),
        HasMany("app_offer_geos", identity="app-offer-geo", label="Offer-Geo Links", help_text="Связки приложения с офферами и гео"),
        StringField("created_at", label="Created At", help_text="Дата и время создания записи"),
        StringField("updated_at", label="Updated At", help_text="Дата и время последнего обновления"),
    ]

    exclude_fields_from_list = ["appstore_url", "app_offer_geos", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "app_offer_geos", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "app_offer_geos", "created_at", "updated_at"]

    searchable_fields = ["bundle_id", "apple_id", "name"]
    sortable_fields = ["id", "bundle_id", "name", "mode", "is_active", "created_at"]

    async def before_delete(self, request: Request, obj: App) -> None:
        """Prevent deletion if app has associated clients or offer-geo links."""
        from sqlalchemy import func, select

        from app.table.app_offer_geo.model import AppOfferGeo
        from app.table.client.model import Client

        async with request.state.session as session:
            # Check clients
            stmt = select(func.count(Client.id)).where(Client.app_id == obj.id)
            result = await session.execute(stmt)
            clients_count = result.scalar() or 0

            if clients_count > 0:
                raise ActionFailed(
                    f"Cannot delete app '{obj.name or obj.bundle_id}': "
                    f"it has {clients_count} associated client(s). "
                    f"Delete clients first or deactivate the app."
                )

            # Check app-offer-geo links
            stmt = select(func.count(AppOfferGeo.id)).where(AppOfferGeo.app_id == obj.id)
            result = await session.execute(stmt)
            links_count = result.scalar() or 0

            if links_count > 0:
                raise ActionFailed(
                    f"Cannot delete app '{obj.name or obj.bundle_id}': "
                    f"it has {links_count} offer-geo link(s). "
                    f"Delete the links first or deactivate the app."
                )


app_view = AppView(App, icon="fas fa-mobile-alt")
