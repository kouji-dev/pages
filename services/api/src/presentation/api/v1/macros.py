"""Macro management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.application.dtos.macro import (
    CreateMacroRequest,
    ExecuteMacroRequest,
    ExecuteMacroResponse,
    MacroListResponse,
    MacroResponse,
    UpdateMacroRequest,
)
from src.application.use_cases.macro import (
    CreateMacroUseCase,
    DeleteMacroUseCase,
    ExecuteMacroUseCase,
    GetMacroUseCase,
    ListMacrosUseCase,
    UpdateMacroUseCase,
)
from src.domain.entities import User
from src.domain.repositories import MacroRepository
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.services import get_macro_repository

router = APIRouter()


# Dependency injection for use cases
def get_create_macro_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> CreateMacroUseCase:
    """Get create macro use case with dependencies."""
    return CreateMacroUseCase(macro_repository)


def get_get_macro_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> GetMacroUseCase:
    """Get macro use case with dependencies."""
    return GetMacroUseCase(macro_repository)


def get_list_macros_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> ListMacrosUseCase:
    """Get list macros use case with dependencies."""
    return ListMacrosUseCase(macro_repository)


def get_update_macro_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> UpdateMacroUseCase:
    """Get update macro use case with dependencies."""
    return UpdateMacroUseCase(macro_repository)


def get_delete_macro_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> DeleteMacroUseCase:
    """Get delete macro use case with dependencies."""
    return DeleteMacroUseCase(macro_repository)


def get_execute_macro_use_case(
    macro_repository: Annotated[MacroRepository, Depends(get_macro_repository)],
) -> ExecuteMacroUseCase:
    """Get execute macro use case with dependencies."""
    return ExecuteMacroUseCase(macro_repository)


@router.post("/", response_model=MacroResponse, status_code=status.HTTP_201_CREATED)
async def create_macro(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: CreateMacroRequest,
    use_case: Annotated[CreateMacroUseCase, Depends(get_create_macro_use_case)],
) -> MacroResponse:
    """Create a new macro.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        request: Create macro request
        use_case: Create macro use case

    Returns:
        Created macro response

    Raises:
        HTTPException: If macro name already exists
    """
    return await use_case.execute(request)


@router.get("/", response_model=MacroListResponse, status_code=status.HTTP_200_OK)
async def list_macros(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListMacrosUseCase, Depends(get_list_macros_use_case)],
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of macros per page"),
    macro_type: str | None = Query(None, description="Filter by macro type"),
    include_system: bool = Query(True, description="Include system macros"),
) -> MacroListResponse:
    """List macros.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        use_case: List macros use case
        page: Page number (1-based)
        limit: Number of macros per page
        macro_type: Optional macro type filter
        include_system: Whether to include system macros

    Returns:
        Macro list response with pagination metadata
    """
    return await use_case.execute(
        page=page,
        limit=limit,
        macro_type=macro_type,
        include_system=include_system,
    )


@router.get("/{macro_id}", response_model=MacroResponse, status_code=status.HTTP_200_OK)
async def get_macro(
    current_user: Annotated[User, Depends(get_current_active_user)],
    macro_id: UUID,
    use_case: Annotated[GetMacroUseCase, Depends(get_get_macro_use_case)],
) -> MacroResponse:
    """Get a macro by ID.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        macro_id: Macro UUID (from path)
        use_case: Get macro use case

    Returns:
        Macro response

    Raises:
        HTTPException: If macro not found
    """
    return await use_case.execute(str(macro_id))


@router.put("/{macro_id}", response_model=MacroResponse, status_code=status.HTTP_200_OK)
async def update_macro(
    current_user: Annotated[User, Depends(get_current_active_user)],
    macro_id: UUID,
    request: UpdateMacroRequest,
    use_case: Annotated[UpdateMacroUseCase, Depends(get_update_macro_use_case)],
) -> MacroResponse:
    """Update a macro.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        macro_id: Macro UUID (from path)
        request: Update macro request
        use_case: Update macro use case

    Returns:
        Updated macro response

    Raises:
        HTTPException: If macro not found
    """
    return await use_case.execute(str(macro_id), request)


@router.delete("/{macro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_macro(
    current_user: Annotated[User, Depends(get_current_active_user)],
    macro_id: UUID,
    use_case: Annotated[DeleteMacroUseCase, Depends(get_delete_macro_use_case)],
) -> None:
    """Delete a macro.

    Requires authentication.
    Cannot delete system macros.

    Args:
        current_user: Current authenticated user
        macro_id: Macro UUID (from path)
        use_case: Delete macro use case

    Raises:
        HTTPException: If macro not found or is a system macro
    """
    await use_case.execute(str(macro_id))


@router.post("/execute", response_model=ExecuteMacroResponse, status_code=status.HTTP_200_OK)
async def execute_macro(
    current_user: Annotated[User, Depends(get_current_active_user)],
    request: ExecuteMacroRequest,
    use_case: Annotated[ExecuteMacroUseCase, Depends(get_execute_macro_use_case)],
) -> ExecuteMacroResponse:
    """Execute a macro.

    Requires authentication.

    Args:
        current_user: Current authenticated user
        request: Execute macro request
        use_case: Execute macro use case

    Returns:
        Macro execution response

    Raises:
        HTTPException: If macro not found or execution fails
    """
    return await use_case.execute(request)
