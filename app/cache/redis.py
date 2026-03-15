"""Redis cache for app config lookups."""

import json

from redis.asyncio import Redis

from app.utils.logger import logger

# TTL in seconds
APP_CACHE_TTL = 300  # 5 minutes


class RedisCache:
    """Async Redis cache for frequently accessed data."""

    def __init__(self) -> None:
        self._redis: Redis | None = None
        self._url: str = ""

    async def connect(self, url: str) -> None:
        """Connect to Redis with given URL."""
        self._url = url
        try:
            self._redis = Redis.from_url(self._url, decode_responses=True)
            await self._redis.ping()
            logger.info(f"Redis connected: {self._url}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self._redis = None

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis disconnected")

    @property
    def available(self) -> bool:
        """Check if Redis is connected."""
        return self._redis is not None

    # --- App cache ---

    def _app_key(self, bundle_id: str) -> str:
        return f"app:{bundle_id}"

    async def get_app_dict(self, bundle_id: str) -> dict | None:
        """Get cached app data as dict."""
        if not self._redis:
            return None
        try:
            data = await self._redis.get(self._app_key(bundle_id))
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None

    async def set_app_dict(self, bundle_id: str, app_data: dict) -> None:
        """Cache app data."""
        if not self._redis:
            return
        try:
            await self._redis.setex(
                self._app_key(bundle_id), APP_CACHE_TTL, json.dumps(app_data)
            )
        except Exception:
            pass

    async def invalidate_app(self, bundle_id: str) -> None:
        """Remove app from cache."""
        if not self._redis:
            return
        try:
            await self._redis.delete(self._app_key(bundle_id))
        except Exception:
            pass

    async def invalidate_all_apps(self) -> None:
        """Remove all apps from cache."""
        if not self._redis:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor, match="app:*", count=100
                )
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass


# Global singleton — call cache.connect(url) in lifespan
cache = RedisCache()
