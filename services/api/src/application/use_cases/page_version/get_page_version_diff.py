"""Get page version diff use case."""

from uuid import UUID

import structlog

from src.application.dtos.page_version import PageVersionDiffResponse
from src.domain.exceptions import EntityNotFoundException
from src.domain.repositories import PageRepository, PageVersionRepository

logger = structlog.get_logger()


class GetPageVersionDiffUseCase:
    """Use case for getting diff between page versions."""

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
        compare_to_version_id: str | None = None,
    ) -> PageVersionDiffResponse:
        """Execute get page version diff.

        Args:
            version_id: Page version ID
            compare_to_version_id: Optional version ID to compare with (defaults to current page)

        Returns:
            Page version diff response DTO

        Raises:
            EntityNotFoundException: If version or page not found
        """
        logger.info(
            "Getting page version diff",
            version_id=version_id,
            compare_to_version_id=compare_to_version_id,
        )

        version_uuid = UUID(version_id)
        version = await self._page_version_repository.get_by_id(version_uuid)

        if version is None:
            logger.warning("Page version not found for diff", version_id=version_id)
            raise EntityNotFoundException("PageVersion", version_id)

        # Get comparison version or current page
        if compare_to_version_id:
            compare_to_uuid = UUID(compare_to_version_id)
            compare_to_version = await self._page_version_repository.get_by_id(compare_to_uuid)

            if compare_to_version is None:
                logger.warning(
                    "Compare to version not found",
                    compare_to_version_id=compare_to_version_id,
                )
                raise EntityNotFoundException("PageVersion", compare_to_version_id)

            if compare_to_version.page_id != version.page_id:
                raise ValueError("Versions must belong to the same page")

            compare_title = compare_to_version.title
            compare_content = compare_to_version.content
            compare_version_number = compare_to_version.version_number
        else:
            # Compare with current page
            page = await self._page_repository.get_by_id(version.page_id)

            if page is None:
                logger.warning("Page not found for diff", page_id=str(version.page_id))
                raise EntityNotFoundException("Page", str(version.page_id))

            compare_title = page.title
            compare_content = page.content
            compare_version_number = None

        # Calculate diff
        title_diff = {
            "old": version.title if version.title != compare_title else None,
            "new": compare_title if version.title != compare_title else None,
        }

        content_diff = {
            "old": version.content if version.content != compare_content else None,
            "new": compare_content if version.content != compare_content else None,
        }

        logger.info("Page version diff calculated", version_id=version_id)

        return PageVersionDiffResponse(
            version_id=version.id,
            compare_to_version_id=UUID(compare_to_version_id) if compare_to_version_id else None,
            version_number=version.version_number,
            compare_to_version_number=compare_version_number,
            title_diff=title_diff,
            content_diff=content_diff,
        )
