"""User reactivation use case (admin only)."""

import structlog

from src.domain.exceptions import AuthorizationException, EntityNotFoundException
from src.domain.repositories import UserRepository
from src.domain.services import PermissionService

logger = structlog.get_logger()


class ReactivateUserUseCase:
    """Use case for reactivating a deactivated user (admin only)."""

    def __init__(
        self,
        user_repository: UserRepository,
        permission_service: PermissionService,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            user_repository: User repository for data access
            permission_service: Permission service for admin checks
        """
        self._user_repository = user_repository
        self._user_repository = user_repository
        self._permission_service = permission_service

    async def execute(self, target_user_id: str, admin_user_id: str) -> None:
        """Execute user reactivation.

        Only users who are admin of at least one organization can reactivate users.

        Args:
            target_user_id: ID of the user to reactivate
            admin_user_id: ID of the admin user performing the reactivation

        Raises:
            EntityNotFoundException: If target user not found
            AuthorizationException: If admin user is not authorized (not admin of any org)
        """
        from uuid import UUID

        logger.info(
            "Reactivating user",
            target_user_id=target_user_id,
            admin_user_id=admin_user_id,
        )

        # Verify admin has permission (is admin of at least one organization)
        admin_uuid = UUID(admin_user_id)
        admin_user = await self._user_repository.get_by_id(admin_uuid)

        if admin_user is None:
            logger.warning("Admin user not found for reactivation", admin_user_id=admin_user_id)
            raise EntityNotFoundException("User", admin_user_id)

        # Check if admin is admin of at least one organization
        is_admin = await self._permission_service.is_admin_of_any_organization(admin_user)

        if not is_admin:
            logger.warning(
                "User is not authorized to reactivate users",
                admin_user_id=admin_user_id,
            )
            raise AuthorizationException("Only organization admins can reactivate users")

        # Get target user
        target_uuid = UUID(target_user_id)
        target_user = await self._user_repository.get_by_id(target_uuid)

        if target_user is None:
            logger.warning("Target user not found for reactivation", target_user_id=target_user_id)
            raise EntityNotFoundException("User", target_user_id)

        # Check if user is already active
        if not target_user.is_deleted:
            logger.info("User already active", target_user_id=target_user_id)
            return

        # Reactivate user
        target_user.reactivate()
        await self._user_repository.update(target_user)

        logger.info(
            "User reactivated successfully",
            target_user_id=target_user_id,
            admin_user_id=admin_user_id,
        )
