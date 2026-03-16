"""Shared utility helpers."""

from datetime import UTC, datetime
from typing import Any


def utc_now() -> datetime:
    """Return current UTC time as naive datetime (for DB columns without timezone)."""
    return datetime.now(UTC).replace(tzinfo=None)


def get_enum_value(val: Any) -> Any:
    """Extract value from enum or return as-is.

    Handles SQLAlchemy sometimes returning str instead of Enum.
    """
    return val.value if hasattr(val, "value") else val
