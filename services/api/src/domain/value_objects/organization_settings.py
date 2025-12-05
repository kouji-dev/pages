"""Organization settings value objects and default schemas."""

from typing import Any


def get_default_organization_settings() -> dict[str, Any]:
    """Get default organization settings structure.

    Returns:
        Dictionary with default settings:
        - feature_flags: Feature flags for the organization
        - notifications: Organization-level notification preferences
        - branding: Custom branding settings (optional)
    """
    return {
        "feature_flags": {
            "advanced_analytics": False,
            "custom_workflows": False,
            "api_access": True,
            "integrations": True,
        },
        "notifications": {
            "email_digest": {
                "enabled": True,
                "frequency": "daily",  # daily, weekly, never
            },
            "project_updates": {
                "enabled": True,
                "on_new_issue": True,
                "on_issue_resolved": True,
                "on_new_member": True,
            },
            "space_updates": {
                "enabled": True,
                "on_new_page": True,
                "on_page_updated": True,
            },
        },
        "branding": {
            "logo_url": None,
            "primary_color": None,
            "secondary_color": None,
        },
    }


def validate_organization_settings(settings: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize organization settings.

    Args:
        settings: Organization settings dictionary

    Returns:
        Validated and normalized settings dictionary

    Raises:
        ValueError: If settings structure is invalid
    """
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a dictionary")

    # Start with defaults and merge organization settings
    validated = get_default_organization_settings()

    # Validate feature flags
    if "feature_flags" in settings:
        feature_flags = settings["feature_flags"]
        if not isinstance(feature_flags, dict):
            raise ValueError("Feature flags must be a dictionary")

        # Merge feature flags
        for flag_name, flag_value in feature_flags.items():
            if not isinstance(flag_value, bool):
                raise ValueError(f"Feature flag '{flag_name}' must be a boolean")
            validated["feature_flags"][flag_name] = flag_value

    # Validate notifications
    if "notifications" in settings:
        notifications = settings["notifications"]
        if not isinstance(notifications, dict):
            raise ValueError("Notifications must be a dictionary")

        # Validate email_digest
        if "email_digest" in notifications:
            email_digest = notifications["email_digest"]
            if not isinstance(email_digest, dict):
                raise ValueError("Email digest config must be a dictionary")

            if "enabled" in email_digest:
                if not isinstance(email_digest["enabled"], bool):
                    raise ValueError("Email digest 'enabled' must be a boolean")
                validated["notifications"]["email_digest"]["enabled"] = email_digest["enabled"]

            if "frequency" in email_digest:
                frequency = email_digest["frequency"]
                if frequency not in ("daily", "weekly", "never"):
                    raise ValueError("Email digest frequency must be 'daily', 'weekly', or 'never'")
                validated["notifications"]["email_digest"]["frequency"] = frequency

        # Validate project_updates
        if "project_updates" in notifications:
            project_updates = notifications["project_updates"]
            if not isinstance(project_updates, dict):
                raise ValueError("Project updates config must be a dictionary")

            boolean_fields = ["enabled", "on_new_issue", "on_issue_resolved", "on_new_member"]
            for field in boolean_fields:
                if field in project_updates:
                    value = project_updates[field]
                    if not isinstance(value, bool):
                        raise ValueError(f"Project updates field '{field}' must be a boolean")
                    validated["notifications"]["project_updates"][field] = value

        # Validate space_updates
        if "space_updates" in notifications:
            space_updates = notifications["space_updates"]
            if not isinstance(space_updates, dict):
                raise ValueError("Space updates config must be a dictionary")

            boolean_fields = ["enabled", "on_new_page", "on_page_updated"]
            for field in boolean_fields:
                if field in space_updates:
                    value = space_updates[field]
                    if not isinstance(value, bool):
                        raise ValueError(f"Space updates field '{field}' must be a boolean")
                    validated["notifications"]["space_updates"][field] = value

    # Validate branding
    if "branding" in settings:
        branding = settings["branding"]
        if not isinstance(branding, dict):
            raise ValueError("Branding must be a dictionary")

        if "logo_url" in branding:
            logo_url = branding["logo_url"]
            if logo_url is not None and not isinstance(logo_url, str):
                raise ValueError("Logo URL must be a string or None")
            validated["branding"]["logo_url"] = logo_url

        if "primary_color" in branding:
            primary_color = branding["primary_color"]
            if primary_color is not None and not isinstance(primary_color, str):
                raise ValueError("Primary color must be a string or None")
            validated["branding"]["primary_color"] = primary_color

        if "secondary_color" in branding:
            secondary_color = branding["secondary_color"]
            if secondary_color is not None and not isinstance(secondary_color, str):
                raise ValueError("Secondary color must be a string or None")
            validated["branding"]["secondary_color"] = secondary_color

    return validated
