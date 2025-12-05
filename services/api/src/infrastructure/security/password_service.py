"""Bcrypt password service implementation."""

import bcrypt

from src.domain.services import PasswordService
from src.domain.value_objects import HashedPassword, Password


class BcryptPasswordService(PasswordService):
    """Password service implementation using bcrypt.

    Uses bcrypt directly for secure password hashing.
    """

    def __init__(self) -> None:
        """Initialize bcrypt service with default rounds."""
        # 12 rounds: good balance between security and performance
        self._rounds = 12

    def hash(self, password: Password) -> HashedPassword:
        """Hash a plain password using bcrypt.

        Args:
            password: Plain password value object

        Returns:
            Hashed password value object
        """
        # Encode password to bytes (bcrypt requires bytes)
        password_bytes = password.value.encode("utf-8")

        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Decode back to string for storage
        return HashedPassword(hashed.decode("utf-8"))

    def verify(self, plain_password: str, hashed_password: HashedPassword) -> bool:
        """Verify a plain password against a bcrypt hash.

        Args:
            plain_password: Plain password string
            hashed_password: Hashed password value object

        Returns:
            True if password matches, False otherwise
        """
        try:
            # Encode both to bytes for comparison
            plain_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.value.encode("utf-8")

            # Use bcrypt.checkpw for constant-time comparison
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except (ValueError, TypeError):
            # Invalid hash format or encoding issue
            return False
