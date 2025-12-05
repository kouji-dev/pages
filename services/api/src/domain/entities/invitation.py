"""Organization invitation domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Self
from uuid import UUID, uuid4

from src.domain.value_objects import Email


@dataclass
class Invitation:
    """Organization invitation domain entity.

    Represents an invitation sent to a user to join an organization.
    """

    id: UUID
    organization_id: UUID
    email: Email
    token: str
    role: str
    invited_by: UUID
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        """Validate invitation entity."""
        if not self.token or not self.token.strip():
            raise ValueError("Invitation token cannot be empty")

        self.token = self.token.strip()

        if len(self.token) > 255:
            raise ValueError("Invitation token cannot exceed 255 characters")

        # Validate role
        valid_roles = ["admin", "member", "viewer"]
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role: {self.role}. Must be one of: {', '.join(valid_roles)}")

        # Note: expiration validation is only done in create() method
        # This allows loading expired invitations from database

    @classmethod
    def create(
        cls,
        organization_id: UUID,
        email: Email,
        token: str,
        role: str,
        invited_by: UUID,
        expires_in_days: int = 7,
    ) -> Self:
        """Create a new invitation.

        Factory method for creating new invitations with proper defaults.

        Args:
            organization_id: Organization ID
            email: Invited user email
            token: Unique invitation token
            role: Role to assign when invitation is accepted (admin, member, viewer)
            invited_by: User ID who sent the invitation
            expires_in_days: Number of days until invitation expires (default: 7)

        Returns:
            New Invitation instance

        Raises:
            ValueError: If any parameter is invalid
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(days=expires_in_days)

        # Validate expiration is in the future
        if expires_at <= now:
            raise ValueError("Invitation expiration must be in the future")

        return cls(
            id=uuid4(),
            organization_id=organization_id,
            email=email,
            token=token,
            role=role,
            invited_by=invited_by,
            expires_at=expires_at,
            accepted_at=None,
            created_at=now,
            updated_at=now,
        )

    def is_expired(self) -> bool:
        """Check if invitation has expired.

        Returns:
            True if invitation is expired, False otherwise
        """
        return datetime.now(UTC) > self.expires_at

    def is_accepted(self) -> bool:
        """Check if invitation has been accepted.

        Returns:
            True if invitation is accepted, False otherwise
        """
        return self.accepted_at is not None

    def is_valid(self) -> bool:
        """Check if invitation is valid (not expired and not accepted).

        Returns:
            True if invitation is valid, False otherwise
        """
        return not self.is_expired() and not self.is_accepted()

    def accept(self) -> None:
        """Mark invitation as accepted.

        Raises:
            ValueError: If invitation is already accepted or expired
        """
        if self.is_accepted():
            raise ValueError("Invitation is already accepted")

        if self.is_expired():
            raise ValueError("Cannot accept expired invitation")

        self.accepted_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
