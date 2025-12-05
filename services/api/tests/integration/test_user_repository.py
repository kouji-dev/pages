"""Integration tests for user repository."""

from uuid import uuid4

import pytest

from src.domain.entities import User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.value_objects import Email, Password
from src.infrastructure.database.repositories import SQLAlchemyUserRepository
from src.infrastructure.security import BcryptPasswordService


@pytest.mark.asyncio
async def test_repository_create_user(db_session) -> None:
    """Test creating a user via repository."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    email = Email("newuser@example.com")
    password = Password("NewPassword123!")
    hashed_password = password_service.hash(password)

    user = User.create(
        email=email,
        password_hash=hashed_password,
        name="New User",
    )

    created_user = await repo.create(user)

    assert created_user.id == user.id
    assert created_user.email == email
    assert created_user.name == "New User"


@pytest.mark.asyncio
async def test_repository_create_duplicate_email(db_session, test_user) -> None:
    """Test creating user with duplicate email raises ConflictException."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    password = Password("AnotherPassword123!")
    hashed_password = password_service.hash(password)

    duplicate_user = User.create(
        email=test_user.email,  # Same email
        password_hash=hashed_password,
        name="Duplicate User",
    )

    with pytest.raises(ConflictException) as exc_info:
        await repo.create(duplicate_user)

    # Check that the exception message mentions email or already registered
    error_message = str(exc_info.value).lower()
    assert "email" in error_message or "already" in error_message


@pytest.mark.asyncio
async def test_repository_get_by_id(db_session, test_user) -> None:
    """Test getting user by ID."""
    repo = SQLAlchemyUserRepository(db_session)

    found_user = await repo.get_by_id(test_user.id)

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


@pytest.mark.asyncio
async def test_repository_get_by_id_not_found(db_session) -> None:
    """Test getting non-existent user by ID returns None."""
    repo = SQLAlchemyUserRepository(db_session)

    non_existent_id = uuid4()
    found_user = await repo.get_by_id(non_existent_id)

    assert found_user is None


@pytest.mark.asyncio
async def test_repository_get_by_email(db_session, test_user) -> None:
    """Test getting user by email."""
    repo = SQLAlchemyUserRepository(db_session)

    found_user = await repo.get_by_email(test_user.email)

    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email


@pytest.mark.asyncio
async def test_repository_get_by_email_not_found(db_session) -> None:
    """Test getting non-existent user by email returns None."""
    repo = SQLAlchemyUserRepository(db_session)

    non_existent_email = Email("nonexistent@example.com")
    found_user = await repo.get_by_email(non_existent_email)

    assert found_user is None


@pytest.mark.asyncio
async def test_repository_update_user(db_session, test_user) -> None:
    """Test updating a user."""
    repo = SQLAlchemyUserRepository(db_session)

    # Update user properties
    test_user.update_name("Updated Name")
    test_user.update_avatar("https://example.com/new-avatar.png")
    test_user.verify()

    updated_user = await repo.update(test_user)

    assert updated_user.name == "Updated Name"
    assert updated_user.avatar_url == "https://example.com/new-avatar.png"
    assert updated_user.is_verified is True


@pytest.mark.asyncio
async def test_repository_update_not_found(db_session) -> None:
    """Test updating non-existent user raises EntityNotFoundException."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    non_existent_user = User.create(
        email=Email("nonexistent@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Non Existent",
    )
    non_existent_user.id = uuid4()  # Set a non-existent ID

    with pytest.raises(EntityNotFoundException):
        await repo.update(non_existent_user)


@pytest.mark.asyncio
async def test_repository_delete_user(db_session, test_user) -> None:
    """Test deleting a user."""
    repo = SQLAlchemyUserRepository(db_session)

    user_id = test_user.id

    # Delete user
    await repo.delete(user_id)

    # Verify user is deleted
    deleted_user = await repo.get_by_id(user_id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_repository_delete_not_found(db_session) -> None:
    """Test deleting non-existent user raises EntityNotFoundException."""
    repo = SQLAlchemyUserRepository(db_session)

    non_existent_id = uuid4()

    with pytest.raises(EntityNotFoundException):
        await repo.delete(non_existent_id)


@pytest.mark.asyncio
async def test_repository_exists_by_email(db_session, test_user) -> None:
    """Test checking if email exists."""
    repo = SQLAlchemyUserRepository(db_session)

    assert await repo.exists_by_email(test_user.email) is True
    assert await repo.exists_by_email(Email("nonexistent@example.com")) is False


@pytest.mark.asyncio
async def test_repository_get_all(db_session) -> None:
    """Test getting all users with pagination."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create multiple users
    users = []
    for i in range(5):
        email = Email(f"user{i}@example.com")
        password = password_service.hash(Password(f"Password{i}123!"))
        user = User.create(
            email=email,
            password_hash=password,
            name=f"User {i}",
        )
        await repo.create(user)
        users.append(user)

    await db_session.flush()

    # Get all users
    all_users = await repo.get_all()

    # Should include at least our created users (plus test_user if it exists)
    assert len(all_users) >= 5

    # Check pagination
    first_page = await repo.get_all(skip=0, limit=2)
    assert len(first_page) <= 2

    second_page = await repo.get_all(skip=2, limit=2)
    assert len(second_page) <= 2


