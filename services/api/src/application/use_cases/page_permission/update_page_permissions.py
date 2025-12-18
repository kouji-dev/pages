"""Update page permissions use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_permission import (
    PagePermissionListResponse,
    PagePermissionResponse,
    UpdatePagePermissionRequest,
)
from src.domain.entities import PagePermission
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PagePermissionRepository,
    PageRepository,
)

logger = structlog.get_logger()


class UpdatePagePermissionsUseCase:
    """Use case for updating page permissions."""

    def __init__(
        self,
        page_repository: PageRepository,
        page_permission_repository: PagePermissionRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            page_permission_repository: Page permission repository
        """
        self._page_repository = page_repository
        self._page_permission_repository = page_permission_repository

    async def execute(
        self,
        page_id: str,
        request: UpdatePagePermissionRequest,
    ) -> PagePermissionListResponse:
        """Execute update page permissions.

        Args:
            page_id: Page ID
            request: Update page permission request

        Returns:
            Updated page permission list response DTO

        Raises:
            EntityNotFoundException: If page not found
            ValueError: If permission data is invalid
        """
        logger.info("Updating page permissions", page_id=page_id)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for updating permissions", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        # Delete existing permissions
        existing_permissions = await self._page_permission_repository.get_all_by_page(page_uuid)
        for perm in existing_permissions:
            await self._page_permission_repository.delete(perm.id)

        # Create new permissions
        new_permissions = []
        for perm_data in request.permissions:
            user_id_value = perm_data.get("user_id")
            if user_id_value:
                user_id = UUID(str(user_id_value))
            else:
                user_id = None
            role = str(perm_data["role"])

            permission = PagePermission.create(
                page_id=page_uuid,
                user_id=user_id,
                role=role,
                inherited_from_space=False,
            )

            created = await self._page_permission_repository.create(permission)
            new_permissions.append(created)

        permission_responses = [
            PagePermissionResponse(
                id=perm.id,
                page_id=perm.page_id,
                user_id=perm.user_id,
                role=perm.role,
                inherited_from_space=perm.inherited_from_space,
                created_at=perm.created_at,
                updated_at=perm.updated_at,
            )
            for perm in new_permissions
        ]

        logger.info("Page permissions updated", page_id=page_id, count=len(new_permissions))

        return PagePermissionListResponse(
            permissions=permission_responses,
            total=len(permission_responses),
        )
