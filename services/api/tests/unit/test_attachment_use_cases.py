"""Unit tests for attachment use cases."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.application.use_cases.attachment import (
    DeleteAttachmentUseCase,
    DownloadAttachmentUseCase,
    GetAttachmentUseCase,
    ListAttachmentsUseCase,
    UploadAttachmentUseCase,
)
from src.domain.entities import Attachment, Issue, User
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_attachment_repository():
    """Mock attachment repository."""
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
def mock_storage_service():
    """Mock storage service."""
    return AsyncMock()


@pytest.fixture
def mock_project_repository():
    """Mock project repository."""
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
def test_attachment(test_issue, test_user):
    """Create a test attachment."""
    return Attachment.create(
        entity_type="issue",
        entity_id=test_issue.id,
        file_name="test_file.pdf",
        original_name="test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        storage_path="attachments/test/test_file.pdf",
        uploaded_by=test_user.id,
    )


class TestUploadAttachmentUseCase:
    """Tests for UploadAttachmentUseCase."""

    @pytest.mark.asyncio
    async def test_upload_attachment_success(
        self,
        mock_attachment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_storage_service,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test successful attachment upload."""
        # Setup mocks
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_user_repository.get_by_id.return_value = test_user

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value

        result_mock = MagicMock()
        result_mock.scalar_one.return_value = user_model
        mock_session.execute.return_value = result_mock

        # Mock storage service
        mock_storage_service.save.return_value = (
            "http://localhost:8000/storage/attachments/test/test_file.pdf"
        )
        mock_storage_service.get_url.return_value = (
            "http://localhost:8000/storage/attachments/test/test_file.pdf"
        )

        # Mock created attachment
        created_attachment = Attachment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            file_name="test_file.pdf",
            original_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            storage_path="attachments/test/test_file.pdf",
            uploaded_by=test_user.id,
        )
        mock_attachment_repository.create.return_value = created_attachment

        # Execute
        use_case = UploadAttachmentUseCase(
            mock_attachment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_storage_service,
            mock_session,
        )

        file_content = b"test file content"
        result = await use_case.execute(
            issue_id=str(test_issue.id),
            file_content=file_content,
            original_filename="test.pdf",
            mime_type="application/pdf",
            user_id=str(test_user.id),
        )

        # Assertions
        assert result.original_name == "test.pdf"
        assert result.file_size == 1024
        assert result.mime_type == "application/pdf"
        assert result.uploaded_by == test_user.id
        mock_attachment_repository.create.assert_called_once()
        mock_storage_service.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_attachment_invalid_file_type(
        self,
        mock_attachment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_storage_service,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test upload with invalid file type."""
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_user_repository.get_by_id.return_value = test_user

        use_case = UploadAttachmentUseCase(
            mock_attachment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_storage_service,
            mock_session,
        )

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(
                issue_id=str(test_issue.id),
                file_content=b"content",
                original_filename="test.exe",
                mime_type="application/x-msdownload",  # Executable file
                user_id=str(test_user.id),
            )

        assert "not allowed" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_upload_attachment_file_too_large(
        self,
        mock_attachment_repository,
        mock_issue_repository,
        mock_user_repository,
        mock_storage_service,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test upload with file too large."""
        mock_issue_repository.get_by_id.return_value = test_issue
        mock_user_repository.get_by_id.return_value = test_user

        use_case = UploadAttachmentUseCase(
            mock_attachment_repository,
            mock_issue_repository,
            mock_user_repository,
            mock_storage_service,
            mock_session,
        )

        # Create file content larger than 10MB
        large_file = b"x" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(
                issue_id=str(test_issue.id),
                file_content=large_file,
                original_filename="large.pdf",
                mime_type="application/pdf",
                user_id=str(test_user.id),
            )

        assert "exceeds maximum" in exc_info.value.message.lower()


class TestGetAttachmentUseCase:
    """Tests for GetAttachmentUseCase."""

    @pytest.mark.asyncio
    async def test_get_attachment_success(
        self,
        mock_attachment_repository,
        mock_storage_service,
        mock_session,
        test_attachment,
        test_user,
    ):
        """Test successful attachment retrieval."""
        mock_attachment_repository.get_by_id.return_value = test_attachment
        mock_storage_service.get_url.return_value = "http://localhost:8000/storage/test.pdf"

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = user_model
        mock_session.execute.return_value = result_mock

        use_case = GetAttachmentUseCase(
            mock_attachment_repository, mock_storage_service, mock_session
        )
        result = await use_case.execute(str(test_attachment.id))

        assert result.id == test_attachment.id
        assert result.original_name == test_attachment.original_name
        assert result.file_size == test_attachment.file_size
        mock_attachment_repository.get_by_id.assert_called_once_with(test_attachment.id)

    @pytest.mark.asyncio
    async def test_get_attachment_not_found(
        self,
        mock_attachment_repository,
        mock_storage_service,
        mock_session,
    ):
        """Test get attachment with non-existent ID."""
        mock_attachment_repository.get_by_id.return_value = None

        use_case = GetAttachmentUseCase(
            mock_attachment_repository, mock_storage_service, mock_session
        )
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()))

        assert "not found" in exc_info.value.message.lower()


