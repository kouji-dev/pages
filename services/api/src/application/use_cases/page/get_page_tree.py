"""Get page tree use case."""

from uuid import UUID

import structlog

from src.application.dtos.page import PageTreeItem, PageTreeResponse
from src.domain.repositories import PageRepository

logger = structlog.get_logger()


class GetPageTreeUseCase:
    """Use case for retrieving a page tree structure."""

    def __init__(self, page_repository: PageRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            page_repository: Page repository
        """
        self._page_repository = page_repository

    async def execute(self, space_id: str) -> PageTreeResponse:
        """Execute get page tree.

        Args:
            space_id: Space ID

        Returns:
            Page tree response DTO with nested structure
        """
        logger.info("Getting page tree", space_id=space_id)

        space_uuid = UUID(space_id)
        pages = await self._page_repository.get_tree(space_uuid)

        # Build tree structure
        page_map: dict[UUID, PageTreeItem] = {}
        root_pages: list[PageTreeItem] = []

        # First pass: create all page items
        for page in pages:
            page_item = PageTreeItem(
                id=page.id,
                space_id=page.space_id,
                title=page.title,
                slug=page.slug,
                content=page.content,
                parent_id=page.parent_id,
                created_by=page.created_by,
                updated_by=page.updated_by,
                position=page.position,
                children=[],
                created_at=page.created_at,
                updated_at=page.updated_at,
            )
            page_map[page.id] = page_item

        # Second pass: build parent-child relationships
        for page in pages:
            page_item = page_map[page.id]
            if page.parent_id is None:
                root_pages.append(page_item)
            else:
                parent_item = page_map.get(page.parent_id)
                if parent_item:
                    parent_item.children.append(page_item)

        # Sort root pages and children by position
        root_pages.sort(key=lambda p: (p.position, p.created_at))
        for page_item in page_map.values():
            page_item.children.sort(key=lambda p: (p.position, p.created_at))

        logger.info("Page tree retrieved", space_id=space_id, count=len(root_pages))

        return PageTreeResponse(pages=root_pages)
