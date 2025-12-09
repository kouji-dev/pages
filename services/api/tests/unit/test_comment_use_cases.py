"""Unit tests for comment use cases."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.dtos.comment import CreateCommentRequest, UpdateCommentRequest
from src.application.use_cases.comment import (
    CreateCommentUseCase,
    DeleteCommentUseCase,
    GetCommentUseCase,
    ListCommentsUseCase,
    UpdateCommentUseCase,
)
from src.domain.entities import Comment, Issue, User
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_comment_repository():
    """Mock comment repository."""
    return AsyncMock()


@pytest.fixture
def mock_issue_repository():
    """Mock issue repository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
    return AsyncMock()


@pytest.fixture
def mock_notification_repository():
    """Mock notification repository."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session."""
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
def test_issue():
    """Create a test issue."""
    return Issue.create(
        project_id=uuid4(),
        issue_number=1,
        title="Test Issue",
        reporter_id=uuid4(),
    )


@pytest.fixture
def test_comment(test_issue, test_user):
    """Create a test comment."""
    return Comment.create(
        entity_type="issue",
        entity_id=test_issue.id,
        user_id=test_user.id,
        content="This is a test comment",
    )


class TestCreateCommentUseCase:
    """Tests for CreateCommentUseCase."""

    @pytest.mark.asyncio
    async def test_create_comment_success(
        self,
        mock_comment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test successful comment creation."""
        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_user_repository.get_by_id.return_value = test_user

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        result_mock = MagicMock()
        result_mock.scalar_one.return_value = user_model
        mock_session.execute.return_value = result_mock

        # Mock created comment
        created_comment = Comment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            user_id=test_user.id,
            content="New comment",
        )
        mock_comment_repository.create.return_value = created_comment

        # Execute
        use_case = CreateCommentUseCase(
            mock_comment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_notification_repository,
            mock_session,
        )

        request = CreateCommentRequest(content="New comment")
        result = await use_case.execute(str(test_issue.id), request, str(test_user.id))

        # Assertions
        assert result.content == "New comment"
        assert result.user_id == test_user.id
        assert result.issue_id == test_issue.id
        mock_comment_repository.create.assert_called_once()
        mock_issue_repository.get_by_id.assert_called_once_with(test_issue.id)
        mock_user_repository.get_by_id.assert_called_once_with(test_user.id)

    @pytest.mark.asyncio
    async def test_create_comment_issue_not_found(
        self,
        mock_comment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_notification_repository,
        mock_session,
    ):
        """Test comment creation with non-existent issue."""
        mock_issue_repository.get_by_id.return_value = None

        use_case = CreateCommentUseCase(
            mock_comment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_notification_repository,
            mock_session,
        )

        request = CreateCommentRequest(content="New comment")
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()), request, str(uuid4()))

        assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_create_comment_user_not_found(
        self,
        mock_comment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_notification_repository,
        mock_session,
        test_issue,
    ):
        """Test comment creation with non-existent user."""
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_user_repository.get_by_id.return_value = None

        use_case = CreateCommentUseCase(
            mock_comment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_notification_repository,
            mock_session,
        )

        request = CreateCommentRequest(content="New comment")
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(test_issue.id), request, str(uuid4()))

        assert "not found" in exc_info.value.message.lower()


class TestGetCommentUseCase:
    """Tests for GetCommentUseCase."""

    @pytest.mark.asyncio
    async def test_get_comment_success(
        self,
        mock_comment_repository,
        mock_session,
        test_comment,
        test_user,
    ):
        """Test successful comment retrieval."""
        mock_comment_repository.get_by_id.return_value = test_comment

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        result_mock = MagicMock()
        result_mock.scalar_one.return_value = user_model
        mock_session.execute.return_value = result_mock

        use_case = GetCommentUseCase(mock_comment_repository, mock_session)
        result = await use_case.execute(str(test_comment.id))

        assert result.id == test_comment.id
        assert result.content == test_comment.content
        assert result.user_id == test_comment.user_id
        mock_comment_repository.get_by_id.assert_called_once_with(test_comment.id)

    @pytest.mark.asyncio
    async def test_get_comment_not_found(
        self,
        mock_comment_repository,
        mock_session,
    ):
        """Test get comment with non-existent ID."""
        mock_comment_repository.get_by_id.return_value = None

        use_case = GetCommentUseCase(mock_comment_repository, mock_session)
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()))

        assert "not found" in exc_info.value.message.lower()


class TestListCommentsUseCase:
    """Tests for ListCommentsUseCase."""

    @pytest.mark.asyncio
    async def test_list_comments_success(
        self,
        mock_comment_repository,
        mock_issue_repository,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test successful comment listing."""
        mock_issue_repository.get_by_id.return_value = test_issue

        comment1 = Comment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            user_id=test_user.id,
            content="First comment",
        )
        comment2 = Comment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            user_id=test_user.id,
            content="Second comment",
        )

        mock_comment_repository.get_by_issue_id.return_value = [comment1, comment2]
        mock_comment_repository.count_by_issue_id.return_value = 2

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [user_model]
        mock_session.execute.return_value = result_mock

        use_case = ListCommentsUseCase(
            mock_comment_repository,
            mock_issue_repository,
            mock_session,
        )

        result = await use_case.execute(str(test_issue.id), page=1, limit=50)

        assert result.total == 2
        assert len(result.comments) == 2
        assert result.comments[0].content == "First comment"
        assert result.comments[1].content == "Second comment"
        mock_comment_repository.get_by_issue_id.assert_called_once_with(
            test_issue.id, skip=0, limit=50
        )

    @pytest.mark.asyncio
    async def test_list_comments_issue_not_found(
        self,
        mock_comment_repository,
        mock_issue_repository,
        mock_session,
    ):
        """Test list comments with non-existent issue."""
        mock_issue_repository.get_by_id.return_value = None

        use_case = ListCommentsUseCase(
            mock_comment_repository,
            mock_issue_repository,
            mock_session,
        )

        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()))

        assert "not found" in exc_info.value.message.lower()


