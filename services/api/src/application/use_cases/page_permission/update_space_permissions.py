"""Update space permissions use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_permission import (
    SpacePermissionListResponse,
    SpacePermissionResponse,
    UpdateSpacePermissionRequest,
)
from src.domain.entities import SpacePermission
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    SpacePermissionRepository,
    SpaceRepository,
)

logger = structlog.get_logger()


class UpdateSpacePermissionsUseCase:
    """Use case for updating space permissions."""

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

    async def execute(
        self,
        space_id: str,
        request: UpdateSpacePermissionRequest,
    ) -> SpacePermissionListResponse:
        """Execute update space permissions.

        Args:
            space_id: Space ID
            request: Update space permission request

        Returns:
            Updated space permission list response DTO

        Raises:
            EntityNotFoundException: If space not found
            ValueError: If permission data is invalid
        """
        logger.info("Updating space permissions", space_id=space_id)

        space_uuid = UUID(space_id)
        space = await self._space_repository.get_by_id(space_uuid)

        if space is None:
            logger.warning("Space not found for updating permissions", space_id=space_id)
            raise EntityNotFoundException("Space", space_id)

        # Delete existing permissions
        existing_permissions = await self._space_permission_repository.get_all_by_space(space_uuid)
        for perm in existing_permissions:
            await self._space_permission_repository.delete(perm.id)

        # Create new permissions
        new_permissions = []
        for perm_data in request.permissions:
            user_id_value = perm_data.get("user_id")
            if user_id_value:
                user_id = UUID(str(user_id_value))
            else:
                user_id = None
            role = str(perm_data["role"])

            permission = SpacePermission.create(
                space_id=space_uuid,
                user_id=user_id,
                role=role,
            )

            created = await self._space_permission_repository.create(permission)
            new_permissions.append(created)

        permission_responses = [
            SpacePermissionResponse(
                id=perm.id,
                space_id=perm.space_id,
                user_id=perm.user_id,
                role=perm.role,
                created_at=perm.created_at,
                updated_at=perm.updated_at,
            )
            for perm in new_permissions
        ]

        logger.info("Space permissions updated", space_id=space_id, count=len(new_permissions))

        return SpacePermissionListResponse(
            permissions=permission_responses,
            total=len(permission_responses),
        )
