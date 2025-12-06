"""Unit tests for invitation use cases."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from src.application.dtos.invitation import SendInvitationRequest
from src.application.use_cases.organization import (
    AcceptInvitationUseCase,
    CancelInvitationUseCase,
    ListInvitationsUseCase,
    SendInvitationUseCase,
)
from src.domain.entities import Invitation, Organization, User
from src.domain.exceptions import (
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)
from src.domain.value_objects import Email, HashedPassword


@pytest.fixture
def mock_invitation_repository():
    """Mock invitation repository."""
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
def mock_session():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def test_organization():
    """Create a test organization."""
    return Organization.create(
        name="Test Organization",
        slug="test-org",
    )


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
def invited_user():
    """Create an invited user."""
    valid_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4yKJeyeQUzK6M5em"
    return User(
        id=uuid4(),
        email=Email("invited@example.com"),
        password_hash=HashedPassword(valid_hash),
        name="Invited User",
    )


@pytest.fixture
def test_invitation(test_organization, test_user):
    """Create a test invitation."""
    return Invitation.create(
        organization_id=test_organization.id,
        email=Email("invited@example.com"),
        token="test-token-123",
        role="member",
        invited_by=test_user.id,
        expires_in_days=7,
    )


class TestSendInvitationUseCase:
    """Tests for SendInvitationUseCase."""

    @pytest.mark.asyncio
    async def test_send_invitation_success(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_user,
    ):
        """Test successfully sending an invitation."""
        # Arrange
        org_id = str(test_organization.id)
        invited_by_id = str(test_user.id)
        request = SendInvitationRequest(email="invited@example.com", role="member")

        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_email.return_value = None  # User doesn't exist yet
        mock_invitation_repository.get_pending_by_organization_and_email.return_value = None
        mock_invitation_repository.create.return_value = Invitation.create(
            organization_id=test_organization.id,
            email=Email(request.email),
            token="generated-token",
            role=request.role,
            invited_by=test_user.id,
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        use_case = SendInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act
        result = await use_case.execute(org_id, request, invited_by_id)

        # Assert
        assert result.email == request.email
        assert result.role == request.role
        assert result.organization_id == test_organization.id
        mock_organization_repository.get_by_id.assert_called_once()
        mock_invitation_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_invitation_organization_not_found(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
    ):
        """Test sending invitation when organization doesn't exist."""
        # Arrange
        org_id = str(uuid4())
        request = SendInvitationRequest(email="invited@example.com", role="member")

        mock_organization_repository.get_by_id.return_value = None

        use_case = SendInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(org_id, request, str(uuid4()))

        assert "Organization" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_invitation_invalid_role(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
    ):
        """Test sending invitation with invalid role."""
        # Arrange
        org_id = str(test_organization.id)
        request = SendInvitationRequest(email="invited@example.com", role="invalid-role")

        mock_organization_repository.get_by_id.return_value = test_organization

        use_case = SendInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(org_id, request, str(uuid4()))

        assert "Invalid role" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_invitation_user_already_member(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        invited_user,
    ):
        """Test sending invitation when user is already a member."""
        # Arrange
        from src.infrastructure.database.models import OrganizationMemberModel

        org_id = str(test_organization.id)
        request = SendInvitationRequest(email=invited_user.email.value, role="member")

        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_email.return_value = invited_user
        mock_member = Mock(spec=OrganizationMemberModel)
        mock_session.execute.return_value.scalar_one_or_none.return_value = mock_member

        use_case = SendInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await use_case.execute(org_id, request, str(uuid4()))

        assert "already a member" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_invitation_pending_exists(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_invitation,
    ):
        """Test sending invitation when pending invitation already exists."""
        # Arrange
        org_id = str(test_organization.id)
        request = SendInvitationRequest(email=test_invitation.email.value, role="member")

        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_email.return_value = None
        mock_invitation_repository.get_pending_by_organization_and_email.return_value = (
            test_invitation
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        use_case = SendInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            await use_case.execute(org_id, request, str(uuid4()))

        assert "Pending invitation already exists" in str(exc_info.value)


class TestAcceptInvitationUseCase:
    """Tests for AcceptInvitationUseCase."""

    @pytest.mark.asyncio
    async def test_accept_invitation_success(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_invitation,
        invited_user,
    ):
        """Test successfully accepting an invitation."""
        # Arrange
        token = test_invitation.token
        user_id = str(invited_user.id)

        mock_invitation_repository.get_by_token.return_value = test_invitation
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = invited_user
        # Mock session.execute to return None (no existing member)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        mock_session.add = Mock()  # Make add synchronous
        mock_session.flush = AsyncMock()  # Make flush async
        mock_invitation_repository.update.return_value = test_invitation

        use_case = AcceptInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act
        result = await use_case.execute(token, user_id)

        # Assert
        assert result.organization_id == test_organization.id
        assert result.organization_name == test_organization.name
        assert result.role == test_invitation.role
        mock_invitation_repository.get_by_token.assert_called_once_with(token)
        mock_invitation_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_accept_invitation_not_found(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
    ):
        """Test accepting non-existent invitation."""
        # Arrange
        token = "invalid-token"

        mock_invitation_repository.get_by_token.return_value = None

        use_case = AcceptInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(token, str(uuid4()))

        assert "Invitation" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_accept_invitation_expired(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_invitation,
    ):
        """Test accepting expired invitation."""
        # Arrange
        # Create expired invitation by modifying expires_at after creation
        expired_invitation = Invitation(
            id=test_invitation.id,
            organization_id=test_invitation.organization_id,
            email=test_invitation.email,
            token=test_invitation.token,
            role=test_invitation.role,
            invited_by=test_invitation.invited_by,
            expires_at=datetime.now(UTC) + timedelta(days=7),  # Valid initially
            accepted_at=None,
            created_at=test_invitation.created_at,
            updated_at=test_invitation.updated_at,
        )
        # Manually set expired date (bypassing validation)
        object.__setattr__(expired_invitation, "expires_at", datetime.now(UTC) - timedelta(days=1))

        token = expired_invitation.token
        mock_invitation_repository.get_by_token.return_value = expired_invitation

        use_case = AcceptInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(token, str(uuid4()))

        assert "expired" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_accept_invitation_email_mismatch(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_organization,
        test_invitation,
        test_user,
    ):
        """Test accepting invitation with email mismatch."""
        # Arrange
        token = test_invitation.token
        user_id = str(test_user.id)  # Different email

        mock_invitation_repository.get_by_token.return_value = test_invitation
        mock_organization_repository.get_by_id.return_value = test_organization
        mock_user_repository.get_by_id.return_value = test_user

        use_case = AcceptInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(token, user_id)

        assert "email" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_accept_invitation_user_not_authenticated(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        mock_user_repository,
        mock_session,
        test_invitation,
    ):
        """Test accepting invitation without authentication."""
        # Arrange
        token = test_invitation.token

        mock_invitation_repository.get_by_token.return_value = test_invitation

        use_case = AcceptInvitationUseCase(
            mock_invitation_repository,
            mock_organization_repository,
            mock_user_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(token, None)

        assert "authenticated" in str(exc_info.value).lower()


class TestListInvitationsUseCase:
    """Tests for ListInvitationsUseCase."""

    @pytest.mark.asyncio
    async def test_list_invitations_success(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        test_organization,
        test_invitation,
    ):
        """Test successfully listing invitations."""
        # Arrange
        org_id = str(test_organization.id)

        mock_organization_repository.get_by_id.return_value = test_organization
        mock_invitation_repository.list_by_organization.return_value = [test_invitation]

        use_case = ListInvitationsUseCase(mock_invitation_repository, mock_organization_repository)

        # Act
        result = await use_case.execute(org_id, page=1, limit=20, pending_only=True)

        # Assert
        assert len(result.invitations) == 1
        assert result.invitations[0].email == test_invitation.email.value
        assert result.page == 1
        assert result.limit == 20

    @pytest.mark.asyncio
    async def test_list_invitations_organization_not_found(
        self,
        mock_invitation_repository,
        mock_organization_repository,
    ):
        """Test listing invitations for non-existent organization."""
        # Arrange
        org_id = str(uuid4())

        mock_organization_repository.get_by_id.return_value = None

        use_case = ListInvitationsUseCase(mock_invitation_repository, mock_organization_repository)

        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(org_id)

        assert "Organization" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_invitations_invalid_page(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        test_organization,
    ):
        """Test listing invitations with invalid page number."""
        # Arrange
        org_id = str(test_organization.id)

        mock_organization_repository.get_by_id.return_value = test_organization

        use_case = ListInvitationsUseCase(mock_invitation_repository, mock_organization_repository)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(org_id, page=0)

        assert "Page" in str(exc_info.value)


class TestCancelInvitationUseCase:
    """Tests for CancelInvitationUseCase."""

    @pytest.mark.asyncio
    async def test_cancel_invitation_success(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        test_invitation,
    ):
        """Test successfully canceling an invitation."""
        # Arrange
        invitation_id = str(test_invitation.id)

        mock_invitation_repository.get_by_id.return_value = test_invitation
        mock_invitation_repository.delete = AsyncMock()

        use_case = CancelInvitationUseCase(mock_invitation_repository, mock_organization_repository)

        # Act
        await use_case.execute(invitation_id)

        # Assert
        mock_invitation_repository.get_by_id.assert_called_once()
        mock_invitation_repository.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_invitation_not_found(
        self,
        mock_invitation_repository,
        mock_organization_repository,
    ):
        """Test canceling non-existent invitation."""
        # Arrange
        invitation_id = str(uuid4())

        mock_invitation_repository.get_by_id.return_value = None

        use_case = CancelInvitationUseCase(mock_invitation_repository, mock_organization_repository)

        # Act & Assert
        with pytest.raises(EntityNotFoundException) as exc_info:
            await use_case.execute(invitation_id)

        assert "Invitation" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cancel_invitation_already_accepted(
        self,
        mock_invitation_repository,
        mock_organization_repository,
        test_invitation,
    ):
        """Test canceling already accepted invitation."""
        # Arrange
        # Mark invitation as accepted
        accepted_invitation = Invitation(
            id=test_invitation.id,
            organization_id=test_invitation.organization_id,
            email=test_invitation.email,
            token=test_invitation.token,
            role=test_invitation.role,
            invited_by=test_invitation.invited_by,
            expires_at=test_invitation.expires_at,
            accepted_at=datetime.now(UTC),  # Accepted
            created_at=test_invitation.created_at,
            updated_at=test_invitation.updated_at,
        )

        invitation_id = str(accepted_invitation.id)

        mock_invitation_repository.get_by_id.return_value = accepted_invitation

        use_case = CancelInvitationUseCase(mock_invitation_repository, mock_organization_repository)

        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            await use_case.execute(invitation_id)

        assert "already been accepted" in str(exc_info.value)
