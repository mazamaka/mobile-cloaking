from starlette.requests import Request
from starlette_admin import EnumField, IntegerField, StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.schemas.common import ATTStatus
from app.table.client.model import Client


class ClientView(ModelView):
    """Admin view for Client model."""

    name = "Client"
    name_plural = "Clients"
    icon = "fa fa-users"

    fields = [
        "id",
        "internal_id",
        "app_id",
        StringField("app_version", label="App Version"),
        StringField("language", label="Language"),
        StringField("timezone", label="Timezone"),
        StringField("region", label="Region"),
        EnumField("att_status", enum=ATTStatus, label="ATT Status"),
        StringField("idfa", label="IDFA"),
        StringField("appsflyer_id", label="AppsFlyer ID"),
        StringField("push_token", label="Push Token"),
        "first_seen_at",
        "last_seen_at",
        IntegerField("sessions_count", label="Sessions"),
    ]

    exclude_fields_from_list = [
        "idfa",
        "appsflyer_id",
        "push_token",
        "first_seen_at",
    ]
    exclude_fields_from_create = ["id", "first_seen_at", "last_seen_at", "sessions_count"]
    exclude_fields_from_edit = ["id", "internal_id", "first_seen_at"]

    searchable_fields = ["internal_id", "region", "appsflyer_id"]
    sortable_fields = ["id", "region", "att_status", "sessions_count", "last_seen_at"]

    # Read-only view (clients are created via API)
    def can_create(self, request: Request) -> bool:
        return False


client_view = ClientView(Client)
