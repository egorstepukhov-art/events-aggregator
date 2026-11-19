from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Основные настройки приложения
    app_name: str = "Events Aggregator"
    debug: bool = True

    # База данных
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/events_db"

    # Внешний Events Provider API
    events_provider_url: str = "http://events-provider.dev-2.python-labs.ru"
    events_provider_api_key: str = ""

    # Настройки синхронизации
    sync_interval_hours: float = 24

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()