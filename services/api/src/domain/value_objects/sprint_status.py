"""Sprint status value object."""

from enum import Enum


class SprintStatus(str, Enum):
    """Sprint status enumeration.

    Defines the possible states of a sprint.
    """

    PLANNED = "planned"  # Sprint is planned but not yet started
    ACTIVE = "active"  # Sprint is currently active
    COMPLETED = "completed"  # Sprint has been completed

    def __str__(self) -> str:
        """Return the string value of the sprint status."""
        return self.value
