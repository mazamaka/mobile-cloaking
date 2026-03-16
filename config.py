"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _is_docker() -> bool:
    """Check if running inside a Docker container."""
    return Path("/.dockerenv").exists()


IS_DOCKER: bool = _is_docker()


class Settings(BaseSettings):
    """Application configuration via environment variables.

    Settings are loaded from `.env` file and can be overridden
    by actual environment variables (higher priority).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_external_port: int = 5440
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "cloaking"

    # App
    debug: bool = False
    workers: int = 4
    port: int = 8000

    # Admin (required in production - no defaults)
    admin_login: str
    admin_password: str
    auth_secret: str  # Must be at least 32 chars in production

    # Database pool
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Master API key for app registration endpoint
    master_api_key: str | None = None

    # Proxy settings
    trusted_hosts: str = "*"  # Comma-separated list or "*" for all

    # Defaults for apps
    default_rate_delay_sec: int = 180
    default_push_delay_sec: int = 60

    @property
    def effective_host(self) -> str:
        """Return DB host: container name in Docker, localhost otherwise."""
        return self.postgres_host if IS_DOCKER else "127.0.0.1"

    @property
    def effective_port(self) -> int:
        """Return DB port: internal in Docker, external (mapped) locally."""
        return self.postgres_port if IS_DOCKER else self.postgres_external_port

    @property
    def _safe_password(self) -> str:
        """URL-encode password for use in connection strings."""
        from urllib.parse import quote_plus

        return quote_plus(self.postgres_password)

    @property
    def database_url(self) -> str:
        """Async database URL for asyncpg driver."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self._safe_password}"
            f"@{self.effective_host}:{self.effective_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync database URL for psycopg2 driver (Alembic)."""
        return (
            f"postgresql://{self.postgres_user}:{self._safe_password}"
            f"@{self.effective_host}:{self.effective_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Create and cache application settings singleton."""
    return Settings()


SETTINGS: Settings = get_settings()
