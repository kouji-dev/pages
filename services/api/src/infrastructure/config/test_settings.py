"""Test settings override."""

import os

from src.infrastructure.config.settings import Settings


class TestSettings(Settings):
    """Settings for testing environment.
    
    Overrides database URL to use test database.
    """
    
    model_config = Settings.model_config.copy()
    
    database_url: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5434/pages_test"
    )
    debug: bool = True
    environment: str = "test"
    
    # Disable rate limiting in tests by using a very high limit
    # Or we can mock the limiter in tests

