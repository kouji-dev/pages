"""Pytest configuration and fixtures."""

import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.entities import User
from src.domain.value_objects import Email, HashedPassword, Password
from src.infrastructure.config.test_settings import TestSettings
from src.infrastructure.database.config import Base

# Import all models to ensure they are registered in Base.metadata
from src.infrastructure.database.models import (  # noqa: F401
    organization,
    page,
    project,
    user,
)
from src.infrastructure.security import BcryptPasswordService, JWTTokenService

# Use test settings
_test_settings = TestSettings()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for session-scoped async fixtures."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock rate limiter BEFORE any routes are imported
# This must be at module level to run before imports
import importlib  # noqa: E402


# Create a no-op limiter class
class NoOpLimiter:
    """Limiter mock that doesn't enforce any limits."""

    def limit(self, *args, **kwargs):
        """Return a decorator that does nothing."""

        def decorator(func):
            return func

        return decorator


# Replace limiter in rate_limit module BEFORE any imports
# This must happen at module level before any routes are imported
from src.presentation.middlewares import rate_limit  # noqa: E402

_original_limiter = rate_limit.limiter
mock_limiter = NoOpLimiter()
rate_limit.limiter = mock_limiter

# Also update the export in middlewares/__init__.py
# The limiter is imported directly, so we need to update the module that exports it
import src.presentation.middlewares as middlewares_module  # noqa: E402

if hasattr(middlewares_module, "limiter"):
    middlewares_module.limiter = mock_limiter

# Reload modules that use the limiter to pick up the mock
# Note: The decorator has already been applied, but reloading ensures new imports use the mock
modules_to_reload = [
    "src.presentation.middlewares",
    "src.presentation.api.v1.auth",
    "src.presentation.api.v1",
    "src.presentation.api",
]

for module_name in modules_to_reload:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings."""
    return _test_settings


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine and ensure tables exist."""
    # Create a separate engine for tests
    engine = create_async_engine(
        str(_test_settings.database_url),
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables using a connection that auto-commits
    # Use begin() which auto-commits when the context exits
    async with engine.begin() as conn:
        # Drop all tables first to ensure clean state
        await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)

    # Verify tables exist by checking the database
    async with engine.connect() as conn:
        from sqlalchemy import text

        result = await conn.execute(
            text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        )
        table_count = result.scalar()
        if table_count == 0:
            raise RuntimeError(
                "No tables found in test database! Expected tables from Base.metadata."
            )

    yield engine

    # Cleanup: drop all tables after all tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncSession:
    """Create a test database session with transaction rollback.

    This fixture creates a session that will be reused across test app instances.
    Tables are guaranteed to exist as they are created in test_engine fixture.
    """
    # Create a session factory bound to test engine
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Create a connection and start a nested transaction (savepoint) for isolation
    connection = await test_engine.connect()
    # Start a nested transaction using savepoint for better isolation
    trans = await connection.begin()
    nested_trans = await connection.begin_nested()

    # Bind session to connection
    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        # Always rollback nested transaction first, then outer transaction
        await session.close()
        await nested_trans.rollback()
        await trans.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def test_app(db_session):
    """Create FastAPI app with overridden session dependency.

    This fixture is async to properly handle the async session.
    """
    from src.infrastructure.database import get_session
    from src.main import create_app

    # Create app without rate limiting
    app = create_app(enable_rate_limiting=False)

    # Create a wrapper function that provides the session
    async def _get_session_override():
        yield db_session

    # Override the dependency
    app.dependency_overrides[get_session] = _get_session_override

    yield app

    # Clear overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(test_app) -> AsyncClient:
    """Create a test HTTP client using httpx.AsyncClient with ASGITransport.

    This approach:
    - Uses the same event loop as pytest-asyncio (no conflicts)
    - Provides real Starlette Request objects (works with rate limiting)
    - Fully async compatible
    """
    # test_app is wrapped by pytest-asyncio, so it's already the app object
    # when we receive it in this fixture
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def password_service() -> BcryptPasswordService:
    """Get password service for testing."""
    return BcryptPasswordService()


@pytest.fixture
def token_service() -> JWTTokenService:
    """Get token service for testing."""
    return JWTTokenService()


@pytest.fixture
def valid_email() -> Email:
    """Create a valid email for testing."""
    return Email("test@example.com")


@pytest.fixture
def valid_password() -> Password:
    """Create a valid password for testing."""
    return Password("SecurePass123!")


@pytest.fixture
def hashed_password(
    password_service: BcryptPasswordService, valid_password: Password
) -> HashedPassword:
    """Create a hashed password for testing."""
    return password_service.hash(valid_password)


@pytest.fixture
def sample_user(valid_email: Email, hashed_password: HashedPassword) -> User:
    """Create a sample user for testing."""
    return User.create(
        email=valid_email,
        password_hash=hashed_password,
        name="Test User",
    )


@pytest_asyncio.fixture
async def test_user(db_session) -> User:
    """Create a test user in the database."""
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository
    from src.infrastructure.security import BcryptPasswordService

    user_repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    email = Email("test@example.com")
    password = Password("TestPassword123!")
    hashed_password = password_service.hash(password)

    test_user = User.create(
        email=email,
        password_hash=hashed_password,
        name="Test User",
    )

    await user_repo.create(test_user)
    await db_session.flush()  # Flush to get ID, but don't commit (test will rollback)

    return test_user


@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    """Create an admin user in the database with organization admin role."""
    from src.infrastructure.database.models import OrganizationMemberModel, OrganizationModel
    from src.infrastructure.database.repositories import SQLAlchemyUserRepository
    from src.infrastructure.security import BcryptPasswordService

    user_repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    email = Email("admin@example.com")
    password = Password("AdminPassword123!")
    hashed_password = password_service.hash(password)

    admin_user = User.create(
        email=email,
        password_hash=hashed_password,
        name="Admin User",
    )

    await user_repo.create(admin_user)
    await db_session.flush()

    # Create an organization and make user admin
    org = OrganizationModel(
        name="Test Organization",
        slug="test-org",
        settings=None,
    )
    db_session.add(org)
    await db_session.flush()

    org_member = OrganizationMemberModel(
        organization_id=org.id,
        user_id=admin_user.id,
        role="admin",
    )
    db_session.add(org_member)
    await db_session.flush()

    return admin_user


@pytest_asyncio.fixture
async def auth_headers_admin(admin_user, token_service) -> dict:
    """Get authentication headers for admin user."""
    token = token_service.create_access_token(str(admin_user.id), admin_user.email.value)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def auth_headers_regular(test_user, token_service) -> dict:
    """Get authentication headers for regular user (non-admin)."""
    token = token_service.create_access_token(str(test_user.id), test_user.email.value)
    return {"Authorization": f"Bearer {token}"}
