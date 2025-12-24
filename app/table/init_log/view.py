from starlette.requests import Request
from starlette_admin import IntegerField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.init_log.model import InitLog


class InitLogView(ModelView):
    """Admin view for InitLog model."""

    name = "Init Log"
    name_plural = "Init Logs"
    icon = "fa fa-history"

    fields = [
        "id",
        "client_id",
        "request_headers",
        "request_body",
        IntegerField("response_code", label="Response Code"),
        "response_body",
        "created_at",
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


init_log_view = InitLogView(InitLog)
