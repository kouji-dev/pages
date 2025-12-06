"""Organization management API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.invitation import (
    AcceptInvitationResponse,
    InvitationListResponse,
    InvitationResponse,
    SendInvitationRequest,
)
from src.application.dtos.organization import (
    CreateOrganizationRequest,
    OrganizationListResponse,
    OrganizationResponse,
    UpdateOrganizationRequest,
)
from src.application.dtos.organization_member import (
    AddMemberRequest,
    OrganizationMemberListResponse,
    OrganizationMemberResponse,
    UpdateMemberRoleRequest,
)
from src.application.dtos.organization_settings import (
    OrganizationSettingsResponse,
    UpdateOrganizationSettingsRequest,
)
from src.application.use_cases.organization import (
    AcceptInvitationUseCase,
    AddOrganizationMemberUseCase,
    CancelInvitationUseCase,
    CreateOrganizationUseCase,
    DeleteOrganizationUseCase,
    GetOrganizationSettingsUseCase,
    GetOrganizationUseCase,
    ListInvitationsUseCase,
    ListOrganizationMembersUseCase,
    ListOrganizationsUseCase,
    RemoveOrganizationMemberUseCase,
    SendInvitationUseCase,
    UpdateOrganizationMemberRoleUseCase,
    UpdateOrganizationSettingsUseCase,
    UpdateOrganizationUseCase,
)
from src.domain.entities import User
from src.domain.repositories import (
    InvitationRepository,
    OrganizationRepository,
    UserRepository,
)
from src.domain.services import PermissionService
from src.infrastructure.database import get_session
from src.presentation.dependencies.auth import get_current_active_user
from src.presentation.dependencies.permissions import (
    require_organization_admin,
    require_organization_member,
)
from src.presentation.dependencies.services import (
    get_invitation_repository,
    get_organization_repository,
    get_permission_service,
    get_user_repository,
)

router = APIRouter()


# Dependency injection for use cases
def get_create_organization_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateOrganizationUseCase:
    """Get create organization use case with dependencies."""
    return CreateOrganizationUseCase(organization_repository, user_repository, session)


def get_organization_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetOrganizationUseCase:
    """Get organization use case with dependencies."""
    return GetOrganizationUseCase(organization_repository, session)


def get_list_organizations_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListOrganizationsUseCase:
    """Get list organizations use case with dependencies."""
    return ListOrganizationsUseCase(organization_repository, session)


def get_update_organization_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateOrganizationUseCase:
    """Get update organization use case with dependencies."""
    return UpdateOrganizationUseCase(organization_repository, session)


def get_delete_organization_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> DeleteOrganizationUseCase:
    """Get delete organization use case with dependencies."""
    return DeleteOrganizationUseCase(organization_repository)


# Member management use case dependencies
def get_add_member_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AddOrganizationMemberUseCase:
    """Get add member use case with dependencies."""
    return AddOrganizationMemberUseCase(organization_repository, user_repository, session)


def get_list_members_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListOrganizationMembersUseCase:
    """Get list members use case with dependencies."""
    return ListOrganizationMembersUseCase(organization_repository, session)


def get_update_member_role_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateOrganizationMemberRoleUseCase:
    """Get update member role use case with dependencies."""
    return UpdateOrganizationMemberRoleUseCase(organization_repository, user_repository, session)


def get_remove_member_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RemoveOrganizationMemberUseCase:
    """Get remove member use case with dependencies."""
    return RemoveOrganizationMemberUseCase(organization_repository, session)


# Invitation use case dependencies
def get_send_invitation_use_case(
    invitation_repository: Annotated[InvitationRepository, Depends(get_invitation_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SendInvitationUseCase:
    """Get send invitation use case with dependencies."""
    return SendInvitationUseCase(
        invitation_repository, organization_repository, user_repository, session
    )


def get_accept_invitation_use_case(
    invitation_repository: Annotated[InvitationRepository, Depends(get_invitation_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AcceptInvitationUseCase:
    """Get accept invitation use case with dependencies."""
    return AcceptInvitationUseCase(
        invitation_repository, organization_repository, user_repository, session
    )


def get_list_invitations_use_case(
    invitation_repository: Annotated[InvitationRepository, Depends(get_invitation_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> ListInvitationsUseCase:
    """Get list invitations use case with dependencies."""
    return ListInvitationsUseCase(invitation_repository, organization_repository)


def get_cancel_invitation_use_case(
    invitation_repository: Annotated[InvitationRepository, Depends(get_invitation_repository)],
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> CancelInvitationUseCase:
    """Get cancel invitation use case with dependencies."""
    return CancelInvitationUseCase(invitation_repository, organization_repository)


# Organization settings use case dependencies
def get_organization_settings_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> GetOrganizationSettingsUseCase:
    """Get organization settings use case with dependencies."""
    return GetOrganizationSettingsUseCase(organization_repository)


def get_update_organization_settings_use_case(
    organization_repository: Annotated[
        OrganizationRepository, Depends(get_organization_repository)
    ],
) -> UpdateOrganizationSettingsUseCase:
    """Get update organization settings use case with dependencies."""
    return UpdateOrganizationSettingsUseCase(organization_repository)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CreateOrganizationUseCase, Depends(get_create_organization_use_case)],
) -> OrganizationResponse:
    """Create a new organization.

    Creates an organization and automatically adds the creator as an admin member.

    Args:
        request: Organization creation request
        current_user: Current authenticated user (will be added as admin)
        use_case: Create organization use case

    Returns:
        Created organization response with member count

    Raises:
        HTTPException: If slug already exists or validation fails
    """
    return await use_case.execute(request, str(current_user.id))


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_organization(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[GetOrganizationUseCase, Depends(get_organization_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationResponse:
    """Get organization by ID.

    Requires the user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user
        use_case: Get organization use case
        permission_service: Permission service

    Returns:
        Organization response with details and member count

    Raises:
        HTTPException: If organization not found or user is not a member
    """
    # Verify user is a member
    await require_organization_member(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id))


@router.get(
    "/",
    response_model=OrganizationListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_organizations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListOrganizationsUseCase, Depends(get_list_organizations_use_case)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of organizations per page")] = 20,
    search: Annotated[str | None, Query(description="Search query (name or slug)")] = None,
) -> OrganizationListResponse:
    """List organizations for the current user.

    Returns only organizations where the current user is a member.

    Args:
        current_user: Current authenticated user
        use_case: List organizations use case
        page: Page number (1-based)
        limit: Number of organizations per page
        search: Optional search query

    Returns:
        Paginated list of organizations with member counts
    """
    return await use_case.execute(
        user_id=str(current_user.id),
        page=page,
        limit=limit,
        search=search,
    )


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization(
    organization_id: UUID,
    request: UpdateOrganizationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[UpdateOrganizationUseCase, Depends(get_update_organization_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationResponse:
    """Update an organization.

    Requires admin role in the organization.

    Args:
        organization_id: Organization UUID (from path)
        request: Organization update request
        current_user: Current authenticated user
        use_case: Update organization use case
        permission_service: Permission service

    Returns:
        Updated organization response

    Raises:
        HTTPException: If organization not found, user is not admin, or slug conflicts
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), request)


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[DeleteOrganizationUseCase, Depends(get_delete_organization_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Delete an organization (soft delete).

    Requires admin role in the organization.
    This will cascade soft delete to projects and spaces.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user
        use_case: Delete organization use case
        permission_service: Permission service

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If organization not found or user is not admin
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    await use_case.execute(str(organization_id))


# Member management endpoints
@router.post(
    "/{organization_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_organization_member(
    organization_id: UUID,
    request: AddMemberRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[AddOrganizationMemberUseCase, Depends(get_add_member_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationMemberResponse:
    """Add a member to an organization.

    Requires admin role in the organization.

    Args:
        organization_id: Organization UUID (from path)
        request: Add member request
        current_user: Current authenticated user (must be admin)
        use_case: Add member use case
        permission_service: Permission service

    Returns:
        Added member response with user details

    Raises:
        HTTPException: If organization/user not found, user already member, or not admin
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), request)


@router.get(
    "/{organization_id}/members",
    response_model=OrganizationMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_organization_members(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListOrganizationMembersUseCase, Depends(get_list_members_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of members per page")] = 20,
) -> OrganizationMemberListResponse:
    """List members of an organization.

    Requires user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user (must be member)
        use_case: List members use case
        permission_service: Permission service
        page: Page number (1-based)
        limit: Number of members per page

    Returns:
        Paginated list of members with user details

    Raises:
        HTTPException: If organization not found or user is not a member
    """
    # Verify user is a member
    await require_organization_member(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), page=page, limit=limit)


@router.put(
    "/{organization_id}/members/{user_id}",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization_member_role(
    organization_id: UUID,
    user_id: UUID,
    request: UpdateMemberRoleRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateOrganizationMemberRoleUseCase, Depends(get_update_member_role_use_case)
    ],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationMemberResponse:
    """Update a member's role in an organization.

    Requires admin role in the organization.
    Prevents removing the last admin.

    Args:
        organization_id: Organization UUID (from path)
        user_id: User ID of the member to update (from path)
        request: Update role request
        current_user: Current authenticated user (must be admin)
        use_case: Update member role use case
        permission_service: Permission service

    Returns:
        Updated member response with user details

    Raises:
        HTTPException: If organization/member not found, not admin, or trying to remove last admin
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), str(user_id), request, str(current_user.id))


@router.delete(
    "/{organization_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_organization_member(
    organization_id: UUID,
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[RemoveOrganizationMemberUseCase, Depends(get_remove_member_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Remove a member from an organization.

    Requires admin role in the organization (or user removing themselves).
    Prevents removing the last admin.

    Args:
        organization_id: Organization UUID (from path)
        user_id: User ID of the member to remove (from path)
        current_user: Current authenticated user
        use_case: Remove member use case
        permission_service: Permission service

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If organization/member not found, not authorized, or trying to remove last admin
    """
    # Allow if admin OR user removing themselves
    requester_uuid = UUID(str(current_user.id))
    target_uuid = user_id

    if requester_uuid != target_uuid:
        # User removing someone else - requires admin
        await require_organization_admin(
            organization_id=organization_id,
            current_user=current_user,
            permission_service=permission_service,
        )

    await use_case.execute(str(organization_id), str(user_id), str(current_user.id))


# Invitation endpoints
@router.post(
    "/{organization_id}/members/invite",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_invitation(
    organization_id: UUID,
    request: SendInvitationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[SendInvitationUseCase, Depends(get_send_invitation_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> InvitationResponse:
    """Send an invitation to join an organization.

    Requires admin role in the organization.
    Creates an invitation that expires in 7 days.

    Args:
        organization_id: Organization UUID (from path)
        request: Send invitation request (email, role)
        current_user: Current authenticated user (must be admin)
        use_case: Send invitation use case
        permission_service: Permission service

    Returns:
        Created invitation response

    Raises:
        HTTPException: If organization not found, not admin, email already member/invited, or validation fails
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), request, str(current_user.id))


@router.post(
    "/invitations/{token}/accept",
    response_model=AcceptInvitationResponse,
    status_code=status.HTTP_200_OK,
)
async def accept_invitation(
    token: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[AcceptInvitationUseCase, Depends(get_accept_invitation_use_case)],
) -> AcceptInvitationResponse:
    """Accept an invitation to join an organization.

    Adds the authenticated user to the organization with the role specified in the invitation.
    User's email must match the invitation email.

    Args:
        token: Invitation token (from path)
        current_user: Current authenticated user
        use_case: Accept invitation use case

    Returns:
        Accept invitation response with organization details

    Raises:
        HTTPException: If invitation not found, expired, already accepted, email mismatch, or user already member
    """
    return await use_case.execute(token, str(current_user.id))


@router.get(
    "/{organization_id}/invitations",
    response_model=InvitationListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_invitations(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[ListInvitationsUseCase, Depends(get_list_invitations_use_case)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based)")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Number of invitations per page")] = 20,
    pending_only: Annotated[
        bool, Query(description="Only return pending (not accepted) invitations")
    ] = True,
) -> InvitationListResponse:
    """List invitations for an organization.

    Requires admin role in the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user (must be admin)
        use_case: List invitations use case
        permission_service: Permission service
        page: Page number (1-based)
        limit: Number of invitations per page
        pending_only: If True, only return pending invitations

    Returns:
        Paginated list of invitations

    Raises:
        HTTPException: If organization not found or user is not admin
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(
        str(organization_id), page=page, limit=limit, pending_only=pending_only
    )


@router.delete(
    "/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_invitation(
    invitation_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[CancelInvitationUseCase, Depends(get_cancel_invitation_use_case)],
    invitation_repository: Annotated[InvitationRepository, Depends(get_invitation_repository)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> None:
    """Cancel a pending invitation.

    Requires admin role in the organization.
    Cannot cancel an invitation that has already been accepted.

    Args:
        invitation_id: Invitation UUID (from path)
        current_user: Current authenticated user (must be admin)
        use_case: Cancel invitation use case
        invitation_repository: Invitation repository
        permission_service: Permission service

    Returns:
        No content (204) on success

    Raises:
        HTTPException: If invitation not found, already accepted, or user is not admin
    """
    # Get invitation to verify organization
    invitation = await invitation_repository.get_by_id(invitation_id)
    if invitation is None:
        from src.domain.exceptions import EntityNotFoundException

        raise EntityNotFoundException("Invitation", str(invitation_id))

    # Verify user is admin of the organization
    await require_organization_admin(
        organization_id=invitation.organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    await use_case.execute(str(invitation_id))


# Organization settings endpoints
@router.get(
    "/{organization_id}/settings",
    response_model=OrganizationSettingsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_organization_settings(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        GetOrganizationSettingsUseCase, Depends(get_organization_settings_use_case)
    ],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationSettingsResponse:
    """Get organization settings.

    Requires user to be a member of the organization.

    Args:
        organization_id: Organization UUID (from path)
        current_user: Current authenticated user (must be member)
        use_case: Get organization settings use case
        permission_service: Permission service

    Returns:
        Organization settings response with default settings if none set

    Raises:
        HTTPException: If organization not found or user is not a member
    """
    # Verify user is a member
    await require_organization_member(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id))


@router.put(
    "/{organization_id}/settings",
    response_model=OrganizationSettingsResponse,
    status_code=status.HTTP_200_OK,
)
async def update_organization_settings(
    organization_id: UUID,
    request: UpdateOrganizationSettingsRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    use_case: Annotated[
        UpdateOrganizationSettingsUseCase, Depends(get_update_organization_settings_use_case)
    ],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
) -> OrganizationSettingsResponse:
    """Update organization settings.

    Requires admin role in the organization.
    Settings are merged with existing settings (not replaced).

    Args:
        organization_id: Organization UUID (from path)
        request: Settings update request
        current_user: Current authenticated user (must be admin)
        use_case: Update organization settings use case
        permission_service: Permission service

    Returns:
        Updated organization settings response

    Raises:
        HTTPException: If organization not found, user is not admin, or validation fails
    """
    # Verify user is admin
    await require_organization_admin(
        organization_id=organization_id,
        current_user=current_user,
        permission_service=permission_service,
    )

    return await use_case.execute(str(organization_id), request)
