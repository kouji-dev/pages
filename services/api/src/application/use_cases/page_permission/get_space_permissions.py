"""Get space permissions use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_permission import (
    SpacePermissionListResponse,
    SpacePermissionResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    SpacePermissionRepository,
    SpaceRepository,
)

logger = structlog.get_logger()


class GetSpacePermissionsUseCase:
    """Use case for getting space permissions."""

    def __init__(
        self,
        space_repository: SpaceRepository,
        space_permission_repository: SpacePermissionRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            space_repository: Space repository
            space_permission_repository: Space permission repository
        """
        self._space_repository = space_repository
        self._space_permission_repository = space_permission_repository

    async def execute(self, space_id: str) -> SpacePermissionListResponse:
        """Execute get space permissions.

        Args:
            space_id: Space ID

        Returns:
            Space permission list response DTO

        Raises:
            EntityNotFoundException: If space not found
        """
        logger.info("Getting space permissions", space_id=space_id)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found for getting permissions", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        permissions = await self._space_permission_repository.get_all_by_space(space_uuid)

        permission_responses = [
            SpacePermissionResponse(
                id=perm.id,
                space_id=perm.space_id,
                user_id=perm.user_id,
                role=perm.role,
                created_at=perm.created_at,
                updated_at=perm.updated_at,
            )
            for perm in permissions
        ]

        logger.info("Space permissions retrieved", space_id=space_id, count=len(permissions))

        return SpacePermissionListResponse(
            permissions=permission_responses,
            total=len(permission_responses),
        )
