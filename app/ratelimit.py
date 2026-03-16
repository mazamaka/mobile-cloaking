"""Rate limiter configuration."""

from slowapi import Limiter
from starlette.requests import Request


def get_real_ip(request: Request) -> str:
    """Get real client IP: cf-connecting-ip > x-forwarded-for > client.host."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["120/minute"],
)
