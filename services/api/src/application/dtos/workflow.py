"""Workflow DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowStatusRequest(BaseModel):
    """Request DTO for creating/updating a workflow status."""

    name: str = Field(..., min_length=1, max_length=100, description="Status name")
    order: int = Field(..., ge=0, description="Display order")
    is_initial: bool = Field(default=False, description="Whether this is the initial status")
    is_final: bool = Field(default=False, description="Whether this is a final status")


class WorkflowStatusResponse(BaseModel):
    """Response DTO for workflow status."""

    id: UUID
    workflow_id: UUID
    name: str
    order: int
    is_initial: bool
    is_final: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkflowTransitionRequest(BaseModel):
    """Request DTO for creating a workflow transition."""

    from_status_id: UUID = Field(..., description="Source status ID")
    to_status_id: UUID = Field(..., description="Target status ID")
    name: str | None = Field(default=None, max_length=100, description="Optional transition name")


class WorkflowTransitionResponse(BaseModel):
    """Response DTO for workflow transition."""

    id: UUID
    workflow_id: UUID
    from_status_id: UUID
    to_status_id: UUID
    name: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CreateWorkflowRequest(BaseModel):
    """Request DTO for creating a workflow."""

    name: str = Field(..., min_length=1, max_length=100, description="Workflow name")
    is_default: bool = Field(default=False, description="Whether this is the default workflow")
    statuses: list[WorkflowStatusRequest] = Field(
        default_factory=list, description="Initial statuses"
    )
    transitions: list[WorkflowTransitionRequest] = Field(
        default_factory=list, description="Initial transitions"
    )


class UpdateWorkflowRequest(BaseModel):
    """Request DTO for updating a workflow."""

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="Workflow name"
    )
    is_default: bool | None = Field(
        default=None, description="Whether this is the default workflow"
    )


class WorkflowResponse(BaseModel):
    """Response DTO for workflow."""

    id: UUID
    project_id: UUID
    name: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
    statuses: list[WorkflowStatusResponse] = Field(default_factory=list)
    transitions: list[WorkflowTransitionResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkflowListItemResponse(BaseModel):
    """Response DTO for workflow list item (without statuses/transitions)."""

    id: UUID
    project_id: UUID
    name: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkflowListResponse(BaseModel):
    """Response DTO for workflow list."""

    workflows: list[WorkflowListItemResponse]
    total: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class ValidateTransitionRequest(BaseModel):
    """Request DTO for validating a transition."""

    from_status_id: UUID = Field(..., description="Source status ID")
    to_status_id: UUID = Field(..., description="Target status ID")


class ValidateTransitionResponse(BaseModel):
    """Response DTO for transition validation."""

    is_valid: bool
    message: str | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True
