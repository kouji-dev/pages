"""Board and BoardList domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


@dataclass
class BoardList:
    """Board list (column) value object / entity.

    Represents a column on a board with type (label, assignee, milestone)
    and optional config (e.g. label_id, user_id, sprint_id).
    """

    id: UUID
    board_id: UUID
    list_type: str
    list_config: dict[str, Any] | None = None
    position: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate list type."""
        allowed = ("label", "assignee", "milestone")
        if self.list_type not in allowed:
            raise ValueError(f"list_type must be one of {allowed}")
        if self.position < 0:
            raise ValueError("Board list position must be non-negative")

    @classmethod
    def create(
        cls,
        board_id: UUID,
        list_type: str,
        list_config: dict[str, Any] | None = None,
        position: int = 0,
    ) -> Self:
        """Create a new board list."""
        allowed = ("label", "assignee", "milestone")
        if list_type not in allowed:
            raise ValueError(f"list_type must be one of {allowed}")
        if position < 0:
            raise ValueError("Board list position must be non-negative")
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            board_id=board_id,
            list_type=list_type,
            list_config=list_config or None,
            position=position,
            created_at=now,
            updated_at=now,
        )

    def update_position(self, position: int) -> None:
        """Update list position."""
        if position < 0:
            raise ValueError("Board list position must be non-negative")
        self.position = position
        self._touch()

    def update_list_config(self, list_config: dict[str, Any] | None) -> None:
        """Update list config."""
        self.list_config = list_config
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass
class Board:
    """Board domain entity.

    Boards belong to a project and define a view with configurable
    columns (lists) and optional scope.
    """

    id: UUID
    project_id: UUID
    name: str
    description: str | None = None
    scope_config: dict[str, Any] | None = None
    is_default: bool = False
    position: int = 0
    created_by: UUID | None = None
    organization_id: UUID | None = None
    board_type: str = "project"  # 'project' or 'group'
    swimlane_type: str = "none"  # 'none', 'epic', 'assignee'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate board entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Board name cannot be empty")
        self.name = self.name.strip()
        if len(self.name) > 255:
            raise ValueError("Board name cannot exceed 255 characters")
        if self.description is not None and len(self.description) > 65535:
            raise ValueError("Board description too long")
        if self.position < 0:
            raise ValueError("Board position must be non-negative")
        if self.board_type not in {"project", "group"}:
            raise ValueError("Board type must be 'project' or 'group'")
        if self.swimlane_type not in {"none", "epic", "assignee"}:
            raise ValueError("swimlane_type must be 'none', 'epic', or 'assignee'")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        name: str,
        description: str | None = None,
        scope_config: dict[str, Any] | None = None,
        is_default: bool = False,
        position: int = 0,
        created_by: UUID | None = None,
    ) -> Self:
        """Create a new board."""
        now = datetime.utcnow()
        name = name.strip() if name else ""
        if not name:
            raise ValueError("Board name cannot be empty")
        if len(name) > 255:
            raise ValueError("Board name cannot exceed 255 characters")
        return cls(
            id=uuid4(),
            project_id=project_id,
            name=name,
            description=description,
            scope_config=scope_config,
            is_default=is_default,
            position=position,
            created_by=created_by,
            organization_id=None,
            board_type="project",
            swimlane_type="none",
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_group(
        cls,
        organization_id: UUID,
        primary_project_id: UUID,
        name: str,
        description: str | None = None,
        scope_config: dict[str, Any] | None = None,
        is_default: bool = False,
        position: int = 0,
        created_by: UUID | None = None,
    ) -> Self:
        """Create a new group board attached to an organization and multiple projects.

        primary_project_id is the project used as the primary/anchor project for the board
        while the full list of projects is managed via the GroupBoardProjects mapping.
        """
        now = datetime.utcnow()
        name = name.strip() if name else ""
        if not name:
            raise ValueError("Board name cannot be empty")
        if len(name) > 255:
            raise ValueError("Board name cannot exceed 255 characters")
        return cls(
            id=uuid4(),
            project_id=primary_project_id,
            name=name,
            description=description,
            scope_config=scope_config,
            is_default=is_default,
            position=position,
            created_by=created_by,
            organization_id=organization_id,
            board_type="group",
            swimlane_type="none",
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str) -> None:
        """Update board name."""
        if not name or not name.strip():
            raise ValueError("Board name cannot be empty")
        name = name.strip()
        if len(name) > 255:
            raise ValueError("Board name cannot exceed 255 characters")
        self.name = name
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update board description."""
        self.description = description
        self._touch()

    def update_scope_config(self, scope_config: dict[str, Any] | None) -> None:
        """Update board scope configuration."""
        self.scope_config = scope_config
        self._touch()

    def update_position(self, position: int) -> None:
        """Update board position."""
        if position < 0:
            raise ValueError("Board position must be non-negative")
        self.position = position
        self._touch()

    def update_swimlane_type(self, swimlane_type: str) -> None:
        """Update board swimlane type ('none', 'epic', 'assignee')."""
        if swimlane_type not in {"none", "epic", "assignee"}:
            raise ValueError("swimlane_type must be 'none', 'epic', or 'assignee'")
        self.swimlane_type = swimlane_type
        self._touch()

    def set_default(self, is_default: bool) -> None:
        """Set or unset as default board."""
        self.is_default = is_default
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
