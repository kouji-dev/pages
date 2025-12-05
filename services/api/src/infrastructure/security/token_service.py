"""JWT token service implementation."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from src.application.interfaces import TokenService
from src.domain.exceptions import AuthenticationException
from src.infrastructure.config import get_settings


class JWTTokenService(TokenService):
    """Token service implementation using python-jose (JWT)."""

    def __init__(self) -> None:
        """Initialize JWT service with settings."""
        settings = get_settings()
        self._secret_key = settings.jwt_secret_key
        self._algorithm = settings.jwt_algorithm
        self._access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self._refresh_token_expire_days = settings.jwt_refresh_token_expire_days
        self._password_reset_expire_hours = 24  # 24 hours for password reset

    def create_access_token(
        self,
        user_id: UUID,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create an access token for a user.

        Args:
            user_id: User UUID
            additional_claims: Additional claims to include

        Returns:
            JWT access token string
        """
        expire = datetime.now(UTC) + timedelta(minutes=self._access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.now(UTC),
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a refresh token for a user.

        Args:
            user_id: User UUID

        Returns:
            JWT refresh token string
        """
        expire = datetime.now(UTC) + timedelta(days=self._refresh_token_expire_days)

        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(UTC),
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode a token.

        Args:
            token: JWT token string

        Returns:
            Token payload as dictionary

        Raises:
            AuthenticationException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except JWTError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}") from e

    def get_user_id_from_token(self, token: str) -> UUID:
        """Extract user ID from token.

        Args:
            token: JWT token string

        Returns:
            User UUID

        Raises:
            AuthenticationException: If token is invalid
        """
        payload = self.verify_token(token)

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException("Invalid token: missing subject")

        try:
            return UUID(user_id_str)
        except ValueError as e:
            raise AuthenticationException("Invalid token: invalid user ID format") from e

    def create_password_reset_token(self, user_id: UUID) -> str:
        """Create a password reset token.

        Args:
            user_id: User UUID

        Returns:
            Password reset token string
        """
        expire = datetime.now(UTC) + timedelta(hours=self._password_reset_expire_hours)

        payload = {
            "sub": str(user_id),
            "type": "password_reset",
            "exp": expire,
            "iat": datetime.now(UTC),
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify_password_reset_token(self, token: str) -> UUID:
        """Verify password reset token and get user ID.

        Args:
            token: Password reset token

        Returns:
            User UUID

        Raises:
            AuthenticationException: If token is invalid or expired
        """
        payload = self.verify_token(token)

        token_type = payload.get("type")
        if token_type != "password_reset":
            raise AuthenticationException("Invalid password reset token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationException("Invalid token: missing subject")

        try:
            return UUID(user_id_str)
        except ValueError as e:
            raise AuthenticationException("Invalid token: invalid user ID format") from e

    @property
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes."""
        return self._access_token_expire_minutes
