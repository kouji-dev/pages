"""Unit tests for template use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.template import CreateTemplateRequest, UpdateTemplateRequest
from src.application.use_cases.template import (
    CreateTemplateUseCase,
    DeleteTemplateUseCase,
    GetTemplateUseCase,
    ListTemplatesUseCase,
    UpdateTemplateUseCase,
)
from src.domain.entities import Organization, Template, User
from src.domain.exceptions import EntityNotFoundException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_template_repository():
    """Mock template repository."""
    return AsyncMock()


@pytest.fixture
def mock_organization_repository():
    """Mock organization repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def test_user():
    """Create a test user."""
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("test@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Test User",
    )


@pytest.fixture
def test_organization():
    """Create a test organization."""
    return Organization.create(
        name="Test Organization",
        slug="test-org",
        description="A test organization",
    )


@pytest.fixture
def test_template(test_organization, test_user):
    """Create a test template."""
    return Template.create(
        organization_id=test_organization.id,
        name="Test Template",
        description="A test template",
        content="# Template Content",
        created_by=test_user.id,
    )


class TestCreateTemplateUseCase:
    """Tests for CreateTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_create_template_success(
        self,
        mock_template_repository,
        mock_organization_repository,
        mock_user_repository,
        test_user,
        test_organization,
    ):
        """Test successful template creation."""
        request = CreateTemplateRequest(
            organization_id=test_organization.id,
            name="New Template",
            description="Template description",
            content="# Template Content",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = test_organization

        created_template = Template.create(
            organization_id=request.organization_id,
            name=request.name,
            description=request.description,
            content=request.content,
            created_by=test_user.id,
        )
        mock_template_repository.create.return_value = created_template

        use_case = CreateTemplateUseCase(
            mock_template_repository,
            mock_organization_repository,
            mock_user_repository,
        )

        result = await use_case.execute(request, str(test_user.id))

        assert result.name == "New Template"
        assert result.description == "Template description"
        assert result.content == "# Template Content"
        assert result.organization_id == test_organization.id
        mock_template_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_template_organization_not_found(
        self,
        mock_template_repository,
        mock_organization_repository,
        mock_user_repository,
        test_user,
    ):
        """Test template creation fails when organization not found."""
        request = CreateTemplateRequest(
            organization_id=uuid4(),
            name="New Template",
        )
        mock_user_repository.get_by_id.return_value = test_user
        mock_organization_repository.get_by_id.return_value = None

        use_case = CreateTemplateUseCase(
            mock_template_repository,
            mock_organization_repository,
            mock_user_repository,
        )

        with pytest.raises(EntityNotFoundException, match="Organization"):
            await use_case.execute(request, str(test_user.id))


class TestGetTemplateUseCase:
    """Tests for GetTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_get_template_success(self, mock_template_repository, test_template):
        """Test successful template retrieval."""
        mock_template_repository.get_by_id.return_value = test_template

        use_case = GetTemplateUseCase(mock_template_repository)

        result = await use_case.execute(str(test_template.id))

        assert result.id == test_template.id
        assert result.name == test_template.name
        mock_template_repository.get_by_id.assert_called_once_with(test_template.id)

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, mock_template_repository):
        """Test template retrieval fails when template not found."""
        template_id = uuid4()
        mock_template_repository.get_by_id.return_value = None

        use_case = GetTemplateUseCase(mock_template_repository)

        with pytest.raises(EntityNotFoundException, match="Template"):
            await use_case.execute(str(template_id))


class TestListTemplatesUseCase:
    """Tests for ListTemplatesUseCase."""

    @pytest.mark.asyncio
    async def test_list_templates_success(self, mock_template_repository, test_organization):
        """Test successful template listing."""
        template1 = Template.create(
            organization_id=test_organization.id, name="Template 1", created_by=uuid4()
        )
        template2 = Template.create(
            organization_id=test_organization.id, name="Template 2", created_by=uuid4()
        )

        mock_template_repository.get_all.return_value = [template1, template2]
        mock_template_repository.count.return_value = 2

        use_case = ListTemplatesUseCase(mock_template_repository)

        result = await use_case.execute(str(test_organization.id), page=1, limit=20)

        assert len(result.templates) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.limit == 20


class TestUpdateTemplateUseCase:
    """Tests for UpdateTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_update_template_success(self, mock_template_repository, test_template):
        """Test successful template update."""
        mock_template_repository.get_by_id.return_value = test_template

        updated_template = Template.create(
            organization_id=test_template.organization_id,
            name="Updated Template",
            description="Updated description",
            content="Updated content",
            created_by=test_template.created_by,
        )
        updated_template.id = test_template.id
        mock_template_repository.update.return_value = updated_template

        use_case = UpdateTemplateUseCase(mock_template_repository)

        request = UpdateTemplateRequest(name="Updated Template", description="Updated description")
        result = await use_case.execute(str(test_template.id), request)

        assert result.name == "Updated Template"
        assert result.description == "Updated description"
        mock_template_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_template_not_found(self, mock_template_repository):
        """Test template update fails when template not found."""
        template_id = uuid4()
        mock_template_repository.get_by_id.return_value = None

        use_case = UpdateTemplateUseCase(mock_template_repository)

        request = UpdateTemplateRequest(name="Updated Template")
        with pytest.raises(EntityNotFoundException, match="Template"):
            await use_case.execute(str(template_id), request)


class TestDeleteTemplateUseCase:
    """Tests for DeleteTemplateUseCase."""

    @pytest.mark.asyncio
    async def test_delete_template_success(self, mock_template_repository, test_template):
        """Test successful template deletion."""
        mock_template_repository.get_by_id.return_value = test_template
        mock_template_repository.update = AsyncMock()

        use_case = DeleteTemplateUseCase(mock_template_repository)

        await use_case.execute(str(test_template.id))

        assert test_template.deleted_at is not None
        mock_template_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self, mock_template_repository):
        """Test template deletion fails when template not found."""
        template_id = uuid4()
        mock_template_repository.get_by_id.return_value = None

        use_case = DeleteTemplateUseCase(mock_template_repository)

        with pytest.raises(EntityNotFoundException, match="Template"):
            await use_case.execute(str(template_id))
