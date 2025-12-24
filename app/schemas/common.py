from enum import Enum


class ATTStatus(str, Enum):
    """App Tracking Transparency status from iOS."""

    AUTHORIZED = "authorized"
    DENIED = "denied"
    NOT_DETERMINED = "notDetermined"
    RESTRICTED = "restricted"
    LEGACY = "legacy"  # iOS < 14
    UNAVAILABLE = "unavailable"  # Tracking disabled
