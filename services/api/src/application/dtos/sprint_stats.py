"""Sprint stats DTOs."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class BurndownStatsResponse(BaseModel):
    """Response DTO for sprint burndown stats."""

    sprint_id: UUID
    burndown_data: list[dict[str, float | str]] = Field(
        ..., description="Burndown chart data points with date, ideal, and actual"
    )


class IssueStatsResponse(BaseModel):
    """Response DTO for sprint issue stats."""

    sprint_id: UUID
    total_issues: int = Field(..., description="Total number of issues in sprint")
    completed_issues: int = Field(..., description="Number of completed issues")
    in_progress_issues: int = Field(..., description="Number of in-progress issues")
    todo_issues: int = Field(..., description="Number of todo issues")
    cancelled_issues: int = Field(..., description="Number of cancelled issues")
    total_story_points: int = Field(..., description="Total story points in sprint")
    completed_story_points: int = Field(..., description="Completed story points")
    in_progress_story_points: int = Field(..., description="In-progress story points")
    todo_story_points: int = Field(..., description="Todo story points")

