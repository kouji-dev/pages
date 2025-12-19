"""Macro domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

# Macro type constants
MACRO_TYPE_TABLE = "table"
MACRO_TYPE_CODE_BLOCK = "code_block"
MACRO_TYPE_INFO_PANEL = "info_panel"
MACRO_TYPE_WARNING_PANEL = "warning_panel"
MACRO_TYPE_ERROR_PANEL = "error_panel"
MACRO_TYPE_PAGE_TREE = "page_tree"
MACRO_TYPE_ISSUE_EMBED = "issue_embed"

# Valid macro types
MACRO_TYPES = {
    MACRO_TYPE_TABLE,
    MACRO_TYPE_CODE_BLOCK,
    MACRO_TYPE_INFO_PANEL,
    MACRO_TYPE_WARNING_PANEL,
    MACRO_TYPE_ERROR_PANEL,
    MACRO_TYPE_PAGE_TREE,
    MACRO_TYPE_ISSUE_EMBED,
}


@dataclass
class Macro:
    """Macro domain entity.

    Represents a reusable content block that can be embedded in pages.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    name: str
    code: str
    config_schema: str | None = None  # JSON schema for macro configuration
    macro_type: str = MACRO_TYPE_INFO_PANEL
    is_system: bool = False  # Whether this is a system macro (cannot be deleted)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate macro entity."""
        if not self.name or not self.name.strip():
            raise ValueError("Macro name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Macro name cannot exceed 100 characters")

        if not self.code or not self.code.strip():
            raise ValueError("Macro code cannot be empty")

        if self.macro_type not in MACRO_TYPES:
            raise ValueError(f"Invalid macro type. Must be one of: {', '.join(MACRO_TYPES)}")

    @classmethod
    def create(
        cls,
        name: str,
        code: str,
        macro_type: str = MACRO_TYPE_INFO_PANEL,
        config_schema: str | None = None,
        is_system: bool = False,
    ) -> Self:
        """Create a new macro.

        Factory method for creating new macros.

        Args:
            name: Macro name (must be unique)
            code: Macro code/implementation
            macro_type: Macro type (table, code_block, info_panel, etc.)
            config_schema: Optional JSON schema for macro configuration
            is_system: Whether this is a system macro

        Returns:
            New Macro instance

        Raises:
            ValueError: If validation fails
        """
        if macro_type not in MACRO_TYPES:
            raise ValueError(f"Invalid macro type. Must be one of: {', '.join(MACRO_TYPES)}")

        return cls(
            id=uuid4(),
            name=name.strip(),
            code=code.strip(),
            macro_type=macro_type,
            config_schema=config_schema,
            is_system=is_system,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update_name(self, name: str) -> None:
        """Update macro name.

        Args:
            name: New macro name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Macro name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Macro name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_code(self, code: str) -> None:
        """Update macro code.

        Args:
            code: New macro code

        Raises:
            ValueError: If code is invalid
        """
        if not code or not code.strip():
            raise ValueError("Macro code cannot be empty")

        self.code = code.strip()
        self._touch()

    def update_config_schema(self, config_schema: str | None) -> None:
        """Update macro configuration schema.

        Args:
            config_schema: New configuration schema (JSON schema)
        """
        self.config_schema = config_schema
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
