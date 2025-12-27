from starlette_admin import BooleanField, EnumField, IntegerField, StringField, TextAreaField
from starlette_admin.contrib.sqlmodel import ModelView

from app.table.group.model import Group, GroupType


class GroupView(ModelView):
    """Admin view for Group model."""

    name = "Group"
    name_plural = "Groups"

    fields = [
        IntegerField("id", label="ID", help_text="Уникальный идентификатор группы"),
        StringField("name", label="Group Name", help_text="Название группы для организации"),
        EnumField("type", enum=GroupType, label="Type", help_text="APP = группа приложений, OFFER = группа офферов"),
        TextAreaField("description", label="Description", help_text="Описание группы (опционально)"),
        BooleanField("is_active", label="Active", help_text="Активна ли группа"),
        StringField("created_at", label="Created At", help_text="Дата и время создания записи"),
        StringField("updated_at", label="Updated At", help_text="Дата и время последнего обновления"),
    ]

    exclude_fields_from_list = ["description", "created_at", "updated_at"]
    exclude_fields_from_create = ["id", "created_at", "updated_at"]
    exclude_fields_from_edit = ["id", "created_at", "updated_at"]

    searchable_fields = ["name"]
    sortable_fields = ["id", "name", "type", "is_active"]


group_view = GroupView(Group, icon="fas fa-layer-group")
