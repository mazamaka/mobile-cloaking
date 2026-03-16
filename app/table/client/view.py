from starlette.requests import Request
from starlette_admin import (
    BooleanField,
    DateTimeField,
    EnumField,
    HasOne,
    IntegerField,
    StringField,
)
from starlette_admin.contrib.sqlmodel import ModelView

from app.schemas.common import ATTStatus
from app.table.client.model import Client


class ClientView(ModelView):
    """Admin view for Client model."""

    name = "Client"
    name_plural = "Clients"

    fields = [
        IntegerField(
            "id", label="ID", help_text="Уникальный идентификатор клиента в БД"
        ),
        StringField(
            "internal_id", label="Internal ID", help_text="UUID клиента от устройства"
        ),
        HasOne("app", identity="app", label="App", help_text="Приложение клиента"),
        HasOne(
            "geo", identity="geo", label="Country", help_text="Страна клиента (по IP)"
        ),
        StringField(
            "app_version",
            label="App Version",
            help_text="Версия приложения на устройстве",
        ),
        StringField(
            "language",
            label="Language",
            help_text="Язык устройства (en, ru, de и т.д.)",
        ),
        StringField("timezone", label="Timezone", help_text="Часовой пояс устройства"),
        StringField(
            "region",
            label="Device Region",
            help_text="ISO код региона из настроек устройства (может не совпадать со страной)",
        ),
        StringField(
            "cf_country",
            label="CF Country",
            help_text="Код страны из Cloudflare cf-ipcountry (raw)",
        ),
        EnumField(
            "att_status",
            enum=ATTStatus,
            label="ATT Status",
            help_text="Статус App Tracking Transparency",
        ),
        StringField(
            "idfa", label="IDFA", help_text="Identifier for Advertisers (если разрешен)"
        ),
        StringField(
            "appsflyer_id", label="AppsFlyer ID", help_text="ID атрибуции AppsFlyer"
        ),
        StringField(
            "push_token", label="Push Token", help_text="Токен для Push-уведомлений"
        ),
        BooleanField(
            "push_enabled",
            label="Push Enabled",
            help_text="Разрешены ли Push-уведомления",
        ),
        DateTimeField(
            "first_seen_at",
            label="First Seen At",
            help_text="Дата первого запроса клиента",
            output_format="dd.MM.yyyy HH:mm",
        ),
        DateTimeField(
            "last_seen_at",
            label="Last Seen At",
            help_text="Дата последнего запроса клиента",
            output_format="dd.MM.yyyy HH:mm",
        ),
        IntegerField(
            "sessions_count",
            label="Sessions",
            help_text="Количество сессий (init запросов)",
        ),
    ]

    exclude_fields_from_list = [
        "region",
        "cf_country",
        "idfa",
        "appsflyer_id",
        "push_token",
        "first_seen_at",
    ]
    exclude_fields_from_create = [
        "id",
        "first_seen_at",
        "last_seen_at",
        "sessions_count",
    ]
    exclude_fields_from_edit = ["id", "internal_id", "first_seen_at"]

    searchable_fields = ["internal_id", "cf_country", "appsflyer_id"]
    sortable_fields = [
        "id",
        "cf_country",
        "att_status",
        "sessions_count",
        "last_seen_at",
    ]

    # Read-only view (clients are created via API)
    def can_create(self, request: Request) -> bool:
        return False


client_view = ClientView(Client, icon="fas fa-users")
