"""Sprint metrics DTOs."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class BurndownDataPoint(BaseModel):
    """Data point for burndown chart."""

    point_date: date = Field(..., description="Date of the data point", alias="date")
    ideal: float = Field(..., description="Ideal remaining story points")
    actual: float = Field(..., description="Actual remaining story points")

    model_config = {"populate_by_name": True}


class SprintMetricsResponse(BaseModel):
    """Response DTO for sprint metrics."""

    sprint_id: UUID
    total_story_points: int = Field(..., description="Total story points in sprint")
    completed_story_points: int = Field(..., description="Completed story points in sprint")
    remaining_story_points: int = Field(..., description="Remaining story points in sprint")
    completion_percentage: float = Field(..., description="Completion percentage (0-100)")
    velocity: float = Field(..., description="Sprint velocity (completed story points)")
    issue_counts: dict[str, int] = Field(..., description="Issue counts by status")
    burndown_data: list[BurndownDataPoint] = Field(
        default_factory=list, description="Burndown chart data points"
    )


class CompleteSprintRequest(BaseModel):
    """Request DTO for completing a sprint."""

    move_incomplete_to_backlog: bool = Field(
        default=True,
        description="Whether to move incomplete issues to backlog",
    )


class CompleteSprintResponse(BaseModel):
    """Response DTO for sprint completion."""

    sprint_id: UUID
    message: str = Field(default="Sprint completed successfully")
    incomplete_issues_moved: int = Field(
        default=0, description="Number of incomplete issues moved to backlog"
    )
    metrics: SprintMetricsResponse = Field(..., description="Final sprint metrics")
