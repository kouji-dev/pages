"""Unit tests for search use cases."""

from uuid import uuid4

import pytest

from src.application.services.search_query_service import SearchQueryService
from src.application.use_cases.search.search_all import SearchAllUseCase
from src.application.use_cases.search.search_issues import SearchIssuesUseCase
from src.application.use_cases.search.search_pages import SearchPagesUseCase


class DummySearchService(SearchQueryService):
    """Lightweight dummy implementation for unit tests."""

    def __init__(self) -> None:  # type: ignore[super-init-not-called]
        self.calls: list[dict] = []

    async def search_issues(self, *args, **kwargs):
        self.calls.append({"method": "issues", "kwargs": kwargs})
        return (
            [
                {
                    "entity_type": "issue",
                    "id": uuid4(),
                    "title": "Issue match",
                    "snippet": "desc",
                    "score": 1.0,
                    "project_id": kwargs.get("project_id"),
                    "space_id": None,
                }
            ],
            1,
        )

    async def search_pages(self, *args, **kwargs):
        self.calls.append({"method": "pages", "kwargs": kwargs})
        return (
            [
                {
                    "entity_type": "page",
                    "id": uuid4(),
                    "title": "Page match",
                    "snippet": "content",
                    "score": 1.0,
                    "project_id": None,
                    "space_id": kwargs.get("space_id"),
                }
            ],
            1,
        )


@pytest.mark.asyncio
async def test_search_issues_use_case_calls_service():
    service = DummySearchService()
    use_case = SearchIssuesUseCase(service)
    project_id = uuid4()

    result = await use_case.execute(project_id=project_id, query="test", page=1, limit=10)

    assert result.total == 1
    assert result.items[0].entity_type == "issue"
    assert service.calls[0]["method"] == "issues"
    assert service.calls[0]["kwargs"]["project_id"] == project_id


@pytest.mark.asyncio
async def test_search_pages_use_case_calls_service():
    service = DummySearchService()
    use_case = SearchPagesUseCase(service)
    space_id = uuid4()

    result = await use_case.execute(space_id=space_id, query="doc", page=1, limit=5)

    assert result.total == 1
    assert result.items[0].entity_type == "page"
    assert service.calls[0]["method"] == "pages"
    assert service.calls[0]["kwargs"]["space_id"] == space_id


@pytest.mark.asyncio
async def test_search_all_use_case_issues_only():
    service = DummySearchService()
    use_case = SearchAllUseCase(service)
    project_id = uuid4()

    result = await use_case.execute(
        query="test",
        search_type="issues",
        project_id=project_id,
        page=1,
        limit=10,
    )

    assert result.total == 1
    assert result.items[0].entity_type == "issue"
    assert service.calls[0]["method"] == "issues"


@pytest.mark.asyncio
async def test_search_all_use_case_pages_only():
    service = DummySearchService()
    use_case = SearchAllUseCase(service)
    space_id = uuid4()

    result = await use_case.execute(
        query="doc",
        search_type="pages",
        space_id=space_id,
        page=1,
        limit=10,
    )

    assert result.total == 1
    assert result.items[0].entity_type == "page"
    assert service.calls[0]["method"] == "pages"
