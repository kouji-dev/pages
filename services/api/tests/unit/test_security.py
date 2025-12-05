"""Tests for security services."""

import pytest
from uuid import uuid4

from src.domain.exceptions import AuthenticationException
from src.domain.value_objects import Password
from src.infrastructure.security import BcryptPasswordService, JWTTokenService


class TestBcryptPasswordService:
    """Tests for BcryptPasswordService."""

    @pytest.fixture
    def service(self) -> BcryptPasswordService:
        """Get password service."""
        return BcryptPasswordService()

    def test_hash_password(self, service: BcryptPasswordService) -> None:
        """Test password hashing."""
        password = Password("SecurePass123!")
        hashed = service.hash(password)

        assert hashed.value is not None
        assert hashed.value.startswith("$2b$")
        assert hashed.value != password.value

    def test_hash_produces_different_hashes(self, service: BcryptPasswordService) -> None:
        """Test same password produces different hashes (due to salt)."""
        password = Password("SecurePass123!")

        hash1 = service.hash(password)
        hash2 = service.hash(password)

        assert hash1.value != hash2.value

    def test_verify_correct_password(self, service: BcryptPasswordService) -> None:
        """Test verifying correct password."""
        password = Password("SecurePass123!")
        hashed = service.hash(password)

        assert service.verify("SecurePass123!", hashed) is True

    def test_verify_incorrect_password(self, service: BcryptPasswordService) -> None:
        """Test verifying incorrect password."""
        password = Password("SecurePass123!")
        hashed = service.hash(password)

        assert service.verify("WrongPassword123!", hashed) is False

    def test_verify_similar_password(self, service: BcryptPasswordService) -> None:
        """Test similar but different password fails verification."""
        password = Password("SecurePass123!")
        hashed = service.hash(password)

        assert service.verify("SecurePass123", hashed) is False
        assert service.verify("securepass123!", hashed) is False


class TestJWTTokenService:
    """Tests for JWTTokenService."""

    @pytest.fixture
    def service(self) -> JWTTokenService:
        """Get token service."""
        return JWTTokenService()

    def test_create_access_token(self, service: JWTTokenService) -> None:
        """Test creating access token."""
        user_id = uuid4()
        token = service.create_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_claims(self, service: JWTTokenService) -> None:
        """Test creating access token with additional claims."""
        user_id = uuid4()
        token = service.create_access_token(
            user_id,
            additional_claims={"role": "admin"},
        )

        payload = service.verify_token(token)
        assert payload.get("role") == "admin"

    def test_create_refresh_token(self, service: JWTTokenService) -> None:
        """Test creating refresh token."""
        user_id = uuid4()
        token = service.create_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_token(self, service: JWTTokenService) -> None:
        """Test verifying valid token."""
        user_id = uuid4()
        token = service.create_access_token(user_id)

        payload = service.verify_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_verify_invalid_token_raises_error(self, service: JWTTokenService) -> None:
        """Test verifying invalid token raises error."""
        with pytest.raises(AuthenticationException):
            service.verify_token("invalid-token")

    def test_verify_tampered_token_raises_error(self, service: JWTTokenService) -> None:
        """Test verifying tampered token raises error."""
        user_id = uuid4()
        token = service.create_access_token(user_id)

        # Tamper with token
        tampered_token = token[:-5] + "xxxxx"

        with pytest.raises(AuthenticationException):
            service.verify_token(tampered_token)

    def test_get_user_id_from_token(self, service: JWTTokenService) -> None:
        """Test extracting user ID from token."""
        user_id = uuid4()
        token = service.create_access_token(user_id)

        extracted_id = service.get_user_id_from_token(token)

        assert extracted_id == user_id

    def test_create_password_reset_token(self, service: JWTTokenService) -> None:
        """Test creating password reset token."""
        user_id = uuid4()
        token = service.create_password_reset_token(user_id)

        assert token is not None

        payload = service.verify_token(token)
        assert payload["type"] == "password_reset"

    def test_verify_password_reset_token(self, service: JWTTokenService) -> None:
        """Test verifying password reset token."""
        user_id = uuid4()
        token = service.create_password_reset_token(user_id)

        extracted_id = service.verify_password_reset_token(token)

        assert extracted_id == user_id

    def test_verify_password_reset_token_wrong_type(self, service: JWTTokenService) -> None:
        """Test verifying access token as password reset token fails."""
        user_id = uuid4()
        access_token = service.create_access_token(user_id)

        with pytest.raises(AuthenticationException) as exc_info:
            service.verify_password_reset_token(access_token)

        assert "password reset" in str(exc_info.value).lower()

    def test_access_token_expire_minutes_property(self, service: JWTTokenService) -> None:
        """Test access_token_expire_minutes property."""
        assert service.access_token_expire_minutes > 0
        assert isinstance(service.access_token_expire_minutes, int)
