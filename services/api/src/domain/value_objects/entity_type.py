"""Entity type value object for favorites."""

from dataclasses import dataclass

from src.domain.exceptions import ValidationException


@dataclass(frozen=True, slots=True)
class EntityType:
    """Entity type value object with validation.

    Immutable value object that validates entity type for favorites.
    Represents the type of entity that can be favorited (project, space, page).
    """

    value: str

    # Allowed entity types
    PROJECT = "project"
    SPACE = "space"
    PAGE = "page"

    # Set of valid entity types
    VALID_TYPES = {PROJECT, SPACE, PAGE}

    def __post_init__(self) -> None:
        """Validate entity type on creation."""
        if not self.value:
            raise ValidationException("Entity type cannot be empty", field="entity_type")

        normalized = self.value.lower().strip()

        if normalized not in self.VALID_TYPES:
            raise ValidationException(
                f"Invalid entity type: {self.value}. "
                f"Valid types are: {', '.join(sorted(self.VALID_TYPES))}",
                field="entity_type",
            )

        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        """Return entity type as string."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare entity types."""
        if isinstance(other, EntityType):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other.lower()
        return False

    def __hash__(self) -> int:
        """Hash entity type."""
        return hash(self.value)

    @classmethod
    def from_string(cls, value: str | None) -> "EntityType":
        """Create EntityType from string.

        Args:
            value: Entity type string

        Returns:
            EntityType instance

        Raises:
            ValidationException: If value is invalid
        """
        if value is None:
            raise ValidationException("Entity type cannot be None", field="entity_type")
        return cls(value)

    @classmethod
    def project(cls) -> "EntityType":
        """Create EntityType for project.

        Returns:
            EntityType instance for project
        """
        return cls(cls.PROJECT)

    @classmethod
    def space(cls) -> "EntityType":
        """Create EntityType for space.

        Returns:
            EntityType instance for space
        """
        return cls(cls.SPACE)

    @classmethod
    def page(cls) -> "EntityType":
        """Create EntityType for page.

        Returns:
            EntityType instance for page
        """
        return cls(cls.PAGE)

    def is_project(self) -> bool:
        """Check if entity type is project.

        Returns:
            True if project, False otherwise
        """
        return self.value == self.PROJECT

    def is_space(self) -> bool:
        """Check if entity type is space.

        Returns:
            True if space, False otherwise
        """
        return self.value == self.SPACE

    def is_page(self) -> bool:
        """Check if entity type is page.

        Returns:
            True if page, False otherwise
        """
        return self.value == self.PAGE

