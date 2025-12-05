"""User repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import User
from src.domain.value_objects import Email


class UserRepository(ABC):
    """Abstract user repository interface.
    
    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user.
        
        Args:
            user: User entity to create
            
        Returns:
            Created user with persisted data
            
        Raises:
            ConflictException: If email already exists
        """
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user.
        
        Args:
            user: User entity with updated data
            
        Returns:
            Updated user
            
        Raises:
            EntityNotFoundException: If user not found
        """
        ...

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        """Hard delete a user.
        
        Args:
            user_id: User UUID
            
        Raises:
            EntityNotFoundException: If user not found
        """
        ...

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if user with email exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if user exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[User]:
        """Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted users
            
        Returns:
            List of users
        """
        ...

    @abstractmethod
    async def count(self, include_deleted: bool = False) -> int:
        """Count total users.
        
        Args:
            include_deleted: Whether to include soft-deleted users
            
        Returns:
            Total count of users
        """
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[User]:
        """Search users by name or email.
        
        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        ...

