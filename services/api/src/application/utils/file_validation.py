"""File validation utilities."""

import hashlib
from pathlib import Path
from uuid import UUID

# Allowed MIME types for MVP
ALLOWED_MIME_TYPES = {
    # Images
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    # Documents
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
    # Text
    "text/plain",
    "text/csv",
    "text/markdown",
    # Archives
    "application/zip",
    "application/x-zip-compressed",
    "application/x-rar-compressed",
    "application/x-7z-compressed",
    # Code
    "text/x-python",
    "application/json",
    "text/xml",
    "application/xml",
}

# Maximum file size: 10MB (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file_type(mime_type: str) -> bool:
    """Validate if MIME type is allowed.

    Args:
        mime_type: MIME type to validate

    Returns:
        True if allowed, False otherwise
    """
    return mime_type in ALLOWED_MIME_TYPES


def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits.

    Args:
        file_size: File size in bytes

    Returns:
        True if within limits, False otherwise
    """
    return 0 < file_size <= MAX_FILE_SIZE


def generate_unique_filename(original_name: str, attachment_id: UUID) -> str:
    """Generate a unique filename for storage.

    Args:
        original_name: Original filename from user
        attachment_id: UUID of the attachment

    Returns:
        Unique filename
    """
    # Get file extension
    original_path = Path(original_name)
    extension = original_path.suffix

    # Generate unique filename using attachment ID and hash of original name
    # Note: MD5 is used for non-cryptographic purposes (filename generation only)
    name_hash = hashlib.md5(original_name.encode(), usedforsecurity=False).hexdigest()[
        :8
    ]  # noqa: S324
    return f"{attachment_id}_{name_hash}{extension}"
