from starlette.requests import Request
from starlette_admin import StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.event.model import Event


class EventView(ModelView):
    """Admin view for Event model."""

    name = "Event"
    name_plural = "Events"
    icon = "fas fa-chart-line"

    fields = [
        "id",
        "client_id",
        "app_id",
        StringField("name", label="Event Name"),
        "event_ts",
        "props",
        StringField("app_version", label="App Version"),
        "received_at",
    ]

    exclude_fields_from_list = ["props", "app_version"]
    exclude_fields_from_create = ["id", "received_at"]
    exclude_fields_from_edit = ["id", "received_at"]

    searchable_fields = ["name"]
    sortable_fields = ["id", "name", "event_ts", "received_at"]

    # Read-only view (events are created via API)
    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False


event_view = EventView(Event)
