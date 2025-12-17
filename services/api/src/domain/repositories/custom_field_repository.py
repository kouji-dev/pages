"""Custom field repository interface (port)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.custom_field import CustomField, CustomFieldValue


class CustomFieldRepository(ABC):
    """Abstract custom field repository interface."""

    @abstractmethod
    async def create(self, custom_field: CustomField) -> CustomField:
        """Create a new custom field.

        Args:
            custom_field: CustomField entity to create

        Returns:
            Created custom field with persisted data
        """
        ...

    @abstractmethod
    async def get_by_id(self, custom_field_id: UUID) -> CustomField | None:
        """Get custom field by ID.

        Args:
            custom_field_id: CustomField UUID

        Returns:
            CustomField if found, None otherwise
        """
        ...

    @abstractmethod
    async def get_by_project_id(self, project_id: UUID) -> list[CustomField]:
        """Get all custom fields for a project.

        Args:
            project_id: Project UUID

        Returns:
            List of custom fields for the project
        """
        ...

    @abstractmethod
    async def update(self, custom_field: CustomField) -> CustomField:
        """Update an existing custom field.

        Args:
            custom_field: CustomField entity with updated data

        Returns:
            Updated custom field

        Raises:
            EntityNotFoundException: If custom field not found
        """
        ...

    @abstractmethod
    async def delete(self, custom_field_id: UUID) -> None:
        """Delete a custom field.

        Args:
            custom_field_id: CustomField UUID

        Raises:
            EntityNotFoundException: If custom field not found
        """
        ...


class CustomFieldValueRepository(ABC):
    """Abstract custom field value repository interface."""

    @abstractmethod
    async def create(self, value: CustomFieldValue) -> CustomFieldValue:
        """Create a new custom field value.

        Args:
            value: CustomFieldValue entity to create

        Returns:
            Created value with persisted data
        """
        ...

    @abstractmethod
    async def get_by_issue_id(self, issue_id: UUID) -> list[CustomFieldValue]:
        """Get all custom field values for an issue.

        Args:
            issue_id: Issue UUID

        Returns:
            List of custom field values for the issue
        """
        ...

    @abstractmethod
    async def get_by_custom_field_id(self, custom_field_id: UUID) -> list[CustomFieldValue]:
        """Get all values for a custom field.

        Args:
            custom_field_id: CustomField UUID

        Returns:
            List of values for the custom field
        """
        ...

    @abstractmethod
    async def get_by_issue_and_field(
        self, issue_id: UUID, custom_field_id: UUID
    ) -> CustomFieldValue | None:
        """Get a specific custom field value for an issue.

        Args:
            issue_id: Issue UUID
            custom_field_id: CustomField UUID

        Returns:
            CustomFieldValue if found, None otherwise
        """
        ...

    @abstractmethod
    async def update(self, value: CustomFieldValue) -> CustomFieldValue:
        """Update an existing custom field value.

        Args:
            value: CustomFieldValue entity with updated data

        Returns:
            Updated value

        Raises:
            EntityNotFoundException: If value not found
        """
        ...

    @abstractmethod
    async def delete(self, value_id: UUID) -> None:
        """Delete a custom field value.

        Args:
            value_id: CustomFieldValue UUID

        Raises:
            EntityNotFoundException: If value not found
        """
        ...

    @abstractmethod
    async def delete_by_issue_id(self, issue_id: UUID) -> None:
        """Delete all custom field values for an issue.

        Args:
            issue_id: Issue UUID
        """
        ...
