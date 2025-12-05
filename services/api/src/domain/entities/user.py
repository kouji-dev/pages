"""User domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from src.domain.value_objects import Email, HashedPassword


@dataclass
class User:
    """User domain entity.

    Represents a user in the system with their core attributes.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    email: Email
    password_hash: HashedPassword
    name: str
    avatar_url: str | None = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate user entity."""
        if not self.name or not self.name.strip():
            raise ValueError("User name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("User name cannot exceed 100 characters")

    @classmethod
    def create(
        cls,
        email: Email,
        password_hash: HashedPassword,
        name: str,
        avatar_url: str | None = None,
    ) -> Self:
        """Create a new user.

        Factory method for creating new users with proper defaults.
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            name=name,
            avatar_url=avatar_url,
            is_active=True,
            is_verified=False,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    def update_name(self, name: str) -> None:
        """Update user name."""
        if not name or not name.strip():
            raise ValueError("User name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("User name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_avatar(self, avatar_url: str | None) -> None:
        """Update user avatar URL."""
        self.avatar_url = avatar_url
        self._touch()

    def update_password(self, password_hash: HashedPassword) -> None:
        """Update user password hash."""
        self.password_hash = password_hash
        self._touch()

    def verify(self) -> None:
        """Mark user as verified."""
        self.is_verified = True
        self._touch()

    def deactivate(self) -> None:
        """Soft delete the user."""
        if self.deleted_at is not None:
            return  # Already deactivated

        self.is_active = False
        self.deleted_at = datetime.utcnow()
        self._touch()

    def reactivate(self) -> None:
        """Reactivate a deactivated user."""
        self.is_active = True
        self.deleted_at = None
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    @property
    def is_deleted(self) -> bool:
        """Check if user is soft deleted."""
        return self.deleted_at is not None

    def __eq__(self, other: object) -> bool:
        """Compare users by ID."""
        if isinstance(other, User):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """Hash user by ID."""
        return hash(self.id)
