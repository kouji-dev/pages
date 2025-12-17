"""Time entry DTOs."""

from datetime import date as DateType
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TimeEntryRequest(BaseModel):
    """Request DTO for creating/updating a time entry."""

    hours: Decimal = Field(..., gt=0, description="Hours worked (must be positive)")
    date: DateType = Field(..., description="Date of the work")
    description: str | None = Field(default=None, description="Optional description")


class TimeEntryResponse(BaseModel):
    """Response DTO for time entry."""

    id: UUID
    issue_id: UUID
    user_id: UUID
    hours: Decimal
    date: DateType
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimeEntryListResponse(BaseModel):
    """Response DTO for time entry list."""

    entries: list[TimeEntryResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimeSummaryResponse(BaseModel):
    """Response DTO for time tracking summary."""

    total_hours: Decimal = Field(..., description="Total hours logged")
    hours_by_user: dict[str, Decimal] = Field(
        default_factory=dict, description="Hours logged by each user (user_id -> hours)"
    )
    hours_by_date_range: dict[str, Decimal] = Field(
        default_factory=dict,
        description="Hours logged by date range (date -> hours)",
    )

    class Config:
        """Pydantic config."""

        from_attributes = True
