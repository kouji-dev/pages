"""Custom field domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID, uuid4


@dataclass
class CustomFieldValue:
    """Custom field value entity.

    Represents a value for a custom field on an issue.
    """

    id: UUID
    custom_field_id: UUID
    issue_id: UUID
    value: Any  # Can be str, int, float, date, list, etc. depending on field type
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate custom field value."""
        # Validation is done at the CustomField level based on field type
        pass

    @classmethod
    def create(
        cls,
        custom_field_id: UUID,
        issue_id: UUID,
        value: Any,
    ) -> Self:
        """Create a new custom field value.

        Args:
            custom_field_id: ID of the custom field
            issue_id: ID of the issue
            value: Field value

        Returns:
            New CustomFieldValue instance
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            custom_field_id=custom_field_id,
            issue_id=issue_id,
            value=value,
            created_at=now,
            updated_at=now,
        )

    def update_value(self, value: Any) -> None:
        """Update field value.

        Args:
            value: New field value
        """
        self.value = value
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


@dataclass
class CustomField:
    """Custom field domain entity.

    Represents a custom field definition for a project.
    This is an aggregate root in DDD terms.
    """

    id: UUID
    project_id: UUID
    name: str
    type: str  # text, number, date, select, multi_select, user, users
    is_required: bool = False
    default_value: Any | None = None
    options: list[str] | None = None  # For select/multi_select types
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    VALID_TYPES = {
        "text",
        "number",
        "date",
        "select",
        "multi_select",
        "user",
        "users",
    }

    def __post_init__(self) -> None:
        """Validate custom field."""
        if not self.name or not self.name.strip():
            raise ValueError("Custom field name cannot be empty")

        self.name = self.name.strip()

        if len(self.name) > 100:
            raise ValueError("Custom field name cannot exceed 100 characters")

        if self.type not in self.VALID_TYPES:
            raise ValueError(f"Custom field type must be one of: {', '.join(self.VALID_TYPES)}")

        # Validate options for select types
        if self.type in {"select", "multi_select"}:
            if not self.options or len(self.options) == 0:
                raise ValueError(f"Custom field type '{self.type}' requires at least one option")

    @classmethod
    def create(
        cls,
        project_id: UUID,
        name: str,
        type: str,
        is_required: bool = False,
        default_value: Any | None = None,
        options: list[str] | None = None,
    ) -> Self:
        """Create a new custom field.

        Factory method for creating new custom fields.

        Args:
            project_id: ID of the project this field belongs to
            name: Field name
            type: Field type (text, number, date, select, multi_select, user, users)
            is_required: Whether the field is required
            default_value: Default value for the field
            options: Options for select/multi_select types

        Returns:
            New CustomField instance

        Raises:
            ValueError: If field data is invalid
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            project_id=project_id,
            name=name,
            type=type,
            is_required=is_required,
            default_value=default_value,
            options=options,
            created_at=now,
            updated_at=now,
        )

    def update_name(self, name: str) -> None:
        """Update field name.

        Args:
            name: New field name

        Raises:
            ValueError: If name is invalid
        """
        if not name or not name.strip():
            raise ValueError("Custom field name cannot be empty")

        name = name.strip()

        if len(name) > 100:
            raise ValueError("Custom field name cannot exceed 100 characters")

        self.name = name
        self._touch()

    def update_options(self, options: list[str] | None) -> None:
        """Update field options.

        Args:
            options: New options list

        Raises:
            ValueError: If options are invalid for field type
        """
        if self.type in {"select", "multi_select"}:
            if not options or len(options) == 0:
                raise ValueError(f"Custom field type '{self.type}' requires at least one option")

        self.options = options
        self._touch()

    def validate_value(self, value: Any) -> None:
        """Validate a value against this field's type and constraints.

        Args:
            value: Value to validate

        Raises:
            ValueError: If value is invalid
        """
        if value is None:
            if self.is_required:
                raise ValueError(f"Custom field '{self.name}' is required")
            return

        if self.type == "text":
            if not isinstance(value, str):
                raise ValueError(f"Custom field '{self.name}' must be a string")
        elif self.type == "number":
            if not isinstance(value, int | float):
                raise ValueError(f"Custom field '{self.name}' must be a number")
        elif self.type == "date":
            if not isinstance(value, str | datetime):
                raise ValueError(f"Custom field '{self.name}' must be a date")
        elif self.type == "select":
            if not isinstance(value, str):
                raise ValueError(f"Custom field '{self.name}' must be a string")
            if self.options and value not in self.options:
                raise ValueError(
                    f"Custom field '{self.name}' value must be one of: {', '.join(self.options)}"
                )
        elif self.type == "multi_select":
            if not isinstance(value, list):
                raise ValueError(f"Custom field '{self.name}' must be a list")
            if self.options:
                invalid_values = [v for v in value if v not in self.options]
                if invalid_values:
                    raise ValueError(
                        f"Custom field '{self.name}' contains invalid values: {', '.join(invalid_values)}"
                    )
        elif self.type == "user":
            if not isinstance(value, str):  # UUID as string
                raise ValueError(f"Custom field '{self.name}' must be a user ID (string)")
        elif self.type == "users":
            if not isinstance(value, list):
                raise ValueError(f"Custom field '{self.name}' must be a list of user IDs")
            if not all(isinstance(v, str) for v in value):
                raise ValueError(f"Custom field '{self.name}' must contain only user IDs (strings)")

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
