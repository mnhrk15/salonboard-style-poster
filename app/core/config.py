"""Application configuration module."""

from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Application
    APP_NAME: str = "SALON BOARD Style Poster"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ENCRYPTION_KEY: str = Field(..., min_length=32)
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: PostgresDsn
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: RedisDsn

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # File Upload
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    UPLOAD_DIR: str = "/app/uploads"
    LOG_DIR: str = "/app/logs"
    SCREENSHOT_DIR: str = "/app/screenshots"

    # Playwright
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_SLOW_MO: int = 100
    PLAYWRIGHT_TIMEOUT: int = 180000

    # SALON BOARD
    SALONBOARD_LOGIN_URL: str = "https://salonboard.com/login/"


# Global settings instance
settings = Settings()
