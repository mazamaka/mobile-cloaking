"""Base ModelView with shared defaults for all admin views."""

from starlette_admin import ExportType
from starlette_admin.contrib.sqlmodel import ModelView


class BaseModelView(ModelView):
    """Base view with common defaults: sort by ID desc, all export types."""

    fields_default_sort = [("id", True)]
    export_types = list(ExportType)
