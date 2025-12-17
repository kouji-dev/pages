"""Unit tests for issue link use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.issue_link import CreateIssueLinkRequest
from src.application.use_cases.issue_link import (
    CreateIssueLinkUseCase,
    DeleteIssueLinkUseCase,
    ListIssueLinksUseCase,
)
from src.domain.entities import Issue, IssueLink
from src.domain.exceptions import EntityNotFoundException, ValidationException


@pytest.fixture
def mock_issue_link_repository():
    """Mock issue link repository."""
    return AsyncMock()


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def test_source_issue():
    """Create a test source issue."""
    return Issue.create(
        project_id=uuid4(),
        issue_number=1,
        title="Source Issue",
    )


@pytest.fixture
def test_target_issue():
    """Create a test target issue."""
    return Issue.create(
        project_id=uuid4(),
        issue_number=2,
        title="Target Issue",
    )


@pytest.fixture
def test_issue_link(test_source_issue, test_target_issue):
    """Create a test issue link."""
    return IssueLink.create(
        source_issue_id=test_source_issue.id,
        target_issue_id=test_target_issue.id,
        link_type="blocks",
    )


class TestCreateIssueLinkUseCase:
    """Tests for CreateIssueLinkUseCase."""

    @pytest.mark.asyncio
    async def test_create_issue_link_success(
        self,
        mock_issue_link_repository,
        mock_issue_repository,
        test_source_issue,
        test_target_issue,
    ):
        """Test successful issue link creation."""
        request = CreateIssueLinkRequest(target_issue_id=test_target_issue.id, link_type="blocks")

        mock_issue_repository.get_by_id.side_effect = [
            test_source_issue,
            test_target_issue,
        ]
        mock_issue_link_repository.check_circular_dependency.return_value = False
        mock_issue_link_repository.exists.return_value = False

        created_link = IssueLink.create(
            source_issue_id=test_source_issue.id,
            target_issue_id=test_target_issue.id,
            link_type=request.link_type,
        )

        mock_issue_link_repository.create.return_value = created_link

        use_case = CreateIssueLinkUseCase(mock_issue_link_repository, mock_issue_repository)

        result = await use_case.execute(test_source_issue.id, request)

        assert result.link_type == "blocks"
        assert result.source_issue_id == test_source_issue.id
        assert result.target_issue_id == test_target_issue.id
        mock_issue_link_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_issue_link_source_not_found(
        self,
        mock_issue_link_repository,
        mock_issue_repository,
    ):
        """Test issue link creation with non-existent source issue."""
        request = CreateIssueLinkRequest(target_issue_id=uuid4(), link_type="blocks")
        source_issue_id = uuid4()

        mock_issue_repository.get_by_id.return_value = None

        use_case = CreateIssueLinkUseCase(mock_issue_link_repository, mock_issue_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(source_issue_id, request)

    @pytest.mark.asyncio
    async def test_create_issue_link_circular_dependency(
        self,
        mock_issue_link_repository,
        mock_issue_repository,
        test_source_issue,
        test_target_issue,
    ):
        """Test issue link creation with circular dependency."""
        request = CreateIssueLinkRequest(target_issue_id=test_target_issue.id, link_type="blocks")

        mock_issue_repository.get_by_id.side_effect = [
            test_source_issue,
            test_target_issue,
        ]
        mock_issue_link_repository.check_circular_dependency.return_value = True

        use_case = CreateIssueLinkUseCase(mock_issue_link_repository, mock_issue_repository)

        with pytest.raises(ValidationException):
            await use_case.execute(test_source_issue.id, request)


class TestListIssueLinksUseCase:
    """Tests for ListIssueLinksUseCase."""

    @pytest.mark.asyncio
    async def test_list_issue_links_success(
        self, mock_issue_link_repository, test_source_issue, test_issue_link
    ):
        """Test successfully listing issue links."""
        links = [test_issue_link]
        mock_issue_link_repository.get_by_issue_id.return_value = links

        use_case = ListIssueLinksUseCase(mock_issue_link_repository)

        result = await use_case.execute(test_source_issue.id)

        assert result.total == 1
        assert len(result.links) == 1
        assert result.links[0].id == test_issue_link.id


class TestDeleteIssueLinkUseCase:
    """Tests for DeleteIssueLinkUseCase."""

    @pytest.mark.asyncio
    async def test_delete_issue_link_success(self, mock_issue_link_repository, test_issue_link):
        """Test successfully deleting an issue link."""
        mock_issue_link_repository.get_by_id.return_value = test_issue_link
        mock_issue_link_repository.delete.return_value = None

        use_case = DeleteIssueLinkUseCase(mock_issue_link_repository)

        await use_case.execute(test_issue_link.id)

        mock_issue_link_repository.delete.assert_called_once_with(test_issue_link.id)

    @pytest.mark.asyncio
    async def test_delete_issue_link_not_found(self, mock_issue_link_repository):
        """Test deleting non-existent issue link."""
        link_id = uuid4()
        mock_issue_link_repository.get_by_id.return_value = None

        use_case = DeleteIssueLinkUseCase(mock_issue_link_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(link_id)
