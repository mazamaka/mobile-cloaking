"""Enums for App model."""

from enum import Enum


class AppMode(str, Enum):
    """App operating mode -- determines client response type."""

    NATIVE = "native"  # result=null, show legal app content
    CASINO = "casino"  # result=url, open WebView with casino


class GeoSource(str, Enum):
    """Source for client geo detection."""

    CLOUDFLARE = "cloudflare"  # cf-ipcountry header (real IP country)
    DEVICE = "device"  # device.region from iOS settings


class UpdateMode(str, Enum):
    """Update enforcement mode for app version checks."""

    SOFT = "soft"  # Show update suggestion (dismissible)
    FORCE = "force"  # Force update required (blocking)
