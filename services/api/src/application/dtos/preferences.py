"""User preferences DTOs."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class NotificationPreferences(BaseModel):
    """Notification preferences for a specific channel."""

    enabled: bool = Field(default=True, description="Whether this notification channel is enabled")
    on_issue_assigned: bool = Field(default=True, description="Notify on issue assignment")
    on_issue_mentioned: bool = Field(default=True, description="Notify when mentioned in issue")
    on_comment_added: bool = Field(default=True, description="Notify on comment added")
    on_comment_mentioned: bool = Field(default=True, description="Notify when mentioned in comment")
    on_issue_status_changed: bool = Field(
        default=True, description="Notify on issue status change"
    )
    on_project_invitation: bool = Field(default=True, description="Notify on project invitation")


class AllNotificationPreferences(BaseModel):
    """All notification preferences."""

    email: NotificationPreferences = Field(
        default_factory=NotificationPreferences, description="Email notification preferences"
    )
    push: NotificationPreferences = Field(
        default_factory=NotificationPreferences, description="Push notification preferences"
    )
    in_app: NotificationPreferences = Field(
        default_factory=NotificationPreferences, description="In-app notification preferences"
    )


class UserPreferencesResponse(BaseModel):
    """Response DTO for user preferences."""

    theme: str = Field(description="UI theme preference (light/dark/auto)")
    language: str = Field(description="Language preference (ISO 639-1 code)")
    notifications: AllNotificationPreferences = Field(
        default_factory=AllNotificationPreferences, description="Notification preferences"
    )


class UserPreferencesUpdateRequest(BaseModel):
    """Request DTO for updating user preferences.

    All fields are optional - only provided fields will be updated.
    """

    theme: str | None = Field(
        None, description="UI theme preference (light/dark/auto)", pattern="^(light|dark|auto)$"
    )
    language: str | None = Field(
        None, description="Language preference (ISO 639-1 code)", min_length=2, max_length=2
    )
    notifications: dict[str, Any] | None = Field(None, description="Notification preferences")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        """Validate language code."""
        if v is not None:
            return v.lower()
        return v

