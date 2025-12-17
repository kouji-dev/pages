"""Time entry domain entity."""

from dataclasses import dataclass, field
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID, uuid4


@dataclass
class TimeEntry:
    """Time entry domain entity.

    Represents time logged on an issue.
    """

    id: UUID
    issue_id: UUID
    user_id: UUID
    hours: Decimal
    date: date_type
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate time entry."""
        if self.hours <= 0:
            raise ValueError("Hours must be positive")

    @classmethod
    def create(
        cls,
        issue_id: UUID,
        user_id: UUID,
        hours: Decimal | float | int,
        date: date_type,
        description: str | None = None,
    ) -> Self:
        """Create a new time entry.

        Args:
            issue_id: Issue ID
            user_id: User ID who logged the time
            hours: Hours worked (must be positive)
            date: Date of the work
            description: Optional description

        Returns:
            New TimeEntry instance

        Raises:
            ValueError: If hours is invalid
        """
        hours_decimal = Decimal(str(hours))
        if hours_decimal <= 0:
            raise ValueError("Hours must be positive")

        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            issue_id=issue_id,
            user_id=user_id,
            hours=hours_decimal,
            date=date,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def update_hours(self, hours: Decimal | float | int) -> None:
        """Update hours.

        Args:
            hours: New hours value

        Raises:
            ValueError: If hours is invalid
        """
        hours_decimal = Decimal(str(hours))
        if hours_decimal <= 0:
            raise ValueError("Hours must be positive")

        self.hours = hours_decimal
        self._touch()

    def update_date(self, date: date_type) -> None:
        """Update date.

        Args:
            date: New date
        """
        self.date = date
        self._touch()

    def update_description(self, description: str | None) -> None:
        """Update description.

        Args:
            description: New description
        """
        self.description = description
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
