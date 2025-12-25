from starlette_admin import EnumField, StringField, IntegerField, BooleanField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.app.enums import AppMode, UpdateMode
from app.table.app.model import App


class AppView(ModelView):
    """Admin view for App model."""

    name = "App"
    name_plural = "Apps"
    icon = "fa fa-mobile-alt"

    fields = [
        "id",
        "bundle_id",
        "name",
        EnumField("mode", enum=AppMode, label="Mode"),
        IntegerField("rate_delay_sec", label="Rate Delay (sec)"),
        IntegerField("push_delay_sec", label="Push Delay (sec)"),
        StringField("min_version", label="Min Version"),
        StringField("latest_version", label="Latest Version"),
        EnumField("update_mode", enum=UpdateMode, label="Update Mode"),
        StringField("appstore_url", label="App Store URL"),
        BooleanField("is_active", label="Active"),
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_list = ["appstore_url", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["bundle_id", "name"]
    sortable_fields = ["id", "bundle_id", "name", "mode", "is_active", "created_at"]


app_view = AppView(App)
