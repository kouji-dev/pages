"""Unit tests for unified use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.unified import ListFoldersAndNodesUseCase
from src.domain.entities import Folder, Organization, Project, Space


@pytest.fixture
def mock_folder_repository():
    """Mock folder repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_space_repository():
    """Mock space repository."""
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
def test_folder(test_organization):
    """Create a test folder."""
    return Folder.create(
        organization_id=test_organization.id,
        name="Test Folder",
        position=0,
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


class TestListFoldersAndNodesUseCase:
    """Tests for ListFoldersAndNodesUseCase."""

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_success(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_project,
        test_space,
    ):
        """Test successful listing of folders and nodes."""
        folders = [test_folder]
        projects = [test_project]
        spaces = [test_space]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id))

        assert result.total == 3
        assert result.folders_count == 1
        assert result.nodes_count == 2
        assert len(result.items) == 3

        # Check item types
        item_types = [item.type for item in result.items]
        assert "folder" in item_types
        assert "project" in item_types
        assert "space" in item_types

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_with_folder_filter(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_project,
    ):
        """Test listing with folder filter for nodes."""
        folder_id = test_folder.id
        # Assign project to folder
        test_project.folder_id = folder_id

        folders = []
        projects = [test_project]
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), folder_id=str(folder_id))

        assert result.nodes_count == 1
        assert result.items[0].type == "project"
        assert result.items[0].details.folder_id == folder_id

        # Verify folder_id was passed to repositories
        mock_project_repository.get_all.assert_called_once()
        call_kwargs = mock_project_repository.get_all.call_args[1]
        assert call_kwargs["folder_id"] == folder_id

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_with_parent_filter(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
    ):
        """Test listing with parent filter for folders."""
        parent_id = uuid4()
        child_folder = Folder.create(
            organization_id=test_organization.id,
            name="Child Folder",
            parent_id=parent_id,
            position=0,
        )

        folders = [child_folder]
        projects = []
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), parent_id=str(parent_id))

        assert result.folders_count == 1
        assert result.items[0].type == "folder"

        # Verify parent_id was passed to repository
        mock_folder_repository.get_all.assert_called_once()
        call_kwargs = mock_folder_repository.get_all.call_args[1]
        assert call_kwargs["parent_id"] == parent_id

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_exclude_empty_folders(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_project,
    ):
        """Test excluding empty folders."""
        # Assign project to folder
        test_project.folder_id = test_folder.id

        folders = [test_folder]
        projects = [test_project]
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), include_empty_folders=False)

        # Folder should be included because it has a project
        assert result.folders_count == 1
        assert result.total == 2  # 1 folder + 1 project

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_include_empty_folders(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
    ):
        """Test including empty folders."""
        folders = [test_folder]
        projects = []
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), include_empty_folders=True)

        # Empty folder should be included
        assert result.folders_count == 1
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_empty_organization(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
    ):
        """Test listing with empty organization."""
        mock_folder_repository.get_all.return_value = []
        mock_project_repository.get_all.return_value = []
        mock_space_repository.get_all.return_value = []

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id))

        assert result.total == 0
        assert result.folders_count == 0
        assert result.nodes_count == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_only_folders(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
    ):
        """Test listing with only folders."""
        folders = [test_folder]
        projects = []
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id))

        assert result.folders_count == 1
        assert result.nodes_count == 0
        assert result.total == 1
        assert result.items[0].type == "folder"

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_only_nodes(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_project,
        test_space,
    ):
        """Test listing with only nodes."""
        folders = []
        projects = [test_project]
        spaces = [test_space]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id))

        assert result.folders_count == 0
        assert result.nodes_count == 2
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_pagination(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
    ):
        """Test pagination."""
        folders = [
            Folder.create(
                organization_id=test_organization.id,
                name=f"Folder {i}",
                position=i,
            )
            for i in range(3)
        ]
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
            for i in range(2)
        ]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        # Test pagination: skip=2, limit=5
        result = await use_case.execute(str(test_organization.id), skip=2, limit=5)

        # Total should be 10 (3 folders + 5 projects + 2 spaces)
        assert result.total == 10
        # But paginated items should be 5
        assert len(result.items) == 5

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_invalid_uuid(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
    ):
        """Test validation with invalid UUID."""
        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        # Invalid UUID will raise ValueError when converting
        with pytest.raises((ValueError, TypeError)):
            await use_case.execute("invalid-uuid")

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_invalid_limit(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
    ):
        """Test with invalid limit (negative)."""
        mock_folder_repository.get_all.return_value = []
        mock_project_repository.get_all.return_value = []
        mock_space_repository.get_all.return_value = []

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        # Negative limit should be handled by the endpoint validation, not the use case
        # But we can test that the use case handles it gracefully
        result = await use_case.execute(str(test_organization.id), skip=0, limit=-1)

        # Use case should still work, validation happens at endpoint level
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_pagination_skip_greater_than_total(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_project,
    ):
        """Test pagination when skip is greater than total items."""
        folders = []
        projects = [test_project]
        spaces = []

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        # Skip is greater than total (1 item)
        result = await use_case.execute(str(test_organization.id), skip=10, limit=5)

        assert result.total == 1
        assert len(result.items) == 0  # No items because skip > total

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_exclude_empty_folders_with_none_folder_id(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_project,
        test_space,
    ):
        """Test excluding empty folders when projects/spaces have folder_id=None."""
        # Project and space without folder_id should not count toward folder having nodes
        test_project.folder_id = None
        test_space.folder_id = None

        folders = [test_folder]
        projects = [test_project]
        spaces = [test_space]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), include_empty_folders=False)

        # Folder should be excluded because no nodes have this folder_id
        assert result.folders_count == 0
        assert result.nodes_count == 2  # Projects and spaces still counted
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_exclude_empty_folders_with_space_folder_id(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_space,
    ):
        """Test excluding empty folders when space has folder_id."""
        # Space with folder_id should count toward folder having nodes
        test_space.folder_id = test_folder.id

        folders = [test_folder]
        projects = []
        spaces = [test_space]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), include_empty_folders=False)

        # Folder should be included because space has this folder_id
        assert result.folders_count == 1
        assert result.nodes_count == 1
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_list_folders_and_nodes_with_both_filters_none(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        test_organization,
        test_folder,
        test_project,
        test_space,
    ):
        """Test listing with both folder_id and parent_id as None."""
        folders = [test_folder]
        projects = [test_project]
        spaces = [test_space]

        mock_folder_repository.get_all.return_value = folders
        mock_project_repository.get_all.return_value = projects
        mock_space_repository.get_all.return_value = spaces

        use_case = ListFoldersAndNodesUseCase(
            mock_folder_repository, mock_project_repository, mock_space_repository
        )

        result = await use_case.execute(str(test_organization.id), folder_id=None, parent_id=None)

        assert result.total == 3
        assert result.folders_count == 1
        assert result.nodes_count == 2
