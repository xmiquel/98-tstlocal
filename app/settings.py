"""Application settings loaded from environment variables.

Uses pydantic-settings to read from .env with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-level configuration backed by environment variables.

    Resolution order: explicit env var > .env file > class default.

    Fields:
        APP_NAME: Display name for the FastAPI application title.
        DEBUG: Enable debug mode (detailed error pages, hot-reload).
        HOST: Bind address for the uvicorn dev server.
        PORT: Port number for the uvicorn dev server.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "98-tstlocal"
    DATABASE_URL: str = "sqlite:///./data/trading.db"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"  # noqa: S104 — intentional dev-server default
    PORT: int = 8000


settings = Settings()
