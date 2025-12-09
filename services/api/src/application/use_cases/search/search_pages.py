"""Use case for searching pages."""

from uuid import UUID

from src.application.dtos.search import SearchPagesResponse, SearchResultItem
from src.application.services.search_query_service import SearchQueryService


class SearchPagesUseCase:
    """Search pages within a space."""

    DEFAULT_LIMIT = 20
    MAX_LIMIT = 50

    def __init__(self, search_service: SearchQueryService) -> None:
        self._search_service = search_service

    async def execute(
        self,
        space_id: UUID,
        query: str,
        page: int = 1,
        limit: int = DEFAULT_LIMIT,
    ) -> SearchPagesResponse:
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1:
            raise ValueError("Limit must be >= 1")
        if limit > self.MAX_LIMIT:
            limit = self.MAX_LIMIT

        skip = (page - 1) * limit

        items_raw, total = await self._search_service.search_pages(
            query=query,
            space_id=space_id,
            skip=skip,
            limit=limit,
        )

        items = [
            SearchResultItem(
                entity_type="page",
                id=item["id"],
                title=item["title"],
                snippet=item.get("snippet"),
                score=item.get("score", 0.0),
                project_id=None,
                space_id=item.get("space_id"),
            )
            for item in items_raw
        ]

        return SearchPagesResponse(items=items, total=total, page=page, limit=limit)
