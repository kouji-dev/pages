"""Comment management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.comment import (
    CommentListResponse,
    CommentResponse,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from src.application.use_cases.comment import (
    CreateCommentUseCase,
    CreatePageCommentUseCase,
    DeleteCommentUseCase,
    GetCommentUseCase,
    ListCommentsUseCase,
    ListPageCommentsUseCase,
    UpdateCommentUseCase,
)
from src.domain.entities import User
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    CommentRepository,
    IssueRepository,
    PageRepository,
    ProjectRepository,
    SpaceRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.infrastructure.database.models import ProjectMemberModel
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_edit_permission,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_comment_repository,
    get_issue_repository,
    get_page_repository,
    get_permission_service,
    get_project_repository,
    get_space_repository,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_comment_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateCommentUseCase:
    """Get create comment use case with dependencies."""
    return CreateCommentUseCase(comment_repository, issue_repository, user_repository, session)


def get_get_comment_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetCommentUseCase:
    """Get comment use case with dependencies."""
    return GetCommentUseCase(comment_repository, session)


def get_list_comments_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListCommentsUseCase:
    """Get list comments use case with dependencies."""
    return ListCommentsUseCase(comment_repository, issue_repository, session)


def get_create_page_comment_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreatePageCommentUseCase:
    """Get create page comment use case with dependencies."""
    return CreatePageCommentUseCase(comment_repository, page_repository, user_repository, session)


def get_list_page_comments_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListPageCommentsUseCase:
    """Get list page comments use case with dependencies."""
    return ListPageCommentsUseCase(comment_repository, page_repository, session)


def get_update_comment_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateCommentUseCase:
    """Get update comment use case with dependencies."""
    return UpdateCommentUseCase(comment_repository, session)


def get_delete_comment_use_case(
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> DeleteCommentUseCase:
    """Get delete comment use case with dependencies."""
    return DeleteCommentUseCase(comment_repository, project_repository)


@router.post(
    "/issues/{issue_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    issue_id: UUID,
    request: CreateCommentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreateCommentUseCase, Depends(get_create_comment_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CommentResponse:
    """Create a comment on an issue.

    Requires project membership (via organization membership).
    """
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise EntityNotFoundException("Issue", str(issue_id))

    # Check user has edit permissions
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise EntityNotFoundException("Project", str(issue.project_id))

    await require_edit_permission(
        project.organization_id, current_user, permission_service, project_id=project.id
    )

    return await use_case.execute(str(issue_id), request, str(current_user.id))


@router.get(
    "/comments/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK
)
async def get_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetCommentUseCase, Depends(get_get_comment_use_case)],
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> CommentResponse:
    """Get a comment by ID.

    Requires project or space membership (via organization membership).
    """
    comment = await comment_repository.get_by_id(comment_id)
    if comment is None:
        raise EntityNotFoundException("Comment", str(comment_id))

    # Check user is member of the organization
    if comment.issue_id:
        issue = await issue_repository.get_by_id(comment.issue_id)
        if issue is None:
            raise EntityNotFoundException("Issue", str(comment.issue_id))

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(issue.project_id))

        await require_organization_member(project.organization_id, current_user, permission_service)
    elif comment.page_id:
        page = await page_repository.get_by_id(comment.page_id)
        if page is None:
            raise EntityNotFoundException("Page", str(comment.page_id))

        space = await space_repository.get_by_id(page.space_id)
        if space is None:
            raise EntityNotFoundException("Space", str(page.space_id))

        await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(comment_id))


@router.get(
    "/issues/{issue_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_comments(
    issue_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListCommentsUseCase, Depends(get_list_comments_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of comments per page")] = 50,
) -> CommentListResponse:
    """List comments for an issue.

    Requires project membership (via organization membership).
    """
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise EntityNotFoundException("Issue", str(issue_id))

    # Check user is member of the organization
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise EntityNotFoundException("Project", str(issue.project_id))

    await require_organization_member(project.organization_id, current_user, permission_service)

    return await use_case.execute(str(issue_id), page=page, limit=limit)


@router.put(
    "/comments/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK
)
async def update_comment(
    comment_id: UUID,
    request: UpdateCommentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateCommentUseCase, Depends(get_update_comment_use_case)],
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> CommentResponse:
    """Update a comment.

    Requires comment author permission.
    """
    comment = await comment_repository.get_by_id(comment_id)
    if comment is None:
        raise EntityNotFoundException("Comment", str(comment_id))

    # Check user is member of the organization (for access)
    if comment.issue_id:
        issue = await issue_repository.get_by_id(comment.issue_id)
        if issue is None:
            raise EntityNotFoundException("Issue", str(comment.issue_id))

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(issue.project_id))

        await require_organization_member(project.organization_id, current_user, permission_service)
    elif comment.page_id:
        page = await page_repository.get_by_id(comment.page_id)
        if page is None:
            raise EntityNotFoundException("Page", str(comment.page_id))

        space = await space_repository.get_by_id(page.space_id)
        if space is None:
            raise EntityNotFoundException("Space", str(page.space_id))

        await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(comment_id), request, current_user.id)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteCommentUseCase, Depends(get_delete_comment_use_case)],
    comment_repository: Annotated[CommentRepository, Depends(get_comment_repository)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    session: Annotated[AsyncSession, Depends(get_session)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
) -> None:
    """Delete a comment (soft delete).

    Requires comment author or project admin permission.
    """
    comment = await comment_repository.get_by_id(comment_id)
    if comment is None:
        raise EntityNotFoundException("Comment", str(comment_id))

    # Check user is member of the organization (for access)
    is_project_admin = False
    is_space_admin = False
    if comment.issue_id:
        issue = await issue_repository.get_by_id(comment.issue_id)
        if issue is None:
            raise EntityNotFoundException("Issue", str(comment.issue_id))

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise EntityNotFoundException("Project", str(issue.project_id))

        await require_organization_member(project.organization_id, current_user, permission_service)

        # Check if user is project admin
        result = await session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project.id,
                ProjectMemberModel.user_id == current_user.id,
                ProjectMemberModel.role == "admin",
            )
        )
        is_project_admin = result.scalar_one_or_none() is not None
    elif comment.page_id:
        page = await page_repository.get_by_id(comment.page_id)
        if page is None:
            raise EntityNotFoundException("Page", str(comment.page_id))

        space = await space_repository.get_by_id(page.space_id)
        if space is None:
            raise EntityNotFoundException("Space", str(page.space_id))

        await require_organization_member(space.organization_id, current_user, permission_service)

        # Check if user is organization admin (space admin)
        is_space_admin = await permission_service.can_manage_organization(
            current_user, space.organization_id
        )

    await use_case.execute(str(comment_id), current_user.id, is_project_admin, is_space_admin)


@router.post(
    "/pages/{page_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_page_comment(
    page_id: UUID,
    request: CreateCommentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreatePageCommentUseCase, Depends(get_create_page_comment_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> CommentResponse:
    """Create a comment on a page.

    Requires space membership (via organization membership).
    """
    page = await page_repository.get_by_id(page_id)
    if page is None:
        raise EntityNotFoundException("Page", str(page_id))

    # Check user has edit permissions
    space = await space_repository.get_by_id(page.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page.space_id))

    await require_edit_permission(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id), request, str(current_user.id))


@router.get(
    "/pages/{page_id}/comments",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_page_comments(
    page_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListPageCommentsUseCase, Depends(get_list_page_comments_use_case)],
    page_repository: Annotated[PageRepository, Depends(get_page_repository)],
    space_repository: Annotated[SpaceRepository, Depends(get_space_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of comments per page")] = 50,
) -> CommentListResponse:
    """List comments for a page.

    Requires space membership (via organization membership).
    """
    page_entity = await page_repository.get_by_id(page_id)
    if page_entity is None:
        raise EntityNotFoundException("Page", str(page_id))

    # Check user is member of the organization
    space = await space_repository.get_by_id(page_entity.space_id)
    if space is None:
        raise EntityNotFoundException("Space", str(page_entity.space_id))

    await require_organization_member(space.organization_id, current_user, permission_service)

    return await use_case.execute(str(page_id), page=page, limit=limit)
