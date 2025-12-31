"""Sprint DTOs."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.value_objects.sprint_status import SprintStatus


class CreateSprintRequest(BaseModel):
    """Request DTO for creating a sprint."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Sprint name",
    )
    goal: str | None = Field(
        None,
        max_length=1000,
        description="Sprint goal",
    )
    start_date: date | None = Field(
        None,
        description="Sprint start date",
    )
    end_date: date | None = Field(
        None,
        description="Sprint end date",
    )
    status: SprintStatus = Field(
        SprintStatus.PLANNED,
        description="Sprint status",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and strip name."""
        return v.strip()

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str | None) -> str | None:
        """Validate and strip goal."""
        if v is None:
            return None
        return v.strip() if v.strip() else None


class UpdateSprintRequest(BaseModel):
    """Request DTO for updating a sprint."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Sprint name",
    )
    goal: str | None = Field(
        None,
        max_length=1000,
        description="Sprint goal",
    )
    start_date: date | None = Field(
        None,
        description="Sprint start date",
    )
    end_date: date | None = Field(
        None,
        description="Sprint end date",
    )
    status: SprintStatus | None = Field(
        None,
        description="Sprint status",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and strip name."""
        if v is None:
            return None
        return v.strip()

    @field_validator("goal")
    @classmethod
    def validate_goal(cls, v: str | None) -> str | None:
        """Validate and strip goal."""
        if v is None:
            return None
        return v.strip() if v.strip() else None


class SprintResponse(BaseModel):
    """Response DTO for sprint data."""

    id: UUID
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus
    total_issues: int = Field(default=0, description="Total number of issues in sprint")
    completed_issues: int = Field(default=0, description="Number of completed issues in sprint")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = False


class SprintListItemResponse(BaseModel):
    """Response DTO for sprint in list view."""

    id: UUID
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus
    total_issues: int = Field(default=0, description="Total number of issues in sprint")
    completed_issues: int = Field(default=0, description="Number of completed issues in sprint")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = False


class SprintListResponse(BaseModel):
    """Response DTO for paginated sprint list."""

    sprints: list[SprintListItemResponse] = Field(..., description="List of sprints")
    total: int = Field(..., description="Total number of sprints")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")


class SprintWithIssuesResponse(BaseModel):
    """Response DTO for sprint with issues."""

    id: UUID
    project_id: UUID
    name: str
    goal: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus
    issues: list[UUID] = Field(..., description="List of issue IDs in the sprint")
    total_issues: int = Field(default=0, description="Total number of issues in sprint")
    completed_issues: int = Field(default=0, description="Number of completed issues in sprint")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        use_enum_values = False


class AddIssueToSprintRequest(BaseModel):
    """Request DTO for adding an issue to a sprint."""

    issue_id: UUID = Field(..., description="Issue UUID to add to sprint")
    order: int = Field(
        default=0,
        ge=0,
        description="Order within the sprint (lower = higher priority)",
    )


class ReorderSprintIssuesRequest(BaseModel):
    """Request DTO for reordering issues in a sprint."""

    issue_orders: dict[str, int] = Field(
        ...,
        description="Dictionary mapping issue IDs (as strings) to their new order",
    )

    @field_validator("issue_orders")
    @classmethod
    def validate_issue_orders(cls, v: dict[str, int]) -> dict[str, int]:
        """Validate issue orders."""
        if not v:
            raise ValueError("issue_orders cannot be empty")
        for order in v.values():
            if order < 0:
                raise ValueError("Order values must be non-negative")
        return v
