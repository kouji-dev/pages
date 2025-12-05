"""Password service interface."""

from abc import ABC, abstractmethod

from src.domain.value_objects import HashedPassword, Password


class PasswordService(ABC):
    """Abstract password service interface.
    
    This is a port for password operations.
    Implementation will be in infrastructure layer using bcrypt/argon2.
    """

    @abstractmethod
    def hash(self, password: Password) -> HashedPassword:
        """Hash a plain password.
        
        Args:
            password: Plain password value object
            
        Returns:
            Hashed password value object
        """
        ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: HashedPassword) -> bool:
        """Verify a plain password against a hash.
        
        Args:
            plain_password: Plain password string
            hashed_password: Hashed password value object
            
        Returns:
            True if password matches, False otherwise
        """
        ...

