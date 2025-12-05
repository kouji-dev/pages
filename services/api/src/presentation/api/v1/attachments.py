"""Attachment management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.attachment import (
    AttachmentListResponse,
    AttachmentResponse,
    UploadAttachmentResponse,
)
from src.application.use_cases.attachment import (
    DeleteAttachmentUseCase,
    DownloadAttachmentUseCase,
    GetAttachmentUseCase,
    ListAttachmentsUseCase,
    UploadAttachmentUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    AttachmentRepository,
    IssueRepository,
    ProjectRepository,
    UserRepository,
)
from src.domain.services import PermissionService, StorageService
from src.infrastructure.database import get_session
from src.infrastructure.database.models import ProjectMemberModel
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import require_organization_member
from src.presentation.dependencies.services import (
    get_attachment_repository,
    get_issue_repository,
    get_permission_service,
    get_project_repository,
    get_storage_service,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_upload_attachment_use_case(
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UploadAttachmentUseCase:
    """Get upload attachment use case with dependencies."""
    return UploadAttachmentUseCase(
        attachment_repository, issue_repository, user_repository, storage_service, session
    )


def get_get_attachment_use_case(
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetAttachmentUseCase:
    """Get attachment use case with dependencies."""
    return GetAttachmentUseCase(attachment_repository, storage_service, session)


def get_list_attachments_use_case(
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListAttachmentsUseCase:
    """Get list attachments use case with dependencies."""
    return ListAttachmentsUseCase(
        attachment_repository, issue_repository, storage_service, session
    )


def get_delete_attachment_use_case(
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DeleteAttachmentUseCase:
    """Get delete attachment use case with dependencies."""
    return DeleteAttachmentUseCase(attachment_repository, project_repository, storage_service)


def get_download_attachment_use_case(
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DownloadAttachmentUseCase:
    """Get download attachment use case with dependencies."""
    return DownloadAttachmentUseCase(attachment_repository, storage_service)


@router.post(
    "/issues/{issue_id}/attachments",
    response_model=UploadAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    issue_id: UUID,
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UploadAttachmentUseCase, Depends(get_upload_attachment_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> UploadAttachmentResponse:
    """Upload a file attachment to an issue.

    Requires project membership (via organization membership).
    """
    # Verify issue exists and user is member of the organization
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_organization_member(
        project.organization_id, current_user, permission_service
    )

    # Read file content
    file_content = await file.read()
    mime_type = file.content_type or "application/octet-stream"

    return await use_case.execute(
        issue_id=str(issue_id),
        file_content=file_content,
        original_filename=file.filename or "unnamed",
        mime_type=mime_type,
        user_id=str(current_user.id),
    )


@router.get("/attachments/{attachment_id}", response_model=AttachmentResponse, status_code=status.HTTP_200_OK)
async def get_attachment(
    attachment_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetAttachmentUseCase, Depends(get_get_attachment_use_case)],
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> AttachmentResponse:
    """Get attachment metadata by ID.

    Requires project membership (via organization membership).
    """
    attachment = await attachment_repository.get_by_id(attachment_id)
    if attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Check user is member of the organization
    if attachment.entity_type == "issue":
        issue = await issue_repository.get_by_id(attachment.entity_id)
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await require_organization_member(
            project.organization_id, current_user, permission_service
        )

    return await use_case.execute(str(attachment_id))


@router.get(
    "/issues/{issue_id}/attachments",
    response_model=AttachmentListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_attachments(
    issue_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListAttachmentsUseCase, Depends(get_list_attachments_use_case)],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> AttachmentListResponse:
    """List attachments for an issue.

    Requires project membership (via organization membership).
    """
    issue = await issue_repository.get_by_id(issue_id)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Check user is member of the organization
    project = await project_repository.get_by_id(issue.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    await require_organization_member(
        project.organization_id, current_user, permission_service
    )

    return await use_case.execute(str(issue_id))


@router.get(
    "/attachments/{attachment_id}/download",
    status_code=status.HTTP_200_OK,
)
async def download_attachment(
    attachment_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        DownloadAttachmentUseCase, Depends(get_download_attachment_use_case)
    ],
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> Response:
    """Download an attachment file.

    Requires project membership (via organization membership).
    """
    attachment = await attachment_repository.get_by_id(attachment_id)
    if attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Check user is member of the organization
    if attachment.entity_type == "issue":
        issue = await issue_repository.get_by_id(attachment.entity_id)
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await require_organization_member(
            project.organization_id, current_user, permission_service
        )

    file_content, mime_type, original_filename = await use_case.execute(str(attachment_id))

    return Response(
        content=file_content,
        media_type=mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{original_filename}"',
        },
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteAttachmentUseCase, Depends(get_delete_attachment_use_case)],
    attachment_repository: Annotated[
        AttachmentRepository, Depends(get_attachment_repository)
    ],
    issue_repository: Annotated[IssueRepository, Depends(get_issue_repository)],
    project_repository: Annotated[ProjectRepository, Depends(get_project_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete an attachment.

    Requires uploader or project admin permission.
    """
    attachment = await attachment_repository.get_by_id(attachment_id)
    if attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found")

    # Check user is member of the organization (for access)
    is_project_admin = False
    if attachment.entity_type == "issue":
        issue = await issue_repository.get_by_id(attachment.entity_id)
        if issue is None:
            raise HTTPException(status_code=404, detail="Issue not found")

        project = await project_repository.get_by_id(issue.project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await require_organization_member(
            project.organization_id, current_user, permission_service
        )

        # Check if user is project admin
        result = await session.execute(
            select(ProjectMemberModel).where(
                ProjectMemberModel.project_id == project.id,
                ProjectMemberModel.user_id == current_user.id,
                ProjectMemberModel.role == "admin",
            )
        )
        is_project_admin = result.scalar_one_or_none() is not None

    await use_case.execute(str(attachment_id), current_user.id, is_project_admin)

