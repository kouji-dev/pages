"""User preferences value objects and default schemas."""

from typing import Any, Literal

# Allowed theme values
Theme = Literal["light", "dark", "auto"]

# Allowed language codes
Language = str  # ISO 639-1 language codes (e.g., "en", "fr", "es")


def get_default_preferences() -> dict[str, Any]:
    """Get default user preferences structure.

    Returns:
        Dictionary with default preferences:
        - theme: UI theme preference (light/dark/auto)
        - language: Language preference (ISO 639-1 code)
        - notifications: Notification preferences
    """
    return {
        "theme": "auto",  # auto = follow system preference
        "language": "en",
        "notifications": {
            "email": {
                "enabled": True,
                "on_issue_assigned": True,
                "on_issue_mentioned": True,
                "on_comment_added": True,
                "on_comment_mentioned": True,
                "on_issue_status_changed": True,
                "on_project_invitation": True,
            },
            "push": {
                "enabled": True,
                "on_issue_assigned": True,
                "on_issue_mentioned": True,
                "on_comment_added": True,
                "on_comment_mentioned": False,
                "on_issue_status_changed": False,
                "on_project_invitation": True,
            },
            "in_app": {
                "enabled": True,
                "on_issue_assigned": True,
                "on_issue_mentioned": True,
                "on_comment_added": True,
                "on_comment_mentioned": True,
                "on_issue_status_changed": True,
                "on_project_invitation": True,
            },
        },
    }


def validate_preferences(preferences: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize preferences.

    Args:
        preferences: User preferences dictionary

    Returns:
        Validated and normalized preferences dictionary

    Raises:
        ValueError: If preferences structure is invalid
    """
    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a dictionary")

    # Start with defaults and merge user preferences
    validated = get_default_preferences()

    # Validate theme
    if "theme" in preferences:
        theme = preferences["theme"]
        if theme not in ("light", "dark", "auto"):
            raise ValueError(f"Invalid theme: {theme}. Must be 'light', 'dark', or 'auto'")
        validated["theme"] = theme

    # Validate language
    if "language" in preferences:
        language = preferences["language"]
        if not isinstance(language, str) or len(language) != 2:
            raise ValueError("Language must be a 2-character ISO 639-1 code")
        validated["language"] = language.lower()

    # Validate notifications
    if "notifications" in preferences:
        notifications = preferences["notifications"]
        if not isinstance(notifications, dict):
            raise ValueError("Notifications must be a dictionary")

        # Validate each notification type
        for notification_type in ["email", "push", "in_app"]:
            if notification_type in notifications:
                notification_config = notifications[notification_type]
                if not isinstance(notification_config, dict):
                    raise ValueError(
                        f"Notification config for '{notification_type}' must be a dictionary"
                    )

                # Merge notification config
                if notification_type not in validated["notifications"]:
                    validated["notifications"][notification_type] = {}

                # Validate boolean fields
                boolean_fields = [
                    "enabled",
                    "on_issue_assigned",
                    "on_issue_mentioned",
                    "on_comment_added",
                    "on_comment_mentioned",
                    "on_issue_status_changed",
                    "on_project_invitation",
                ]

                for field in boolean_fields:
                    if field in notification_config:
                        value = notification_config[field]
                        if not isinstance(value, bool):
                            raise ValueError(f"Notification field '{field}' must be a boolean")
                        validated["notifications"][notification_type][field] = value

    return validated