class TestListAttachmentsUseCase:
    """Tests for ListAttachmentsUseCase."""

    @pytest.mark.asyncio
    async def test_list_attachments_success(
        self,
        mock_attachment_repository,
        mock_issue_repository,
        mock_storage_service,
        mock_session,
        test_issue,
        test_user,
    ):
        """Test successful attachment listing."""
        mock_issue_repository.get_by_id.return_value = test_issue

        attachment1 = Attachment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            file_name="file1.pdf",
            original_name="test1.pdf",
            file_size=1024,
            mime_type="application/pdf",
            storage_path="attachments/test/file1.pdf",
            uploaded_by=test_user.id,
        )
        attachment2 = Attachment.create(
            entity_type="issue",
            entity_id=test_issue.id,
            file_name="file2.pdf",
            original_name="test2.pdf",
            file_size=2048,
            mime_type="application/pdf",
            storage_path="attachments/test/file2.pdf",
            uploaded_by=test_user.id,
        )

        mock_attachment_repository.get_by_entity_id.return_value = [
            attachment1,
            attachment2,
        ]
        mock_storage_service.get_url.side_effect = [
            "http://localhost:8000/storage/file1.pdf",
            "http://localhost:8000/storage/file2.pdf",
        ]

        # Mock UserModel for response
        user_model = MagicMock()
        user_model.id = test_user.id
        user_model.name = test_user.name
        user_model.email = test_user.email.value

        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [user_model]
        mock_session.execute.return_value = result_mock

        use_case = ListAttachmentsUseCase(
            mock_attachment_repository,
            mock_issue_repository,
            mock_storage_service,
            mock_session,
        )

        result = await use_case.execute(str(test_issue.id))

        assert result.total == 2
        assert len(result.attachments) == 2
        assert result.attachments[0].original_name == "test1.pdf"
        assert result.attachments[1].original_name == "test2.pdf"


class TestDeleteAttachmentUseCase:
    """Tests for DeleteAttachmentUseCase."""

    @pytest.mark.asyncio
    async def test_delete_attachment_success(
        self,
        mock_attachment_repository,
        mock_project_repository,
        mock_storage_service,
        test_attachment,
        test_user,
    ):
        """Test successful attachment deletion."""
        mock_attachment_repository.get_by_id.return_value = test_attachment

        use_case = DeleteAttachmentUseCase(
            mock_attachment_repository, mock_project_repository, mock_storage_service
        )
        await use_case.execute(str(test_attachment.id), test_user.id, is_project_admin=False)

        mock_storage_service.delete.assert_called_once_with(test_attachment.storage_path)
        mock_attachment_repository.delete.assert_called_once_with(test_attachment.id)

    @pytest.mark.asyncio
    async def test_delete_attachment_unauthorized(
        self,
        mock_attachment_repository,
        mock_project_repository,
        mock_storage_service,
        test_attachment,
    ):
        """Test delete attachment by non-uploader and non-admin."""
        mock_attachment_repository.get_by_id.return_value = test_attachment

        use_case = DeleteAttachmentUseCase(
            mock_attachment_repository, mock_project_repository, mock_storage_service
        )

        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(str(test_attachment.id), uuid4(), is_project_admin=False)

        assert "uploader or project admin" in exc_info.value.message.lower()


class TestDownloadAttachmentUseCase:
    """Tests for DownloadAttachmentUseCase."""

    @pytest.mark.asyncio
    async def test_download_attachment_success(
        self,
        mock_attachment_repository,
        mock_storage_service,
        test_attachment,
    ):
        """Test successful attachment download."""
        mock_attachment_repository.get_by_id.return_value = test_attachment
        mock_storage_service.get_file.return_value = b"file content"

        use_case = DownloadAttachmentUseCase(mock_attachment_repository, mock_storage_service)
        file_content, mime_type, original_name = await use_case.execute(str(test_attachment.id))

        assert file_content == b"file content"
        assert mime_type == test_attachment.mime_type
        assert original_name == test_attachment.original_name
        mock_storage_service.get_file.assert_called_once_with(test_attachment.storage_path)

    @pytest.mark.asyncio
    async def test_download_attachment_not_found(
        self,
        mock_attachment_repository,
        mock_storage_service,
    ):
        """Test download attachment with non-existent ID."""
        mock_attachment_repository.get_by_id.return_value = None

        use_case = DownloadAttachmentUseCase(mock_attachment_repository, mock_storage_service)
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(str(uuid4()))

        assert "not found" in exc_info.value.message.lower()
