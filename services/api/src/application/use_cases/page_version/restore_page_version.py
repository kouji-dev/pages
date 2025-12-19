"""Restore page version use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_version import RestorePageVersionResponse
from src.domain.entities import PageVersion
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PageVersionRepository

logger = structlog.get_logger()


class RestorePageVersionUseCase:
    """Use case for restoring a page from a version."""

    def __init__(
        self,
        page_repository: PageRepository,
        page_version_repository: PageVersionRepository,
    ) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
            page_version_repository: Page version repository
        """
        self._page_repository = page_repository
        self._page_version_repository = page_version_repository

    async def execute(
        self,
        version_id: str,
        restored_by: str | None = None,
    ) -> RestorePageVersionResponse:
        """Execute restore page version.

        Creates a new version from the restored content.

        Args:
            version_id: Page version ID to restore
            restored_by: ID of the user restoring the version

        Returns:
            Restore page version response DTO

        Raises:
            EntityNotFoundException: If version or page not found
        """
        logger.info("Restoring page version", version_id=version_id)

        version_uuid = UUID(version_id)
        version = await self._page_version_repository.get_by_id(version_uuid)

        if version is None:
            logger.warning("Page version not found for restore", version_id=version_id)
            raise EntityNotFoundException("PageVersion", version_id)

        # Get the page
        page = await self._page_repository.get_by_id(version.page_id)

        if page is None:
            logger.warning("Page not found for restore", page_id=str(version.page_id))
            raise EntityNotFoundException("Page", str(version.page_id))

        # Update page with version content
        page.update_title(version.title, regenerate_slug=False)
        page.update_content(version.content, updated_by=UUID(restored_by) if restored_by else None)

        # Persist page update
        updated_page = await self._page_repository.update(page)

        # Create new version from restored content
        next_version_number = await self._page_version_repository.get_next_version_number(
            version.page_id
        )
        restored_by_uuid = UUID(restored_by) if restored_by else None

        new_version = PageVersion.create(
            page_id=version.page_id,
            version_number=next_version_number,
            title=updated_page.title,
            content=updated_page.content,
            created_by=restored_by_uuid,
        )

        created_version = await self._page_version_repository.create(new_version)

        logger.info(
            "Page version restored",
            version_id=version_id,
            new_version_id=str(created_version.id),
        )

        return RestorePageVersionResponse(
            page_id=version.page_id,
            restored_version_id=version.id,
            new_version_id=created_version.id,
            message=f"Page restored from version {version.version_number}",
        )
