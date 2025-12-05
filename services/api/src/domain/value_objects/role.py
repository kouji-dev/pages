"""Role value object for permissions system."""

from enum import Enum


class Role(str, Enum):
    """User role enumeration.

    Defines the base roles used across the system:
    - admin: Full access (manage members, settings, delete)
    - member: Standard access (create, edit, participate)
    - viewer: Read-only access (view only)
    """

    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

    def __str__(self) -> str:
        """Return role as string."""
        return self.value

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a string value is a valid role."""
        try:
            cls(value)
            return True
        except ValueError:
            return False

    def can_manage_members(self) -> bool:
        """Check if role can manage members."""
        return self == Role.ADMIN

    def can_edit_content(self) -> bool:
        """Check if role can edit content."""
        return self in (Role.ADMIN, Role.MEMBER)

    def can_view(self) -> bool:
        """Check if role can view content."""
        return True  # All roles can view

    def can_delete(self) -> bool:
        """Check if role can delete content."""
        return self == Role.ADMIN
