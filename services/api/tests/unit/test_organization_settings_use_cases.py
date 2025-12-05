"""Unit tests for organization settings use cases."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.organization_settings import UpdateOrganizationSettingsRequest
from src.application.use_cases.organization_settings import (
    GetOrganizationSettingsUseCase,
    UpdateOrganizationSettingsUseCase,
)
from src.domain.entities import Organization
from src.domain.exceptions import EntityNotFoundException, ValidationException


class TestGetOrganizationSettingsUseCase:
    """Tests for GetOrganizationSettingsUseCase."""

    @pytest.fixture
    def test_organization(self):
        """Create a test organization without settings."""
        return Organization.create(
            name="Test Organization",
            slug="test-org",
            description="Test description",
        )

    @pytest.fixture
    def test_organization_with_settings(self):
        """Create a test organization with custom settings."""
        org = Organization.create(
            name="Test Organization",
            slug="test-org",
            description="Test description",
        )
        org.settings = {
            "feature_flags": {
                "advanced_analytics": True,
                "custom_workflows": True,
            },
            "notifications": {
                "email_digest": {
                    "enabled": False,
                    "frequency": "weekly",
                },
            },
        }
        return org

    @pytest.mark.asyncio
    async def test_get_settings_returns_defaults(self, test_organization) -> None:
        """Test getting settings returns defaults when organization has none."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization

        use_case = GetOrganizationSettingsUseCase(organization_repository)

        # Execute
        result = await use_case.execute(str(test_organization.id))

        # Assert
        assert result.settings is not None
        assert "feature_flags" in result.settings
        assert "notifications" in result.settings
        assert "branding" in result.settings
        assert result.settings["feature_flags"]["advanced_analytics"] is False  # Default
        organization_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_settings_returns_organization_settings(
        self, test_organization_with_settings
    ) -> None:
        """Test getting settings returns organization's custom settings."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization_with_settings

        use_case = GetOrganizationSettingsUseCase(organization_repository)

        # Execute
        result = await use_case.execute(str(test_organization_with_settings.id))

        # Assert
        assert result.settings is not None
        assert result.settings["feature_flags"]["advanced_analytics"] is True
        assert result.settings["feature_flags"]["custom_workflows"] is True
        assert result.settings["notifications"]["email_digest"]["enabled"] is False
        assert result.settings["notifications"]["email_digest"]["frequency"] == "weekly"
        organization_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_settings_organization_not_found(self) -> None:
        """Test getting settings for non-existent organization."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = None

        use_case = GetOrganizationSettingsUseCase(organization_repository)

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()))


class TestUpdateOrganizationSettingsUseCase:
    """Tests for UpdateOrganizationSettingsUseCase."""

    @pytest.fixture
    def test_organization(self):
        """Create a test organization."""
        return Organization.create(
            name="Test Organization",
            slug="test-org",
            description="Test description",
        )

    @pytest.mark.asyncio
    async def test_update_settings_success(self, test_organization) -> None:
        """Test successfully updating settings."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization
        organization_repository.update.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "feature_flags": {
                    "advanced_analytics": True,
                },
            }
        )

        # Execute
        result = await use_case.execute(str(test_organization.id), request)

        # Assert
        assert result.settings is not None
        assert result.settings["feature_flags"]["advanced_analytics"] is True
        organization_repository.get_by_id.assert_called_once()
        organization_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_merges_with_existing(self, test_organization) -> None:
        """Test that settings are merged with existing settings."""
        # Setup - organization with existing settings
        test_organization.settings = {
            "feature_flags": {
                "advanced_analytics": False,
                "custom_workflows": True,
            },
            "notifications": {
                "email_digest": {
                    "enabled": True,
                    "frequency": "daily",
                },
            },
        }

        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization
        organization_repository.update.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        # Only update advanced_analytics, keep custom_workflows
        request = UpdateOrganizationSettingsRequest(
            settings={
                "feature_flags": {
                    "advanced_analytics": True,
                },
            }
        )

        # Execute
        result = await use_case.execute(str(test_organization.id), request)

        # Assert - merged settings should have both flags
        assert result.settings["feature_flags"]["advanced_analytics"] is True  # Updated
        assert result.settings["feature_flags"]["custom_workflows"] is True  # Kept
        assert result.settings["notifications"]["email_digest"]["enabled"] is True  # Kept

    @pytest.mark.asyncio
    async def test_update_settings_invalid_feature_flag(self, test_organization) -> None:
        """Test updating settings with invalid feature flag value fails."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "feature_flags": {
                    "advanced_analytics": "invalid",  # Should be boolean
                },
            }
        )

        # Execute & Assert
        with pytest.raises(ValidationException):
            await use_case.execute(str(test_organization.id), request)

    @pytest.mark.asyncio
    async def test_update_settings_invalid_email_digest_frequency(self, test_organization) -> None:
        """Test updating settings with invalid email digest frequency fails."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "notifications": {
                    "email_digest": {
                        "frequency": "invalid",  # Should be daily, weekly, or never
                    },
                },
            }
        )

        # Execute & Assert
        with pytest.raises(ValidationException):
            await use_case.execute(str(test_organization.id), request)

    @pytest.mark.asyncio
    async def test_update_settings_organization_not_found(self) -> None:
        """Test updating settings for non-existent organization."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = None

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "feature_flags": {
                    "advanced_analytics": True,
                },
            }
        )

        # Execute & Assert
        with pytest.raises(EntityNotFoundException):
            await use_case.execute(str(uuid4()), request)

    @pytest.mark.asyncio
    async def test_update_settings_notifications(self, test_organization) -> None:
        """Test updating notification settings."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization
        organization_repository.update.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "notifications": {
                    "email_digest": {
                        "enabled": False,
                        "frequency": "weekly",
                    },
                    "project_updates": {
                        "enabled": True,
                        "on_new_issue": False,
                    },
                },
            }
        )

        # Execute
        result = await use_case.execute(str(test_organization.id), request)

        # Assert
        assert result.settings["notifications"]["email_digest"]["enabled"] is False
        assert result.settings["notifications"]["email_digest"]["frequency"] == "weekly"
        assert result.settings["notifications"]["project_updates"]["enabled"] is True
        assert result.settings["notifications"]["project_updates"]["on_new_issue"] is False
        organization_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_settings_branding(self, test_organization) -> None:
        """Test updating branding settings."""
        # Setup
        organization_repository = AsyncMock()
        organization_repository.get_by_id.return_value = test_organization
        organization_repository.update.return_value = test_organization

        use_case = UpdateOrganizationSettingsUseCase(organization_repository)
        request = UpdateOrganizationSettingsRequest(
            settings={
                "branding": {
                    "logo_url": "https://example.com/logo.png",
                    "primary_color": "#FF5733",
                    "secondary_color": "#33FF57",
                },
            }
        )

        # Execute
        result = await use_case.execute(str(test_organization.id), request)

        # Assert
        assert result.settings["branding"]["logo_url"] == "https://example.com/logo.png"
        assert result.settings["branding"]["primary_color"] == "#FF5733"
        assert result.settings["branding"]["secondary_color"] == "#33FF57"
        organization_repository.update.assert_called_once()
