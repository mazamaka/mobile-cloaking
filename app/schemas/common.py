"""Shared Pydantic schemas and enums used across the application."""

from enum import Enum


class ATTStatus(str, Enum):
    """App Tracking Transparency status from iOS 14+."""

    AUTHORIZED = "authorized"
    DENIED = "denied"
    NOT_DETERMINED = "notDetermined"
    RESTRICTED = "restricted"
    LEGACY = "legacy"  # iOS < 14
    UNAVAILABLE = "unavailable"  # Tracking disabled on device
