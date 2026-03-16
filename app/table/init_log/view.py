from starlette.requests import Request
from starlette_admin import DateTimeField, HasOne, IntegerField, JSONField, StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.init_log.model import InitLog


class InitLogView(ModelView):
    """Admin view for InitLog model."""

    name = "Init Log"
    name_plural = "Init Logs"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор лога"),
        HasOne(
            "client",
            identity="client",
            label="Client",
            help_text="Клиент, выполнивший init запрос",
        ),
        HasOne(
            "geo",
            identity="geo",
            label="Geo",
            help_text="Разрешённый регион клиента на момент запроса",
        ),
        StringField("ip", label="IP", help_text="IP клиента (cf-connecting-ip)"),
        StringField(
            "cf_country",
            label="CF Country",
            help_text="Страна по Cloudflare (cf-ipcountry)",
        ),
        StringField("bundle_id", label="Bundle ID", help_text="Bundle ID приложения"),
        StringField(
            "result_mode",
            label="Result",
            help_text="Результат: casino (URL) или native (null)",
        ),
        StringField(
            "geo_source",
            label="Geo Source",
            help_text="Источник гео на момент запроса: cloudflare или device",
        ),
        JSONField(
            "request_headers",
            label="Request Headers",
            help_text="HTTP заголовки запроса",
        ),
        JSONField(
            "request_body", label="Request Body", help_text="Тело запроса (JSON)"
        ),
        IntegerField(
            "response_code",
            label="Response Code",
            help_text="HTTP код ответа (всегда 200, result определяет режим)",
        ),
        JSONField(
            "response_body", label="Response Body", help_text="Тело ответа (JSON)"
        ),
        DateTimeField(
            "created_at",
            label="Created At",
            help_text="Время создания записи",
            output_format="dd.MM.yyyy HH:mm:ss",
        ),
    ]

    exclude_fields_from_list = ["request_headers", "request_body", "response_body"]

    searchable_fields = ["ip", "cf_country", "bundle_id"]
    sortable_fields = [
        "id",
        "cf_country",
        "bundle_id",
        "result_mode",
        "geo_source",
        "created_at",
    ]

    # Read-only view (logs are created automatically)
    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False


init_log_view = InitLogView(InitLog, icon="fas fa-history")
