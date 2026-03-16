from starlette.requests import Request
from starlette_admin import DateTimeField, HasOne, IntegerField, JSONField
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
            help_text="HTTP код ответа (200=native, 400=casino)",
        ),
        JSONField(
            "response_body", label="Response Body", help_text="Тело ответа (JSON)"
        ),
        DateTimeField(
            "created_at", label="Created At", help_text="Время создания записи"
        ),
    ]

    exclude_fields_from_list = ["request_headers", "request_body", "response_body"]

    searchable_fields = []
    sortable_fields = ["id", "response_code", "created_at"]

    # Read-only view (logs are created automatically)
    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False


init_log_view = InitLogView(InitLog, icon="fas fa-history")
