"""SQLAlchemy implementation of UserRepository."""

import json
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import User
from src.domain.exceptions import ConflictException, EntityNotFoundException
from src.domain.repositories import UserRepository
from src.domain.value_objects import Email, HashedPassword
from src.domain.value_objects.language import Language
from src.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository.

    Adapts the domain UserRepository interface to SQLAlchemy.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, user: User) -> User:
        """Create a new user in the database.

        Args:
            user: User domain entity

        Returns:
            Created user with persisted data

        Raises:
            ConflictException: If email already exists
        """
        # Check for existing email
        if await self.exists_by_email(user.email):
            raise ConflictException("Email already registered", field="email")

        # Create model from entity
        model = UserModel(
            id=user.id,
            email=str(user.email),
            password_hash=user.password_hash.value,
            name=user.name,
            avatar_url=user.avatar_url,
            preferences=json.dumps(user.preferences) if user.preferences else None,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User if found, None otherwise
        """
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_email(self, email: Email) -> User | None:
        """Get user by email.

        Args:
            email: User email value object

        Returns:
            User if found, None otherwise
        """
        result = await self._session.execute(select(UserModel).where(UserModel.email == str(email)))
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User entity with updated data

        Returns:
            Updated user

        Raises:
            EntityNotFoundException: If user not found
        """
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("User", str(user.id))

        # Update model fields
        model.email = str(user.email)
        model.password_hash = user.password_hash.value
        model.name = user.name
        model.avatar_url = user.avatar_url
        model.preferences = json.dumps(user.preferences) if user.preferences else None
        model.language = str(user.language)
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        model.updated_at = user.updated_at
        model.deleted_at = user.deleted_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> None:
        """Hard delete a user.

        Args:
            user_id: User UUID

        Raises:
            EntityNotFoundException: If user not found
        """
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()

        if model is None:
            raise EntityNotFoundException("User", str(user_id))

        await self._session.delete(model)
        await self._session.flush()

    async def exists_by_email(self, email: Email) -> bool:
        """Check if user with email exists.

        Args:
            email: Email to check

        Returns:
            True if user exists, False otherwise
        """
        result = await self._session.execute(
            select(func.count()).select_from(UserModel).where(UserModel.email == str(email))
        )
        count: int = result.scalar_one()
        return count > 0

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[User]:
        """Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted users

        Returns:
            List of users
        """
        query = select(UserModel)

        if not include_deleted:
            query = query.where(UserModel.deleted_at.is_(None))

        query = query.offset(skip).limit(limit).order_by(UserModel.created_at.desc())

        result = await self._session.execute(query)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    async def count(self, include_deleted: bool = False) -> int:
        """Count total users.

        Args:
            include_deleted: Whether to include soft-deleted users

        Returns:
            Total count of users
        """
        query = select(func.count()).select_from(UserModel)

        if not include_deleted:
            query = query.where(UserModel.deleted_at.is_(None))

        result = await self._session.execute(query)
        count: int = result.scalar_one()
        return count

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[User]:
        """Search users by name or email.

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching users
        """
        search_pattern = f"%{query}%"

        stmt = (
            select(UserModel)
            .where(
                UserModel.deleted_at.is_(None),
                or_(
                    UserModel.name.ilike(search_pattern),
                    UserModel.email.ilike(search_pattern),
                ),
            )
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.name)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity.

        Args:
            model: UserModel instance

        Returns:
            User domain entity
        """
        # Parse preferences JSON
        preferences = None
        if model.preferences:
            try:
                preferences = json.loads(model.preferences)
            except (json.JSONDecodeError, TypeError):
                # Invalid JSON, use None
                preferences = None

        return User(
            id=model.id,
            email=Email(model.email),
            password_hash=HashedPassword(model.password_hash),
            name=model.name,
            avatar_url=model.avatar_url,
            preferences=preferences,
            language=Language.from_string(model.language),
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
