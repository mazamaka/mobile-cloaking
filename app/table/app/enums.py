"""Enums for App model."""

from enum import Enum


class AppMode(str, Enum):
    """App operating mode -- determines client response type."""

    NATIVE = "native"  # result=null, show legal app content
    CASINO = "casino"  # result=url, open WebView with casino


class UpdateMode(str, Enum):
    """Update enforcement mode for app version checks."""

    SOFT = "soft"  # Show update suggestion (dismissible)
    FORCE = "force"  # Force update required (blocking)
