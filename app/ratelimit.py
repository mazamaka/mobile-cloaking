"""Rate limiter configuration."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import SETTINGS

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    storage_uri=SETTINGS.redis_url,
)
