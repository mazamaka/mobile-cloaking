"""Shared utility helpers."""

from typing import Any


def get_enum_value(val: Any) -> Any:
    """Extract value from enum or return as-is.

    Handles SQLAlchemy sometimes returning str instead of Enum.
    """
    return val.value if hasattr(val, "value") else val
