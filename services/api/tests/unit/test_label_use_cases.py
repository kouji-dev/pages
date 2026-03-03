"""Unit tests for label use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.label import CreateLabelRequest, UpdateLabelRequest
from src.application.use_cases.label import (
    AddLabelToIssueUseCase,
    CreateLabelUseCase,
    DeleteLabelUseCase,
    GetLabelUseCase,
    ListIssueLabelsUseCase,
    ListProjectLabelsUseCase,
    RemoveLabelFromIssueUseCase,
    UpdateLabelUseCase,
)
from src.domain.entities import Issue, Label, Project
from src.domain.exceptions import EntityNotFoundException


@pytest.fixture
def mock_label_repository():
    """Mock label repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
    )


@pytest.fixture
def test_label(test_project):
    """Create a test label."""
    return Label.create(
        project_id=test_project.id,
        name="bug",
        color="#ff0000",
        description="Bug fix",
    )


class TestCreateLabelUseCase:
    """Tests for CreateLabelUseCase."""

    @pytest.mark.asyncio
    async def test_create_label_success(
        self, mock_label_repository, mock_project_repository, test_project
    ):
        """Test successful label creation."""
        request = CreateLabelRequest(
            name="bug",
            color="#ff0000",
            description="Bug fix",
        )
        mock_project_repository.get_by_id.return_value = test_project
        created = Label.create(
            project_id=test_project.id,
            name=request.name,
            color=request.color,
            description=request.description,
        )
        mock_label_repository.create.return_value = created

        use_case = CreateLabelUseCase(mock_label_repository, mock_project_repository)
        result = await use_case.execute(str(test_project.id), request)

        assert result.name == "bug"
        assert result.color == "#ff0000"
        assert result.description == "Bug fix"
        mock_label_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_label_project_not_found(
        self, mock_label_repository, mock_project_repository
    ):
        """Test label creation fails when project not found."""
        mock_project_repository.get_by_id.return_value = None
        request = CreateLabelRequest(name="bug", color="#ff0000")

        use_case = CreateLabelUseCase(mock_label_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()), request)


class TestGetLabelUseCase:
    """Tests for GetLabelUseCase."""

    @pytest.mark.asyncio
    async def test_get_label_success(self, mock_label_repository, test_label):
        """Test successful label retrieval."""
        mock_label_repository.get_by_id.return_value = test_label
        use_case = GetLabelUseCase(mock_label_repository)
        result = await use_case.execute(str(test_label.id))
        assert result.id == test_label.id
        assert result.name == test_label.name

    @pytest.mark.asyncio
    async def test_get_label_not_found(self, mock_label_repository):
        """Test get label when not found."""
        mock_label_repository.get_by_id.return_value = None
        use_case = GetLabelUseCase(mock_label_repository)
        with pytest.raises(EntityNotFoundException, match="Label"):
            await use_case.execute(str(uuid4()))


class TestListProjectLabelsUseCase:
    """Tests for ListProjectLabelsUseCase."""

    @pytest.mark.asyncio
    async def test_list_project_labels_success(
        self, mock_label_repository, mock_project_repository, test_project, test_label
    ):
        """Test listing project labels."""
        mock_project_repository.get_by_id.return_value = test_project
        mock_label_repository.get_by_project.return_value = [test_label]
        mock_label_repository.count_by_project.return_value = 1

        use_case = ListProjectLabelsUseCase(mock_label_repository, mock_project_repository)
        result = await use_case.execute(str(test_project.id), page=1, limit=20)

        assert result.total == 1
        assert len(result.labels) == 1
        assert result.labels[0].name == "bug"

    @pytest.mark.asyncio
    async def test_list_project_labels_project_not_found(
        self, mock_label_repository, mock_project_repository
    ):
        """Test list labels when project not found."""
        mock_project_repository.get_by_id.return_value = None
        use_case = ListProjectLabelsUseCase(mock_label_repository, mock_project_repository)
        with pytest.raises(EntityNotFoundException, match="Project"):
            await use_case.execute(str(uuid4()))


