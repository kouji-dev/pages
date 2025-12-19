"""Page and space permission domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

# Permission role constants (more granular than organization roles)
PERMISSION_ROLE_READ = "read"
PERMISSION_ROLE_EDIT = "edit"
PERMISSION_ROLE_DELETE = "delete"
PERMISSION_ROLE_ADMIN = "admin"
PERMISSION_ROLE_VIEW = "view"
PERMISSION_ROLE_CREATE = "create"

# Valid permission roles
PAGE_PERMISSION_ROLES = {
    PERMISSION_ROLE_READ,
    PERMISSION_ROLE_EDIT,
    PERMISSION_ROLE_DELETE,
    PERMISSION_ROLE_ADMIN,
}
SPACE_PERMISSION_ROLES = {
    PERMISSION_ROLE_VIEW,
    PERMISSION_ROLE_CREATE,
    PERMISSION_ROLE_EDIT,
    PERMISSION_ROLE_DELETE,
    PERMISSION_ROLE_ADMIN,
}


@dataclass
class PagePermission:
    """Page permission domain entity.

    Represents a user's permission on a specific page.
    """

    id: UUID
    page_id: UUID
    user_id: UUID | None
    role: str
    inherited_from_space: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate page permission entity."""
        if self.role not in PAGE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid page permission role. Must be one of: {', '.join(PAGE_PERMISSION_ROLES)}"
            )

    @classmethod
    def create(
        cls,
        page_id: UUID,
        user_id: UUID | None,
        role: str,
        inherited_from_space: bool = False,
    ) -> Self:
        """Create a new page permission.

        Factory method for creating new page permissions.

        Args:
            page_id: ID of the page
            user_id: ID of the user (None for public permissions)
            role: Permission role (read, edit, delete, admin)
            inherited_from_space: Whether this permission is inherited from space

        Returns:
            New PagePermission instance

        Raises:
            ValueError: If validation fails
        """
        if role not in PAGE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid page permission role. Must be one of: {', '.join(PAGE_PERMISSION_ROLES)}"
            )

        return cls(
            id=uuid4(),
            page_id=page_id,
            user_id=user_id,
            role=role,
            inherited_from_space=inherited_from_space,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update_role(self, role: str) -> None:
        """Update permission role.

        Args:
            role: New permission role

        Raises:
            ValueError: If role is invalid
        """
        if role not in PAGE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid page permission role. Must be one of: {', '.join(PAGE_PERMISSION_ROLES)}"
            )
        self.role = role
        self.updated_at = datetime.utcnow()


@dataclass
class SpacePermission:
    """Space permission domain entity.

    Represents a user's permission on a specific space.
    """

    id: UUID
    space_id: UUID
    user_id: UUID | None
    role: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate space permission entity."""
        if self.role not in SPACE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid space permission role. Must be one of: {', '.join(SPACE_PERMISSION_ROLES)}"
            )

    @classmethod
    def create(
        cls,
        space_id: UUID,
        user_id: UUID | None,
        role: str,
    ) -> Self:
        """Create a new space permission.

        Factory method for creating new space permissions.

        Args:
            space_id: ID of the space
            user_id: ID of the user (None for public permissions)
            role: Permission role (view, create, edit, delete, admin)

        Returns:
            New SpacePermission instance

        Raises:
            ValueError: If validation fails
        """
        if role not in SPACE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid space permission role. Must be one of: {', '.join(SPACE_PERMISSION_ROLES)}"
            )

        return cls(
            id=uuid4(),
            space_id=space_id,
            user_id=user_id,
            role=role,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update_role(self, role: str) -> None:
        """Update permission role.

        Args:
            role: New permission role

        Raises:
            ValueError: If role is invalid
        """
        if role not in SPACE_PERMISSION_ROLES:
            raise ValueError(
                f"Invalid space permission role. Must be one of: {', '.join(SPACE_PERMISSION_ROLES)}"
            )
        self.role = role
        self.updated_at = datetime.utcnow()
