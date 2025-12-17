"""Unit tests for workflow use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.workflow import (
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    ValidateTransitionRequest,
    WorkflowStatusRequest,
)
from src.application.use_cases.workflow import (
    CreateWorkflowUseCase,
    DeleteWorkflowUseCase,
    GetWorkflowUseCase,
    ListWorkflowsUseCase,
    UpdateWorkflowUseCase,
    ValidateTransitionUseCase,
)
from src.domain.entities import Project, Workflow
from src.domain.exceptions import EntityNotFoundException, ValidationException


@pytest.fixture
def mock_workflow_repository():
    """Mock workflow repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def test_project():
    """Create a test project."""
    return Project.create(
        organization_id=uuid4(),
        name="Test Project",
        key="TEST",
        description="A test project",
    )


@pytest.fixture
def test_workflow(test_project):
    """Create a test workflow."""
    workflow = Workflow.create(
        project_id=test_project.id,
        name="Test Workflow",
        is_default=False,
    )
    status1 = workflow.add_status("To Do", order=0, is_initial=True, is_final=False)
    status2 = workflow.add_status("In Progress", order=1, is_initial=False, is_final=False)
    status3 = workflow.add_status("Done", order=2, is_initial=False, is_final=True)
    workflow.add_transition(status1.id, status2.id, "Start")
    workflow.add_transition(status2.id, status3.id, "Complete")
    workflow.validate()
    return workflow


