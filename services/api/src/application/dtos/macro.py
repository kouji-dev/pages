"""Macro DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MacroResponse(BaseModel):
    """Response DTO for macro data."""

    id: UUID
    name: str
    code: str
    config_schema: str | None = None
    macro_type: str = Field(..., description="Macro type: table, code_block, info_panel, etc.")
    is_system: bool = Field(False, description="Whether this is a system macro")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MacroListResponse(BaseModel):
    """Response DTO for paginated macro list."""

    macros: list[MacroResponse]
    total: int = Field(..., description="Total number of macros")
    page: int = Field(..., description="Current page number (1-based)")
    limit: int = Field(..., description="Number of items per page")
    pages_count: int = Field(..., description="Total number of pages (pagination)")


class CreateMacroRequest(BaseModel):
    """Request DTO for creating a macro."""

    name: str = Field(..., min_length=1, max_length=100, description="Macro name")
    code: str = Field(..., min_length=1, description="Macro code/implementation")
    macro_type: str = Field(
        ...,
        description="Macro type: table, code_block, info_panel, warning_panel, error_panel, page_tree, issue_embed",
    )
    config_schema: str | None = Field(None, description="JSON schema for macro configuration")
    is_system: bool = Field(False, description="Whether this is a system macro")


class UpdateMacroRequest(BaseModel):
    """Request DTO for updating a macro."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Macro name")
    code: str | None = Field(None, min_length=1, description="Macro code/implementation")
    config_schema: str | None = Field(None, description="JSON schema for macro configuration")


class ExecuteMacroRequest(BaseModel):
    """Request DTO for executing a macro."""

    macro_name: str = Field(..., description="Macro name to execute")
    config: dict[str, str] = Field(default_factory=dict, description="Macro configuration")


class ExecuteMacroResponse(BaseModel):
    """Response DTO for macro execution."""

    output: str = Field(..., description="Macro output (rendered HTML)")
    macro_name: str = Field(..., description="Name of the executed macro")