@pytest.mark.asyncio
async def test_repository_get_all_exclude_deleted(db_session) -> None:
    """Test getting all users excludes deleted users."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create a user
    email = Email("active@example.com")
    password = password_service.hash(Password("Password123!"))
    active_user = User.create(
        email=email,
        password_hash=password,
        name="Active User",
    )
    await repo.create(active_user)

    # Create and deactivate another user
    email2 = Email("deleted@example.com")
    deleted_user = User.create(
        email=email2,
        password_hash=password,
        name="Deleted User",
    )
    await repo.create(deleted_user)
    deleted_user.deactivate()
    await repo.update(deleted_user)

    await db_session.flush()

    # Get all users without deleted
    all_users = await repo.get_all(include_deleted=False)
    user_emails = [user.email.value for user in all_users]

    assert active_user.email.value in user_emails
    assert deleted_user.email.value not in user_emails

    # Get all users including deleted
    all_users_with_deleted = await repo.get_all(include_deleted=True)
    user_emails_with_deleted = [user.email.value for user in all_users_with_deleted]

    assert active_user.email.value in user_emails_with_deleted
    assert deleted_user.email.value in user_emails_with_deleted


@pytest.mark.asyncio
async def test_repository_count(db_session) -> None:
    """Test counting users."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Get initial count
    initial_count = await repo.count()

    # Create a new user
    email = Email("counttest@example.com")
    password = password_service.hash(Password("Password123!"))
    user = User.create(
        email=email,
        password_hash=password,
        name="Count Test User",
    )
    await repo.create(user)
    await db_session.flush()

    # Count should increase
    new_count = await repo.count()
    assert new_count == initial_count + 1

    # Count excluding deleted should be same
    count_without_deleted = await repo.count(include_deleted=False)
    assert count_without_deleted == new_count

    # Deactivate user
    user.deactivate()
    await repo.update(user)
    await db_session.flush()

    # Count excluding deleted should decrease
    count_after_deactivate = await repo.count(include_deleted=False)
    assert count_after_deactivate == initial_count

    # Count including deleted should include it
    count_with_deleted = await repo.count(include_deleted=True)
    assert count_with_deleted == new_count


@pytest.mark.asyncio
async def test_repository_search_by_name(db_session) -> None:
    """Test searching users by name."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create users with specific names
    user1 = User.create(
        email=Email("john@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="John Doe",
    )
    user2 = User.create(
        email=Email("jane@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Jane Smith",
    )
    user3 = User.create(
        email=Email("bob@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Bob Johnson",
    )

    await repo.create(user1)
    await repo.create(user2)
    await repo.create(user3)
    await db_session.flush()

    # Search for "John"
    results = await repo.search("John")
    result_names = [user.name for user in results]

    assert "John Doe" in result_names
    assert "Bob Johnson" in result_names  # Contains "John"
    assert "Jane Smith" not in result_names


@pytest.mark.asyncio
async def test_repository_search_by_email(db_session) -> None:
    """Test searching users by email."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create users
    user1 = User.create(
        email=Email("alice@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Alice",
    )
    user2 = User.create(
        email=Email("alice.test@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Alice Test",
    )

    await repo.create(user1)
    await repo.create(user2)
    await db_session.flush()

    # Search for "alice"
    results = await repo.search("alice")
    result_emails = [user.email.value for user in results]

    assert "alice@example.com" in result_emails
    assert "alice.test@example.com" in result_emails


@pytest.mark.asyncio
async def test_repository_search_case_insensitive(db_session) -> None:
    """Test search is case insensitive."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    user = User.create(
        email=Email("testcase@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Test Case",
    )

    await repo.create(user)
    await db_session.flush()

    # Search with different cases
    results_lower = await repo.search("test")
    results_upper = await repo.search("TEST")
    results_mixed = await repo.search("TeSt")

    assert len(results_lower) > 0
    assert len(results_upper) > 0
    assert len(results_mixed) > 0


@pytest.mark.asyncio
async def test_repository_search_pagination(db_session) -> None:
    """Test search with pagination."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create multiple users with similar names
    for i in range(5):
        user = User.create(
            email=Email(f"search{i}@example.com"),
            password_hash=password_service.hash(Password("Password123!")),
            name=f"Search User {i}",
        )
        await repo.create(user)

    await db_session.flush()

    # Get first page
    first_page = await repo.search("Search", skip=0, limit=2)
    assert len(first_page) <= 2

    # Get second page
    second_page = await repo.search("Search", skip=2, limit=2)
    assert len(second_page) <= 2

    # Results should be different
    first_ids = {user.id for user in first_page}
    second_ids = {user.id for user in second_page}
    assert first_ids.isdisjoint(second_ids)


@pytest.mark.asyncio
async def test_repository_search_excludes_deleted(db_session) -> None:
    """Test search excludes deleted users."""
    repo = SQLAlchemyUserRepository(db_session)
    password_service = BcryptPasswordService()

    # Create active user
    active_user = User.create(
        email=Email("activesearch@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Active Search User",
    )
    await repo.create(active_user)

    # Create and delete another user
    deleted_user = User.create(
        email=Email("deletedsearch@example.com"),
        password_hash=password_service.hash(Password("Password123!")),
        name="Deleted Search User",
    )
    await repo.create(deleted_user)
    deleted_user.deactivate()
    await repo.update(deleted_user)

    await db_session.flush()

    # Search should only return active user
    results = await repo.search("Search User")
    result_emails = [user.email.value for user in results]

    assert active_user.email.value in result_emails
    assert deleted_user.email.value not in result_emails
