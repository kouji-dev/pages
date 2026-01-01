"""Project reports DTOs."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class VelocityDataPoint(BaseModel):
    """Velocity data point for a sprint."""

    sprint_id: UUID
    sprint_name: str
    committed: int = Field(..., description="Committed story points")
    completed: int = Field(..., description="Completed story points")


class VelocityReportResponse(BaseModel):
    """Response DTO for project velocity report."""

    project_id: UUID
    velocity_data: list[VelocityDataPoint] = Field(
        ..., description="Velocity data for each sprint"
    )


class CumulativeFlowDataPoint(BaseModel):
    """Cumulative flow data point for a day."""

    date: date
    todo: int = Field(..., description="Number of issues in todo status")
    in_progress: int = Field(..., description="Number of issues in in-progress status")
    done: int = Field(..., description="Number of issues in done status")


class CumulativeFlowReportResponse(BaseModel):
    """Response DTO for project cumulative flow report."""

    project_id: UUID
    flow_data: list[CumulativeFlowDataPoint] = Field(
        ..., description="Cumulative flow data for each day"
    )


class ProjectSummaryStatsResponse(BaseModel):
    """Response DTO for project summary statistics."""

    project_id: UUID
    avg_velocity: float = Field(..., description="Average velocity (story points per sprint)")
    team_members: int = Field(..., description="Number of active team members")
    cycle_time_days: float = Field(..., description="Average cycle time in days")
    sprint_goal_completion: float = Field(
        ..., description="Current sprint goal completion percentage (0-100)"
    )