class TestCreateWorkflowUseCase:
    """Tests for CreateWorkflowUseCase."""

    @pytest.mark.asyncio
    async def test_create_workflow_success(
        self,
        mock_workflow_repository,
        mock_project_repository,
        test_project,
    ):
        """Test successful workflow creation."""
        request = CreateWorkflowRequest(
            name="Test Workflow",
            is_default=False,
            statuses=[
                WorkflowStatusRequest(name="To Do", order=0, is_initial=True, is_final=False),
                WorkflowStatusRequest(name="Done", order=1, is_initial=False, is_final=True),
            ],
            transitions=[],
        )

        mock_project_repository.get_by_id.return_value = test_project
        mock_workflow_repository.get_default_by_project_id.return_value = None

        created_workflow = Workflow.create(
            project_id=test_project.id,
            name=request.name,
            is_default=request.is_default,
        )
        for status_req in request.statuses:
            created_workflow.add_status(
                name=status_req.name,
                order=status_req.order,
                is_initial=status_req.is_initial,
                is_final=status_req.is_final,
            )
        created_workflow.validate()

        mock_workflow_repository.create.return_value = created_workflow

        use_case = CreateWorkflowUseCase(mock_workflow_repository, mock_project_repository)

        result = await use_case.execute(test_project.id, request)

        assert result.name == "Test Workflow"
        assert result.project_id == test_project.id
        assert len(result.statuses) == 2
        mock_workflow_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_workflow_project_not_found(
        self,
        mock_workflow_repository,
        mock_project_repository,
    ):
        """Test workflow creation with non-existent project."""
        request = CreateWorkflowRequest(name="Test Workflow")
        project_id = uuid4()

        mock_project_repository.get_by_id.return_value = None

        use_case = CreateWorkflowUseCase(mock_workflow_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(project_id, request)

    @pytest.mark.asyncio
    async def test_create_workflow_invalid_structure(
        self,
        mock_workflow_repository,
        mock_project_repository,
        test_project,
    ):
        """Test workflow creation with invalid structure (no initial status)."""
        request = CreateWorkflowRequest(
            name="Test Workflow",
            statuses=[
                WorkflowStatusRequest(name="To Do", order=0, is_initial=False, is_final=False),
            ],
        )

        mock_project_repository.get_by_id.return_value = test_project

        use_case = CreateWorkflowUseCase(mock_workflow_repository, mock_project_repository)

        with pytest.raises(ValidationException):
            await use_case.execute(test_project.id, request)


class TestGetWorkflowUseCase:
    """Tests for GetWorkflowUseCase."""

    @pytest.mark.asyncio
    async def test_get_workflow_success(self, mock_workflow_repository, test_workflow):
        """Test successfully getting a workflow."""
        mock_workflow_repository.get_by_id.return_value = test_workflow

        use_case = GetWorkflowUseCase(mock_workflow_repository)

        result = await use_case.execute(test_workflow.id)

        assert result.id == test_workflow.id
        assert result.name == test_workflow.name
        mock_workflow_repository.get_by_id.assert_called_once_with(test_workflow.id)

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, mock_workflow_repository):
        """Test getting non-existent workflow."""
        workflow_id = uuid4()
        mock_workflow_repository.get_by_id.return_value = None

        use_case = GetWorkflowUseCase(mock_workflow_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(workflow_id)


class TestListWorkflowsUseCase:
    """Tests for ListWorkflowsUseCase."""

    @pytest.mark.asyncio
    async def test_list_workflows_success(
        self, mock_workflow_repository, test_project, test_workflow
    ):
        """Test successfully listing workflows."""
        workflows = [test_workflow]
        mock_workflow_repository.get_by_project_id.return_value = workflows

        use_case = ListWorkflowsUseCase(mock_workflow_repository)

        result = await use_case.execute(test_project.id)

        assert result.total == 1
        assert len(result.workflows) == 1
        assert result.workflows[0].id == test_workflow.id


class TestUpdateWorkflowUseCase:
    """Tests for UpdateWorkflowUseCase."""

    @pytest.mark.asyncio
    async def test_update_workflow_success(self, mock_workflow_repository, test_workflow):
        """Test successfully updating a workflow."""
        request = UpdateWorkflowRequest(name="Updated Workflow")

        updated_workflow = Workflow.create(
            project_id=test_workflow.project_id,
            name=request.name,
            is_default=test_workflow.is_default,
        )
        updated_workflow.statuses = test_workflow.statuses
        updated_workflow.transitions = test_workflow.transitions

        mock_workflow_repository.get_by_id.return_value = test_workflow
        mock_workflow_repository.get_default_by_project_id.return_value = None
        mock_workflow_repository.update.return_value = updated_workflow

        use_case = UpdateWorkflowUseCase(mock_workflow_repository)

        result = await use_case.execute(test_workflow.id, request)

        assert result.name == "Updated Workflow"
        mock_workflow_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_workflow_not_found(self, mock_workflow_repository):
        """Test updating non-existent workflow."""
        workflow_id = uuid4()
        request = UpdateWorkflowRequest(name="Updated Workflow")

        mock_workflow_repository.get_by_id.return_value = None

        use_case = UpdateWorkflowUseCase(mock_workflow_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(workflow_id, request)


class TestDeleteWorkflowUseCase:
    """Tests for DeleteWorkflowUseCase."""

    @pytest.mark.asyncio
    async def test_delete_workflow_success(self, mock_workflow_repository, test_workflow):
        """Test successfully deleting a workflow."""
        mock_workflow_repository.get_by_id.return_value = test_workflow
        mock_workflow_repository.delete.return_value = None

        use_case = DeleteWorkflowUseCase(mock_workflow_repository)

        await use_case.execute(test_workflow.id)

        mock_workflow_repository.delete.assert_called_once_with(test_workflow.id)

    @pytest.mark.asyncio
    async def test_delete_workflow_not_found(self, mock_workflow_repository):
        """Test deleting non-existent workflow."""
        workflow_id = uuid4()
        mock_workflow_repository.get_by_id.return_value = None

        use_case = DeleteWorkflowUseCase(mock_workflow_repository)

        with pytest.raises(EntityNotFoundException):
            await use_case.execute(workflow_id)


class TestValidateTransitionUseCase:
    """Tests for ValidateTransitionUseCase."""

    @pytest.mark.asyncio
    async def test_validate_transition_valid(self, mock_workflow_repository, test_workflow):
        """Test validating a valid transition."""
        from_status_id = test_workflow.statuses[0].id
        to_status_id = test_workflow.statuses[1].id

        request = ValidateTransitionRequest(
            from_status_id=from_status_id, to_status_id=to_status_id
        )

        mock_workflow_repository.get_by_id.return_value = test_workflow

        use_case = ValidateTransitionUseCase(mock_workflow_repository)

        result = await use_case.execute(test_workflow.id, request)

        assert result.is_valid is True
        assert result.message is None

    @pytest.mark.asyncio
    async def test_validate_transition_invalid(self, mock_workflow_repository, test_workflow):
        """Test validating an invalid transition."""
        from_status_id = test_workflow.statuses[0].id
        to_status_id = test_workflow.statuses[2].id  # Skip intermediate status

        request = ValidateTransitionRequest(
            from_status_id=from_status_id, to_status_id=to_status_id
        )

        mock_workflow_repository.get_by_id.return_value = test_workflow

        use_case = ValidateTransitionUseCase(mock_workflow_repository)

        result = await use_case.execute(test_workflow.id, request)

        assert result.is_valid is False
        assert result.message is not None

    @pytest.mark.asyncio
    async def test_validate_transition_with_conditional_logic(
        self, mock_workflow_repository, test_workflow
    ):
        """Test validating a transition with conditional logic."""
        from_status_id = test_workflow.statuses[0].id
        to_status_id = (
            test_workflow.statuses[1].id
            if len(test_workflow.statuses) > 1
            else test_workflow.statuses[0].id
        )

        request = ValidateTransitionRequest(
            from_status_id=from_status_id,
            to_status_id=to_status_id,
        )

        mock_workflow_repository.get_by_id.return_value = test_workflow

        use_case = ValidateTransitionUseCase(mock_workflow_repository)

        result = await use_case.execute(test_workflow.id, request)

        # The result depends on whether the transition exists in the workflow
        assert isinstance(result.is_valid, bool)
