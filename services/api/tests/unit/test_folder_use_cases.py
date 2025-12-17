"""Unit tests for folder use cases."""

from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.folder import (
    AssignNodesToFolderRequest,
    CreateFolderRequest,
    UpdateFolderRequest,
)
from src.application.use_cases.folder import (
    AssignNodesToFolderUseCase,
    CreateFolderUseCase,
    DeleteFolderUseCase,
    GetFolderUseCase,
    ListFoldersUseCase,
    UpdateFolderUseCase,
)
from src.domain.entities import Folder, Organization, Project, Space
from src.domain.exceptions import ConflictException, EntityNotFoundException, ValidationException


@pytest.fixture
def mock_folder_repository():
    """Mock folder repository."""
    return AsyncMock()


@pytest.fixture
def mock_organization_repository():
    """Mock organization repository."""
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
def test_folder(test_organization):
    """Create a test folder."""
    return Folder.create(
        organization_id=test_organization.id,
        name="Test Folder",
        parent_id=None,
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


class TestCreateFolderUseCase:
    """Tests for CreateFolderUseCase."""

    @pytest.mark.asyncio
    async def test_create_folder_success(
        self,
        mock_folder_repository,
        mock_organization_repository,
        test_organization,
    ):
        """Test successful folder creation."""
        request = CreateFolderRequest(
            organization_id=test_organization.id,
            name="New Folder",
            parent_id=None,
            position=0,
        )
        mock_organization_repository.get_by_id.return_value = test_organization

        created_folder = Folder.create(
            organization_id=request.organization_id,
            name=request.name,
            parent_id=request.parent_id,
            position=request.position,
        )
        mock_folder_repository.create.return_value = created_folder
        mock_folder_repository.exists_by_name.return_value = False

        use_case = CreateFolderUseCase(mock_folder_repository, mock_organization_repository)

        result = await use_case.execute(request, str(uuid4()))

        assert result.name == "New Folder"
        assert result.organization_id == test_organization.id
        mock_folder_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_folder_with_parent(
        self,
        mock_folder_repository,
        mock_organization_repository,
        test_organization,
        test_folder,
    ):
        """Test folder creation with parent."""
        request = CreateFolderRequest(
            organization_id=test_organization.id,
            name="Child Folder",
            parent_id=test_folder.id,
            position=0,
        )
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_folder_repository.get_by_id.return_value = test_folder

        created_folder = Folder.create(
            organization_id=request.organization_id,
            name=request.name,
            parent_id=request.parent_id,
            position=request.position,
        )
        mock_folder_repository.create.return_value = created_folder
        mock_folder_repository.exists_by_name.return_value = False

        use_case = CreateFolderUseCase(mock_folder_repository, mock_organization_repository)

        result = await use_case.execute(request, str(uuid4()))

        assert result.name == "Child Folder"
        assert result.parent_id == test_folder.id
        mock_folder_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_folder_organization_not_found(
        self,
        mock_folder_repository,
        mock_organization_repository,
    ):
        """Test folder creation with non-existent organization."""
        request = CreateFolderRequest(
            organization_id=uuid4(),
            name="New Folder",
        )
        mock_organization_repository.get_by_id.return_value = None

        use_case = CreateFolderUseCase(mock_folder_repository, mock_organization_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request, str(uuid4()))

    @pytest.mark.asyncio
    async def test_create_folder_parent_not_found(
        self,
        mock_folder_repository,
        mock_organization_repository,
        test_organization,
    ):
        """Test folder creation with non-existent parent."""
        request = CreateFolderRequest(
            organization_id=test_organization.id,
            name="Child Folder",
            parent_id=uuid4(),
        )
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_folder_repository.get_by_id.return_value = None

        use_case = CreateFolderUseCase(mock_folder_repository, mock_organization_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(request, str(uuid4()))

    @pytest.mark.asyncio
    async def test_create_folder_name_conflict(
        self,
        mock_folder_repository,
        mock_organization_repository,
        test_organization,
    ):
        """Test folder creation with duplicate name."""
        request = CreateFolderRequest(
            organization_id=test_organization.id,
            name="Existing Folder",
        )
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_folder_repository.exists_by_name.return_value = True

        use_case = CreateFolderUseCase(mock_folder_repository, mock_organization_repository)

        # ConflictException should be raised before create is called
        with pytest.raises(ConflictException):
            await use_case.execute(request, str(uuid4()))

        # Verify create was not called
        mock_folder_repository.create.assert_not_called()


class TestGetFolderUseCase:
    """Tests for GetFolderUseCase."""

    @pytest.mark.asyncio
    async def test_get_folder_success(self, mock_folder_repository, test_folder):
        """Test successful folder retrieval."""
        mock_folder_repository.get_by_id.return_value = test_folder

        use_case = GetFolderUseCase(mock_folder_repository)

        result = await use_case.execute(str(test_folder.id))

        assert result.id == test_folder.id
        assert result.name == test_folder.name
        mock_folder_repository.get_by_id.assert_called_once_with(test_folder.id)

    @pytest.mark.asyncio
    async def test_get_folder_not_found(self, mock_folder_repository):
        """Test folder retrieval with non-existent ID."""
        mock_folder_repository.get_by_id.return_value = None

        use_case = GetFolderUseCase(mock_folder_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestListFoldersUseCase:
    """Tests for ListFoldersUseCase."""

    @pytest.mark.asyncio
    async def test_list_folders_success(
        self, mock_folder_repository, test_organization, test_folder
    ):
        """Test successful folder listing."""
        folders = [test_folder]
        mock_folder_repository.get_all.return_value = folders
        mock_folder_repository.count.return_value = 1

        use_case = ListFoldersUseCase(mock_folder_repository)

        result = await use_case.execute(str(test_organization.id))

        assert len(result.folders) == 1
        assert result.folders[0].id == test_folder.id
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_list_folders_with_parent(
        self, mock_folder_repository, test_organization, test_folder
    ):
        """Test folder listing with parent filter."""
        child_folder = Folder.create(
            organization_id=test_organization.id,
            name="Child Folder",
            parent_id=test_folder.id,
        )
        folders = [child_folder]
        mock_folder_repository.get_all.return_value = folders
        mock_folder_repository.count.return_value = 1

        use_case = ListFoldersUseCase(mock_folder_repository)

        result = await use_case.execute(str(test_organization.id), parent_id=str(test_folder.id))

        assert len(result.folders) == 1
        assert result.folders[0].parent_id == test_folder.id


class TestUpdateFolderUseCase:
    """Tests for UpdateFolderUseCase."""

    @pytest.mark.asyncio
    async def test_update_folder_name_success(self, mock_folder_repository, test_folder):
        """Test successful folder name update."""
        mock_folder_repository.get_by_id.return_value = test_folder

        updated_folder = Folder(
            id=test_folder.id,
            organization_id=test_folder.organization_id,
            name="Updated Name",
            parent_id=test_folder.parent_id,
            position=test_folder.position,
            created_at=test_folder.created_at,
            updated_at=test_folder.updated_at,
            deleted_at=test_folder.deleted_at,
        )
        updated_folder.update_name("Updated Name")
        mock_folder_repository.update.return_value = updated_folder

        use_case = UpdateFolderUseCase(mock_folder_repository)

        request = UpdateFolderRequest(name="Updated Name")
        result = await use_case.execute(str(test_folder.id), request)

        assert result.name == "Updated Name"
        mock_folder_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_folder_parent_success(
        self, mock_folder_repository, test_organization, test_folder
    ):
        """Test successful folder parent update."""
        parent_folder = Folder.create(
            organization_id=test_organization.id,
            name="Parent Folder",
        )
        mock_folder_repository.get_by_id.side_effect = [test_folder, parent_folder]

        updated_folder = Folder(
            id=test_folder.id,
            organization_id=test_folder.organization_id,
            name=test_folder.name,
            parent_id=parent_folder.id,
            position=test_folder.position,
            created_at=test_folder.created_at,
            updated_at=test_folder.updated_at,
            deleted_at=test_folder.deleted_at,
        )
        updated_folder.update_parent(parent_folder.id)
        mock_folder_repository.update.return_value = updated_folder

        use_case = UpdateFolderUseCase(mock_folder_repository)

        request = UpdateFolderRequest(parent_id=parent_folder.id)
        result = await use_case.execute(str(test_folder.id), request)

        assert result.parent_id == parent_folder.id
        mock_folder_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_folder_not_found(self, mock_folder_repository):
        """Test folder update with non-existent ID."""
        mock_folder_repository.get_by_id.return_value = None

        use_case = UpdateFolderUseCase(mock_folder_repository)

        request = UpdateFolderRequest(name="New Name")
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_update_folder_self_parent(self, mock_folder_repository, test_folder):
        """Test folder update with self as parent."""
        mock_folder_repository.get_by_id.return_value = test_folder

        use_case = UpdateFolderUseCase(mock_folder_repository)

        request = UpdateFolderRequest(parent_id=test_folder.id)
        with pytest.raises(ValidationException):
            await use_case.execute(str(test_folder.id), request)


class TestDeleteFolderUseCase:
    """Tests for DeleteFolderUseCase."""

    @pytest.mark.asyncio
    async def test_delete_folder_success(self, mock_folder_repository, test_folder):
        """Test successful folder deletion."""
        mock_folder_repository.get_by_id.return_value = test_folder
        test_folder.delete()
        mock_folder_repository.update.return_value = test_folder

        use_case = DeleteFolderUseCase(mock_folder_repository)

        await use_case.execute(str(test_folder.id))

        mock_folder_repository.update.assert_called_once()
        assert test_folder.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_folder_not_found(self, mock_folder_repository):
        """Test folder deletion with non-existent ID."""
        mock_folder_repository.get_by_id.return_value = None

        use_case = DeleteFolderUseCase(mock_folder_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestAssignNodesToFolderUseCase:
    """Tests for AssignNodesToFolderUseCase."""

    @pytest.mark.asyncio
    async def test_assign_project_to_folder_success(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
        test_folder,
        test_project,
    ):
        """Test successful project assignment to folder."""
        mock_folder_repository.get_by_id.return_value = test_folder
        mock_project_repository.get_by_id.return_value = test_project

        # Mock SQLAlchemy model
        from src.infrastructure.database.models import ProjectModel

        project_model = MagicMock(spec=ProjectModel)
        project_model.id = test_project.id
        project_model.folder_id = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = project_model
        mock_session.execute.return_value = result_mock
        mock_session.flush = AsyncMock()

        use_case = AssignNodesToFolderUseCase(
            mock_folder_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        request = AssignNodesToFolderRequest(node_ids=[test_project.id])
        await use_case.execute(str(test_folder.id), request)

        mock_session.execute.assert_called()
        mock_session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_assign_space_to_folder_success(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_organization,
        test_folder,
        test_space,
    ):
        """Test successful space assignment to folder."""
        mock_folder_repository.get_by_id.return_value = test_folder
        mock_project_repository.get_by_id.return_value = None
        mock_space_repository.get_by_id.return_value = test_space

        # Mock SQLAlchemy model
        from src.infrastructure.database.models import SpaceModel

        space_model = MagicMock(spec=SpaceModel)
        space_model.id = test_space.id
        space_model.folder_id = None

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = space_model
        mock_session.execute.return_value = result_mock
        mock_session.flush = AsyncMock()

        use_case = AssignNodesToFolderUseCase(
            mock_folder_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        request = AssignNodesToFolderRequest(node_ids=[test_space.id])
        await use_case.execute(str(test_folder.id), request)

        mock_session.execute.assert_called()
        mock_session.flush.assert_called()

    @pytest.mark.asyncio
    async def test_assign_nodes_folder_not_found(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
    ):
        """Test node assignment with non-existent folder."""
        mock_folder_repository.get_by_id.return_value = None

        use_case = AssignNodesToFolderUseCase(
            mock_folder_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        request = AssignNodesToFolderRequest(node_ids=[uuid4()])
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_assign_nodes_node_not_found(
        self,
        mock_folder_repository,
        mock_project_repository,
        mock_space_repository,
        mock_session,
        test_folder,
    ):
        """Test node assignment with non-existent node."""
        mock_folder_repository.get_by_id.return_value = test_folder
        mock_project_repository.get_by_id.return_value = None
        mock_space_repository.get_by_id.return_value = None

        use_case = AssignNodesToFolderUseCase(
            mock_folder_repository,
            mock_project_repository,
            mock_space_repository,
            mock_session,
        )

        request = AssignNodesToFolderRequest(node_ids=[uuid4()])
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(test_folder.id), request)
