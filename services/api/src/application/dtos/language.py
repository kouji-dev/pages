"""Language DTOs."""

from pydantic import BaseModel, Field


class LanguageInfo(BaseModel):
    """DTO for language information."""

    code: str = Field(..., description="ISO 639-1 language code (e.g., 'en', 'fr')")
    name: str = Field(..., description="Human-readable language name")

    class Config:
        """Pydantic config."""

        from_attributes = True


class SupportedLanguagesResponse(BaseModel):
    """Response DTO for list of supported languages."""

    languages: list[LanguageInfo] = Field(..., description="List of supported languages")


class UserLanguagePreference(BaseModel):
    """DTO for user language preference."""

    language: str = Field(
        ...,
        description="ISO 639-1 language code (e.g., 'en', 'fr', 'es', 'de')",
        min_length=2,
        max_length=5,
        examples=["en", "fr", "es-MX", "de"],
    )


class UserLanguageResponse(BaseModel):
    """Response DTO for user language preference."""

    language: str = Field(..., description="Current language preference")
    message: str = Field(default="Language preference retrieved successfully")

    class Config:
        """Pydantic config."""

        from_attributes = True


class UpdateUserLanguageResponse(BaseModel):
    """Response DTO for updating user language preference."""

    language: str = Field(..., description="Updated language preference")
    message: str = Field(default="Language preference updated successfully")

    class Config:
        """Pydantic config."""

        from_attributes = True
