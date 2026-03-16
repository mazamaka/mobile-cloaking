from starlette.requests import Request
from starlette_admin import DateTimeField, HasOne, IntegerField, JSONField, StringField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.event.model import Event


class EventView(ModelView):
    """Admin view for Event model."""

    name = "Event"
    name_plural = "Events"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор события"),
        HasOne(
            "client",
            identity="client",
            label="Client",
            help_text="Клиент, отправивший событие",
        ),
        HasOne("app", identity="app", label="App", help_text="Приложение клиента"),
        StringField(
            "name",
            label="Event Name",
            help_text="Название события (screen_view, button_click и т.д.)",
        ),
        DateTimeField(
            "event_ts", label="Event Time", help_text="Время события на устройстве"
        ),
        JSONField(
            "props",
            label="Properties",
            help_text="JSON с дополнительными данными события",
        ),
        StringField(
            "app_version",
            label="App Version",
            help_text="Версия приложения при отправке события",
        ),
        DateTimeField(
            "received_at",
            label="Received At",
            help_text="Время получения события сервером",
        ),
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


event_view = EventView(Event, icon="fas fa-calendar-check")
