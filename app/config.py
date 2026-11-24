import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    app_version: str
    database_path: str
    api_key: str | None


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "notes-api"),
        app_env=os.getenv("APP_ENV", "development"),
        app_version=os.getenv("APP_VERSION", "0.0.0-dev"),
        database_path=os.getenv("DATABASE_PATH", "notes.db"),
        api_key=os.getenv("API_KEY") or None,
    )
