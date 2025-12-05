"""Organization settings management use cases."""

from typing import Any

import structlog

from src.application.dtos.organization_settings import (
    OrganizationSettingsResponse,
    UpdateOrganizationSettingsRequest,
)
from src.domain.exceptions import EntityNotFoundException, ValidationException
from src.domain.repositories import OrganizationRepository
from src.domain.value_objects.organization_settings import (
    get_default_organization_settings,
    validate_organization_settings,
)

logger = structlog.get_logger()


class GetOrganizationSettingsUseCase:
    """Use case for retrieving organization settings."""

    def __init__(self, organization_repository: OrganizationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository for data access
        """
        self._organization_repository = organization_repository

    async def execute(self, organization_id: str) -> OrganizationSettingsResponse:
        """Execute get organization settings.

        Args:
            organization_id: Organization ID

        Returns:
            Organization settings response DTO

        Raises:
            EntityNotFoundException: If organization not found
        """
        from uuid import UUID

        logger.info("Getting organization settings", organization_id=organization_id)

        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning("Organization not found for settings", organization_id=organization_id)
            raise EntityNotFoundException("Organization", organization_id)

        # Use organization settings or defaults
        settings = organization.settings or get_default_organization_settings()

        return OrganizationSettingsResponse(settings=settings)


class UpdateOrganizationSettingsUseCase:
    """Use case for updating organization settings."""

    def __init__(self, organization_repository: OrganizationRepository) -> None:
        """Initialize use case with dependencies.

        Args:
            organization_repository: Organization repository for data access
        """
        self._organization_repository = organization_repository

    async def execute(
        self, organization_id: str, request: UpdateOrganizationSettingsRequest
    ) -> OrganizationSettingsResponse:
        """Execute update organization settings.

        Settings are merged with existing settings (not replaced).

        Args:
            organization_id: Organization ID
            request: Settings update request

        Returns:
            Updated organization settings response DTO

        Raises:
            EntityNotFoundException: If organization not found
            ValidationException: If settings validation fails
        """
        from uuid import UUID

        logger.info("Updating organization settings", organization_id=organization_id)

        org_uuid = UUID(organization_id)
        organization = await self._organization_repository.get_by_id(org_uuid)

        if organization is None:
            logger.warning(
                "Organization not found for settings update", organization_id=organization_id
            )
            raise EntityNotFoundException("Organization", organization_id)

        # Get current settings or defaults
        current_settings = organization.settings or get_default_organization_settings()

        # Deep merge request settings with current settings
        def deep_merge(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
            """Deep merge two dictionaries."""
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged_settings = deep_merge(current_settings, request.settings)

        # Validate merged settings
        try:
            validated_settings = validate_organization_settings(merged_settings)
        except ValueError as e:
            logger.warning(
                "Invalid organization settings", organization_id=organization_id, error=str(e)
            )
            raise ValidationException(str(e), field="settings") from e

        # Update organization settings
        organization.update_settings(validated_settings)

        # Save to database
        updated_org = await self._organization_repository.update(organization)

        logger.info("Organization settings updated", organization_id=organization_id)

        return OrganizationSettingsResponse(
            settings=updated_org.settings or get_default_organization_settings()
        )
