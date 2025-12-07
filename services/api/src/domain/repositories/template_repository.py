"""Template repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities import Template


class TemplateRepository(ABC):
    """Abstract template repository interface.

    This is a port in hexagonal architecture / interface in clean architecture.
    The actual implementation will be in the infrastructure layer.
    """

    @abstractmethod
    async def create(self, template: Template) -> Template:
        """Create a new template.

        Args:
            template: Template entity to create

        Returns:
            Created template with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, template_id: UUID) -> Template | None:
        """Get template by ID.

        Args:
            template_id: Template UUID

        Returns:
            Template if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, template: Template) -> Template:
        """Update an existing template.

        Args:
            template: Template entity with updated data

        Returns:
            Updated template

        Raises:
            EntityNotFoundException: If template not found
        """
        ...

    @abstractmethod
    async def delete(self, template_id: UUID) -> None:
        """Hard delete a template.

        Args:
            template_id: Template UUID

        Raises:
            EntityNotFoundException: If template not found
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
        include_defaults: bool = True,
    ) -> list[Template]:
        """Get all templates in an organization with pagination.

        Args:
            organization_id: Organization UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted templates
            include_defaults: Whether to include default templates

        Returns:
            List of templates
        """
        ...

    @abstractmethod
    async def count(
        self,
        organization_id: UUID,
        include_deleted: bool = False,
        include_defaults: bool = True,
    ) -> int:
        """Count total templates in an organization.

        Args:
            organization_id: Organization UUID
            include_deleted: Whether to include soft-deleted templates
            include_defaults: Whether to include default templates

        Returns:
            Total count of templates
        """
        ...
