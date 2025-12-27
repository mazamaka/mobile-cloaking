from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _is_docker() -> bool:
    return Path("/.dockerenv").exists()


IS_DOCKER = _is_docker()


class Settings(BaseSettings):
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

    # Admin
    admin_login: str = "admin"
    admin_password: str = "admin"
    auth_secret: str = "change-me-in-production"

    # Defaults for apps
    default_rate_delay_sec: int = 180
    default_push_delay_sec: int = 60

    @property
    def effective_host(self) -> str:
        return self.postgres_host if IS_DOCKER else "127.0.0.1"

    @property
    def effective_port(self) -> int:
        """В Docker — внутренний порт, локально — внешний (mapped) порт."""
        return self.postgres_port if IS_DOCKER else self.postgres_external_port

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.effective_host}:{self.effective_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.effective_host}:{self.effective_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


SETTINGS = get_settings()
