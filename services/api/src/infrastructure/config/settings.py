"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Pages API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/pages"  # type: ignore[assignment]
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10

    # Redis
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0")  # type: ignore[assignment]

    # JWT Authentication
    jwt_secret_key: str = Field(default="change-me-in-production-super-secret-key")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # CORS
    allowed_origins: list[str] = Field(default=["http://localhost:4200"])

    # File Storage
    storage_path: str = Field(
        default="./storage",
        description="Local filesystem path for file storage",
    )
    storage_base_url: str = Field(
        default="http://localhost:8000/storage",
        description="Base URL for accessing stored files",
    )
    max_file_size_mb: int = Field(
        default=5,
        description="Maximum file size in MB",
    )

    # Logging
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
