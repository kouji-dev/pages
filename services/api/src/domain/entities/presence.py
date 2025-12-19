"""Presence domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4


@dataclass
class Presence:
    """Presence domain entity.

    Represents a user's presence on a page for real-time collaboration.
    """

    id: UUID
    page_id: UUID
    user_id: UUID
    cursor_position: str | None = None  # JSON cursor position data
    selection: str | None = None  # JSON selection data
    socket_id: str | None = None  # WebSocket connection ID
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        page_id: UUID,
        user_id: UUID,
        cursor_position: str | None = None,
        selection: str | None = None,
        socket_id: str | None = None,
    ) -> Self:
        """Create a new presence.

        Factory method for creating new presences.

        Args:
            page_id: ID of the page
            user_id: ID of the user
            cursor_position: Optional JSON cursor position data
            selection: Optional JSON selection data
            socket_id: Optional WebSocket connection ID

        Returns:
            New Presence instance
        """
        return cls(
            id=uuid4(),
            page_id=page_id,
            user_id=user_id,
            cursor_position=cursor_position,
            selection=selection,
            socket_id=socket_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update_cursor(self, cursor_position: str | None) -> None:
        """Update cursor position.

        Args:
            cursor_position: New cursor position (JSON)
        """
        self.cursor_position = cursor_position
        self._touch()

    def update_selection(self, selection: str | None) -> None:
        """Update selection.

        Args:
            selection: New selection (JSON)
        """
        self.selection = selection
        self._touch()

    def update_socket_id(self, socket_id: str | None) -> None:
        """Update socket ID.

        Args:
            socket_id: New socket ID
        """
        self.socket_id = socket_id
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
