"""Node DTOs."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.project import ProjectListItemResponse
from src.application.dtos.space import SpaceListItemResponse


class NodeResponse(BaseModel):
    """Response DTO for node data.

    A node represents either a project or a space in a unified way.
    """

    type: Literal["project", "space"] = Field(..., description="Type of node: project or space")
    data: ProjectListItemResponse | SpaceListItemResponse = Field(
        ..., description="Node data (project or space)"
    )


class NodeListItemResponse(BaseModel):
    """Response DTO for node in list view."""

    type: Literal["project", "space"] = Field(..., description="Type of node: project or space")
    id: UUID = Field(..., description="Node ID")
    organization_id: UUID = Field(..., description="Organization ID")
    name: str = Field(..., description="Node name")
    key: str | None = Field(None, description="Node key (for projects and spaces)")
    description: str | None = Field(None, description="Node description")
    folder_id: UUID | None = Field(None, description="Folder ID if assigned to a folder")
    # Project-specific fields
    member_count: int | None = Field(None, description="Number of members (projects only)")
    issue_count: int | None = Field(None, description="Number of issues (projects only)")
    # Space-specific fields
    page_count: int | None = Field(None, description="Number of pages (spaces only)")


class NodeListResponse(BaseModel):
    """Response DTO for node list."""

    nodes: list[NodeListItemResponse]
    total: int = Field(..., description="Total number of nodes")
