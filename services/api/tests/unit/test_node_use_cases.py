"""Unit tests for node use cases."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.node import ListNodesUseCase
from src.domain.entities import Organization, Project, Space


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def test_organization():
    """Create a test organization."""
    return Organization.create(
        name="Test Organization",
        slug="test-org",
        description="A test organization",
    )


@pytest.fixture
def test_project(test_organization):
    """Create a test project."""
    return Project.create(
        organization_id=test_organization.id,
        name="Test Project",
        key="TEST",
        description="A test project",
    )


@pytest.fixture
def test_space(test_organization):
    """Create a test space."""
    return Space.create(
        organization_id=test_organization.id,
        name="Test Space",
        key="TEST",
        description="A test space",
    )


class TestListNodesUseCase:
    """Tests for ListNodesUseCase."""

    @pytest.mark.asyncio
    async def test_list_nodes_success(
        self,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
        test_project,
        test_space,
    ):
        """Test successful node listing."""
        projects = [test_project]
        spaces = [test_space]
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        # Mock folder_id queries
        folder_result = MagicMock()
        folder_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = folder_result

        # Mock count queries
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        mock_session.execute.side_effect = [
            folder_result,  # project folder_id
            count_result,  # project member_count
            count_result,  # project issue_count
            folder_result,  # space folder_id
            count_result,  # space page_count
        ]

        use_case = ListNodesUseCase(
            mock_project_repository, mock_space_repository, mock_session
        )

        result = await use_case.execute(str(test_organization.id))

        assert len(result.nodes) == 2
        assert result.total == 2
        # Check that we have both project and space
        node_types = [node.type for node in result.nodes]
        assert "project" in node_types
        assert "space" in node_types

    @pytest.mark.asyncio
    async def test_list_nodes_with_folder_filter(
        self,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
        test_project,
    ):
        """Test node listing with folder filter."""
        folder_id = uuid4()
        projects = [test_project]
        spaces = []
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        # Mock folder_id query
        folder_result = MagicMock()
        folder_result.scalar_one_or_none.return_value = folder_id
        mock_session.execute.return_value = folder_result

        # Mock count queries
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        mock_session.execute.side_effect = [
            folder_result,  # project folder_id
            count_result,  # project member_count
            count_result,  # project issue_count
        ]

        use_case = ListNodesUseCase(
            mock_project_repository, mock_space_repository, mock_session
        )

        result = await use_case.execute(
            str(test_organization.id), folder_id=str(folder_id)
        )

        assert len(result.nodes) == 1
        assert result.nodes[0].type == "project"
        assert result.nodes[0].folder_id == folder_id
        # Verify folder_id was passed to repositories
        mock_project_repository.get_all.assert_called_with(
            organization_id=test_organization.id,
            folder_id=folder_id,
            skip=0,
            limit=100,
            include_deleted=False,
        )

    @pytest.mark.asyncio
    async def test_list_nodes_empty(
        self,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
    ):
        """Test node listing with no nodes."""
        mock_project_repository.get_all.return_value = []
        mock_space_repository.get_all.return_value = []

        use_case = ListNodesUseCase(
            mock_project_repository, mock_space_repository, mock_session
        )

        result = await use_case.execute(str(test_organization.id))

        assert len(result.nodes) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_nodes_with_pagination(
        self,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
    ):
        """Test node listing with pagination."""
        projects = [
            Project.create(
                organization_id=test_organization.id,
                name=f"Project {i}",
                key=f"PROJ{i}",
            )
            for i in range(5)
        ]
        spaces = [
            Space.create(
                organization_id=test_organization.id,
                name=f"Space {i}",
                key=f"SPACE{i}",
            )
            for i in range(3)
        ]
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        # Mock folder_id and count queries
        folder_result = MagicMock()
        folder_result.scalar_one_or_none.return_value = None
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        # 5 projects * 3 queries each + 3 spaces * 2 queries each = 21 queries
        mock_session.execute.side_effect = [
            folder_result,
            count_result,
            count_result,
        ] * 5 + [
            folder_result,
            count_result,
        ] * 3

        use_case = ListNodesUseCase(
            mock_project_repository, mock_space_repository, mock_session
        )

        result = await use_case.execute(
            str(test_organization.id), skip=0, limit=10
        )

        assert len(result.nodes) == 8  # 5 projects + 3 spaces
        assert result.total == 8

