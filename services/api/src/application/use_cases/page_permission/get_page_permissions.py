"""Get page permissions use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_permission import (
    PagePermissionListResponse,
    PagePermissionResponse,
)
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import (
    PagePermissionRepository,
    PageRepository,
)

logger = structlog.get_logger()


class GetPagePermissionsUseCase:
    """Use case for getting page permissions."""

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

    async def execute(self, page_id: str) -> PagePermissionListResponse:
        """Execute get page permissions.

        Args:
            page_id: Page ID

        Returns:
            Page permission list response DTO

        Raises:
            EntityNotFoundException: If page not found
        """
        logger.info("Getting page permissions", page_id=page_id)

        page_uuid = UUID(page_id)
        page = await self._page_repository.get_by_id(page_uuid)

        if page is None:
            logger.warning("Page not found for getting permissions", page_id=page_id)
            raise EntityNotFoundException("Page", page_id)

        permissions = await self._page_permission_repository.get_all_by_page(page_uuid)

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
            for perm in permissions
        ]

        logger.info("Page permissions retrieved", page_id=page_id, count=len(permissions))

        return PagePermissionListResponse(
            permissions=permission_responses,
            total=len(permission_responses),
        )
