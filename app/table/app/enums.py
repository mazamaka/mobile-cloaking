from enum import Enum


class AppMode(str, Enum):
    """App mode - determines response type."""

    NATIVE = "native"  # Return 200 OK
    CASINO = "casino"  # Return 400 with casino URL


class UpdateMode(str, Enum):
    """Update mode for app version checks."""

    SOFT = "soft"  # Show update suggestion
    FORCE = "force"  # Force update required
