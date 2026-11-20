from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Events Aggregator"
    debug: bool = False

    database_url: str | None = None

    postgres_connection_string: str | None = None
    postgres_host: str | None = None
    postgres_port: str | None = None
    postgres_username: str | None = None
    postgres_password: str | None = None
    postgres_database_name: str | None = None

    events_provider_url: str = (
        "http://student-system-events-provider-web.student-system-events-provider.svc:8000"
    )
    events_provider_api_key: str = ""
    sync_interval_hours: float = 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def db_url(self) -> str:
        """Собирает URL для БД из переменных LMS или берет локальный."""

        if self.postgres_connection_string:
            url = self.postgres_connection_string

            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql+asyncpg://", 1)
            if url.startswith("postgresql://") and "+asyncpg" not in url:
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url

        if self.postgres_host:
            return (
                f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"
            )

        if self.database_url:
            return self.database_url

        raise ValueError("Не удалось определить настройки базы данных!")


@lru_cache
def get_settings() -> Settings:
    return Settings()
