"""Test settings override."""

import os

from pydantic_settings import SettingsConfigDict

from src.infrastructure.config.settings import Settings


class TestSettings(Settings):
    """Settings for testing environment.

    Overrides database URL to use test database.
    """

    # Override model_config to NOT read .env file (only use environment variables)
    model_config = SettingsConfigDict(
        env_file=None,  # Don't read .env file in tests
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = os.getenv(  # type: ignore[assignment]
        "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5434/pages_test"
    )
    debug: bool = True
    environment: str = "test"  # type: ignore[assignment]

    # Disable rate limiting in tests by using a very high limit
    # Or we can mock the limiter in tests