class TestUpdateLabelUseCase:
    """Tests for UpdateLabelUseCase."""

    @pytest.mark.asyncio
    async def test_update_label_success(self, mock_label_repository, test_label):
        """Test successful label update."""
        mock_label_repository.get_by_id.return_value = test_label
        test_label.update_name("feature")
        test_label.update_color("#00ff00")
        mock_label_repository.update.return_value = test_label

        use_case = UpdateLabelUseCase(mock_label_repository)
        request = UpdateLabelRequest(name="feature", color="#00ff00")
        await use_case.execute(str(test_label.id), request)

        mock_label_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_label_not_found(self, mock_label_repository):
        """Test update label when not found."""
        mock_label_repository.get_by_id.return_value = None
        use_case = UpdateLabelUseCase(mock_label_repository)
        request = UpdateLabelRequest(name="new")
        with pytest.raises(EntityNotFoundException, match="Label"):
            await use_case.execute(str(uuid4()), request)


class TestDeleteLabelUseCase:
    """Tests for DeleteLabelUseCase."""

    @pytest.mark.asyncio
    async def test_delete_label_success(self, mock_label_repository, test_label):
        """Test successful label deletion."""
        mock_label_repository.get_by_id.return_value = test_label
        use_case = DeleteLabelUseCase(mock_label_repository)
        await use_case.execute(str(test_label.id))
        mock_label_repository.delete.assert_called_once_with(test_label.id)

    @pytest.mark.asyncio
    async def test_delete_label_not_found(self, mock_label_repository):
        """Test delete label when not found."""
        mock_label_repository.get_by_id.return_value = None
        use_case = DeleteLabelUseCase(mock_label_repository)
        with pytest.raises(EntityNotFoundException, match="Label"):
            await use_case.execute(str(uuid4()))


class TestAddLabelToIssueUseCase:
    """Tests for AddLabelToIssueUseCase."""

    @pytest.mark.asyncio
    async def test_add_label_to_issue_success(
        self, mock_label_repository, mock_issue_repository, test_label
    ):
        """Test adding label to issue."""
        issue = Issue.create(
            project_id=test_label.project_id,
            issue_number=1,
            title="Fix bug",
            type="bug",
        )
        mock_issue_repository.get_by_id.return_value = issue
        use_case = AddLabelToIssueUseCase(mock_label_repository, mock_issue_repository)
        await use_case.execute(str(issue.id), str(test_label.id))
        mock_label_repository.add_label_to_issue.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_label_to_issue_issue_not_found(
        self, mock_label_repository, mock_issue_repository
    ):
        """Test add label when issue not found."""
        mock_issue_repository.get_by_id.return_value = None
        use_case = AddLabelToIssueUseCase(mock_label_repository, mock_issue_repository)
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(str(uuid4()), str(uuid4()))


class TestRemoveLabelFromIssueUseCase:
    """Tests for RemoveLabelFromIssueUseCase."""

    @pytest.mark.asyncio
    async def test_remove_label_from_issue_success(self, mock_label_repository, test_label):
        """Test removing label from issue."""
        use_case = RemoveLabelFromIssueUseCase(mock_label_repository)
        issue_id = uuid4()
        await use_case.execute(str(issue_id), str(test_label.id))
        mock_label_repository.remove_label_from_issue.assert_called_once_with(
            issue_id, test_label.id
        )


class TestListIssueLabelsUseCase:
    """Tests for ListIssueLabelsUseCase."""

    @pytest.mark.asyncio
    async def test_list_issue_labels_success(
        self, mock_label_repository, mock_issue_repository, test_label
    ):
        """Test listing issue labels."""
        issue = Issue.create(
            project_id=test_label.project_id,
            issue_number=1,
            title="Fix",
        )
        mock_issue_repository.get_by_id.return_value = issue
        mock_label_repository.get_labels_for_issue.return_value = [test_label]

        use_case = ListIssueLabelsUseCase(mock_label_repository, mock_issue_repository)
        result = await use_case.execute(str(issue.id))
        assert len(result) == 1
        assert result[0].name == "bug"

    @pytest.mark.asyncio
    async def test_list_issue_labels_issue_not_found(
        self, mock_label_repository, mock_issue_repository
    ):
        """Test list issue labels when issue not found."""
        mock_issue_repository.get_by_id.return_value = None
        use_case = ListIssueLabelsUseCase(mock_label_repository, mock_issue_repository)
        with pytest.raises(EntityNotFoundException, match="Issue"):
            await use_case.execute(str(uuid4()))
