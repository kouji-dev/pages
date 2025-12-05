"""Token service interface."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID


class TokenService(ABC):
    """Abstract token service interface.
    
    This is a port for JWT token operations.
    Implementation will be in infrastructure layer.
    """

    @abstractmethod
    def create_access_token(
        self,
        user_id: UUID,
        additional_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create an access token for a user.
        
        Args:
            user_id: User UUID
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT access token string
        """
        ...

    @abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a refresh token for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            JWT refresh token string
        """
        ...

    @abstractmethod
    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify and decode a token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload as dictionary
            
        Raises:
            AuthenticationException: If token is invalid or expired
        """
        ...

    @abstractmethod
    def get_user_id_from_token(self, token: str) -> UUID:
        """Extract user ID from token.
        
        Args:
            token: JWT token string
            
        Returns:
            User UUID
            
        Raises:
            AuthenticationException: If token is invalid
        """
        ...

    @abstractmethod
    def create_password_reset_token(self, user_id: UUID) -> str:
        """Create a password reset token.
        
        Args:
            user_id: User UUID
            
        Returns:
            Password reset token string
        """
        ...

    @abstractmethod
    def verify_password_reset_token(self, token: str) -> UUID:
        """Verify password reset token and get user ID.
        
        Args:
            token: Password reset token
            
        Returns:
            User UUID
            
        Raises:
            AuthenticationException: If token is invalid or expired
        """
        ...

    @property
    @abstractmethod
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes."""
        ...

