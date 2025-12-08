"""Test script to debug login issue."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.application.dtos.auth import LoginRequest
from src.application.use_cases.auth.auth import LoginUserUseCase
from src.domain.value_objects import Email
from src.infrastructure.config import get_settings
from src.infrastructure.database import get_session_context
from src.infrastructure.database.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.security import BcryptPasswordService
from src.infrastructure.security.token_service import JWTTokenService


async def test_login() -> None:
    """Test login flow."""
    print("🔍 Testing login flow...")

    settings = get_settings()
    print("📋 Settings:")
    print(f"   - Environment: {settings.environment}")
    print(f"   - Debug: {settings.debug}")
    print(f"   - Database: {settings.database_url}")
    print()

    async with get_session_context() as session:
        # Initialize services
        user_repository = SQLAlchemyUserRepository(session)
        password_service = BcryptPasswordService()
        token_service = JWTTokenService()

        # Create use case
        use_case = LoginUserUseCase(
            user_repository=user_repository,
            password_service=password_service,
            token_service=token_service,
        )

        # Test 1: Check if user exists
        print("1️⃣ Checking if user exists...")
        email = Email("admin@pages.dev")
        user = await user_repository.get_by_email(email)

        if user is None:
            print("   ❌ User not found!")
            return
        else:
            print(f"   ✅ User found: {user.email}")
            print(f"   - ID: {user.id}")
            print(f"   - Name: {user.name}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Verified: {user.is_verified}")
            print(f"   - Password hash type: {type(user.password_hash)}")
            print(f"   - Password hash value type: {type(user.password_hash.value)}")
            print(f"   - Password hash length: {len(user.password_hash.value)}")
            print()

        # Test 2: Test password verification directly
        print("2️⃣ Testing password verification...")
        test_password = "TestPass123!"
        print(f"   - Test password: {test_password}")
        print(f"   - Password type: {type(test_password)}")

        try:
            is_valid = password_service.verify(test_password, user.password_hash)
            print(f"   ✅ Password verification result: {is_valid}")
        except Exception as e:
            print(f"   ❌ Password verification failed: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            return
        print()

        # Test 3: Test full login use case
        print("3️⃣ Testing full login use case...")
        login_request = LoginRequest(
            email="admin@pages.dev",
            password="TestPass123!",
        )

        try:
            response = await use_case.execute(login_request)
            print("   ✅ Login successful!")
            print(f"   - Access token: {response.access_token[:50]}...")
            print(f"   - Refresh token: {response.refresh_token[:50]}...")
            print(f"   - User: {response.user.email}")
        except Exception as e:
            print(f"   ❌ Login failed: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_login())
