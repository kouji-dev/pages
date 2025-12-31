"""Node DTOs."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from src.application.dtos.project import ProjectListItemResponse
from src.application.dtos.space import SpaceListItemResponse
from src.application.dtos.unified import DTOResponseProject, DTOResponseSpace


class NodeResponse(BaseModel):
    """Response DTO for node data.

    A node represents either a project or a space in a unified way.
    """

    type: Literal["project", "space"] = Field(..., description="Type of node: project or space")
    data: ProjectListItemResponse | SpaceListItemResponse = Field(
        ..., description="Node data (project or space)"
    )


class NodeDetailsProject(BaseModel):
    """Response DTO for project details in node (for favorites)."""

    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    key: str | None = Field(None, description="Project key")
    description: str | None = Field(None, max_length=1000, description="Project description")
    folder_id: UUID | None = Field(None, description="Folder ID if assigned to a folder")
    member_count: int = Field(0, description="Number of members in the project")
    issue_count: int = Field(0, description="Number of issues in the project")

    class Config:
        """Pydantic config."""

        from_attributes = True


class NodeDetailsSpace(BaseModel):
    """Response DTO for space details in node (for favorites)."""

    name: str = Field(..., min_length=1, max_length=100, description="Space name")
    key: str | None = Field(None, description="Space key")
    description: str | None = Field(None, max_length=1000, description="Space description")
    folder_id: UUID | None = Field(None, description="Folder ID if assigned to a folder")
    page_count: int = Field(0, description="Number of pages in the space")

    class Config:
        """Pydantic config."""

        from_attributes = True


class NodeListItemResponse(BaseModel):
    """Response DTO for node in list view (for favorites).

    Similar to UnifiedListResponse items but only for projects and spaces.
    """

    type: Literal["project", "space"] = Field(..., description="Type of node: project or space")
    id: UUID = Field(..., description="Node ID")
    organization_id: UUID = Field(..., description="Organization ID")
    details: NodeDetailsProject | NodeDetailsSpace = Field(
        ..., description="Node details (project or space)"
    )


class NodeListResponse(BaseModel):
    """Response DTO for node list."""

    nodes: list[NodeListItemResponse]
    total: int = Field(..., description="Total number of nodes")