class TestUpdateCommentUseCase:
    """Tests for UpdateCommentUseCase."""

    @pytest.mark.asyncio
    async def test_update_comment_success(
        self,
        mock_comment_repository,
        mock_session,
        test_comment,
        test_user,
    ):
        """Test successful comment update."""
        mock_comment_repository.get_by_id.return_value = test_comment

        updated_comment = Comment.create(
            entity_type="issue",
            entity_id=test_comment.entity_id,
            user_id=test_comment.user_id,
            content="Updated content",
        )
        updated_comment.is_edited = True
        updated_comment.id = test_comment.id

        mock_comment_repository.update.return_value = updated_comment

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value
        user_model.avatar_url = None

        result_mock = MagicMock()
        result_mock.scalar_one.return_value = user_model
        mock_session.execute.return_value = result_mock

        use_case = UpdateCommentUseCase(mock_comment_repository, mock_session)
        request = UpdateCommentRequest(content="Updated content")
        result = await use_case.execute(str(test_comment.id), request, test_user.id)

        assert result.content == "Updated content"
        assert result.is_edited is True
        mock_comment_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_comment_not_found(
        self,
        mock_comment_repository,
        mock_session,
    ):
        """Test update comment with non-existent ID."""
        mock_comment_repository.get_by_id.return_value = None

        use_case = UpdateCommentUseCase(mock_comment_repository, mock_session)
        request = UpdateCommentRequest(content="Updated content")

        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()), request, uuid4())

        assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_update_comment_unauthorized(
        self,
        mock_comment_repository,
        mock_session,
        test_comment,
    ):
        """Test update comment by non-author."""
        mock_comment_repository.get_by_id.return_value = test_comment

        use_case = UpdateCommentUseCase(mock_comment_repository, mock_session)
        request = UpdateCommentRequest(content="Updated content")

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(test_comment.id), request, uuid4())

        assert "Only the comment author" in exc_info.value.message


class TestDeleteCommentUseCase:
    """Tests for DeleteCommentUseCase."""

    @pytest.mark.asyncio
    async def test_delete_comment_success(
        self,
        mock_comment_repository,
        mock_project_repository,
        test_comment,
        test_user,
    ):
        """Test successful comment deletion."""
        mock_comment_repository.get_by_id.return_value = test_comment

        use_case = DeleteCommentUseCase(mock_comment_repository, mock_project_repository)
        await use_case.execute(str(test_comment.id), test_user.id, is_project_admin=False)

        mock_comment_repository.update.assert_called_once()
        deleted_comment = mock_comment_repository.update.call_args[0][0]
        assert deleted_comment.deleted_at is not None

    @pytest.mark.asyncio
    async def test_delete_comment_not_found(
        self,
        mock_comment_repository,
        mock_project_repository,
    ):
        """Test delete comment with non-existent ID."""
        mock_comment_repository.get_by_id.return_value = None

        use_case = DeleteCommentUseCase(mock_comment_repository, mock_project_repository)

        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()), uuid4(), is_project_admin=False)

        assert "not found" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_delete_comment_unauthorized(
        self,
        mock_comment_repository,
        mock_project_repository,
        test_comment,
    ):
        """Test delete comment by non-author and non-admin."""
        mock_comment_repository.get_by_id.return_value = test_comment

        use_case = DeleteCommentUseCase(mock_comment_repository, mock_project_repository)

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(test_comment.id), uuid4(), is_project_admin=False)

        assert "Only the comment author or project admin" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_delete_comment_as_admin(
        self,
        mock_comment_repository,
        mock_project_repository,
        test_comment,
    ):
        """Test delete comment by project admin."""
        mock_comment_repository.get_by_id.return_value = test_comment

        use_case = DeleteCommentUseCase(mock_comment_repository, mock_project_repository)
        await use_case.execute(str(test_comment.id), uuid4(), is_project_admin=True)

        mock_comment_repository.update.assert_called_once()
        deleted_comment = mock_comment_repository.update.call_args[0][0]
        assert deleted_comment.deleted_at is not None
