"""Image processing service for avatar uploads."""

import io
from typing import NamedTuple

import structlog
from PIL import Image

from src.domain.exceptions import ValidationException

logger = structlog.get_logger()


class ImageSize(NamedTuple):
    """Image size configuration."""

    width: int
    height: int
    name: str


class ImageProcessingService:
    """Service for processing and resizing images."""

    # Allowed MIME types for images
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    # Standard avatar sizes
    AVATAR_SIZES = [
        ImageSize(64, 64, "64x64"),
        ImageSize(128, 128, "128x128"),
        ImageSize(256, 256, "256x256"),
    ]

    @classmethod
    def is_allowed_mime_type(cls, mime_type: str) -> bool:
        """Check if MIME type is allowed for images.

        Args:
            mime_type: MIME type to check

        Returns:
            True if allowed, False otherwise
        """
        return mime_type in cls.ALLOWED_MIME_TYPES

    @classmethod
    def validate_image(
        cls,
        file_content: bytes,
        max_size_mb: int = 5,
    ) -> None:
        """Validate image file.

        Args:
            file_content: Image file content as bytes
            max_size_mb: Maximum file size in MB

        Raises:
            ValidationException: If validation fails
        """
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        if len(file_content) > max_size_bytes:
            raise ValidationException(
                f"File size exceeds maximum allowed size of {max_size_mb}MB",
                field="file",
            )

        # Try to open and validate image
        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()  # Verify that it's a valid image
        except Exception as e:
            logger.warning("Invalid image file", error=str(e))
            raise ValidationException(
                "Invalid image file format",
                field="file",
            ) from e

    @classmethod
    def process_avatar(
        cls,
        file_content: bytes,
        output_format: str = "PNG",
    ) -> dict[str, bytes]:
        """Process avatar image and create multiple sizes.

        Args:
            file_content: Original image file content
            output_format: Output format (PNG, JPEG, WEBP)

        Returns:
            Dictionary mapping size names to processed image bytes

        Raises:
            ValidationException: If processing fails
        """
        try:
            # Open original image
            original_image = Image.open(io.BytesIO(file_content))

            # Convert RGBA to RGB if necessary (for JPEG)
            if output_format == "JPEG" and original_image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", original_image.size, (255, 255, 255))
                if original_image.mode == "P":
                    original_image = original_image.convert("RGBA")
                background.paste(
                    original_image,
                    mask=original_image.split()[-1] if original_image.mode == "RGBA" else None,
                )
                original_image = background
            elif original_image.mode not in ("RGB", "RGBA", "L"):
                original_image = original_image.convert("RGB")

            processed_images = {}

            # Generate each size
            for size_config in cls.AVATAR_SIZES:
                # Resize image maintaining aspect ratio
                resized_image = cls._resize_image(
                    original_image,
                    size_config.width,
                    size_config.height,
                )

                # Save to bytes
                output_buffer = io.BytesIO()

                # Optimize based on format
                if output_format == "JPEG":
                    resized_image.save(output_buffer, format="JPEG", quality=85, optimize=True)
                elif output_format == "WEBP":
                    resized_image.save(output_buffer, format="WEBP", quality=85, method=6)
                else:  # PNG
                    resized_image.save(output_buffer, format="PNG", optimize=True)

                processed_images[size_config.name] = output_buffer.getvalue()

            logger.info(
                "Avatar processed",
                sizes=list(processed_images.keys()),
                format=output_format,
            )

            return processed_images

        except Exception as e:
            logger.error("Failed to process avatar", error=str(e))
            raise ValidationException(
                f"Failed to process image: {str(e)}",
                field="file",
            ) from e

    @classmethod
    def _resize_image(
        cls,
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        """Resize image maintaining aspect ratio with cropping to fit exactly.

        Args:
            image: Original PIL Image
            target_width: Target width in pixels
            target_height: Target height in pixels

        Returns:
            Resized PIL Image
        """
        # Calculate aspect ratios
        original_aspect = image.width / image.height
        target_aspect = target_width / target_height

        # Resize maintaining aspect ratio, then crop to exact size
        if original_aspect > target_aspect:
            # Image is wider than target - fit to height, crop width
            new_height = target_height
            new_width = int(image.width * (target_height / image.height))
        else:
            # Image is taller than target - fit to width, crop height
            new_width = target_width
            new_height = int(image.height * (target_width / image.width))

        # Resize
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop to exact size (center crop)
        if new_width > target_width:
            left = (new_width - target_width) // 2
            resized = resized.crop((left, 0, left + target_width, target_height))
        elif new_height > target_height:
            top = (new_height - target_height) // 2
            resized = resized.crop((0, top, target_width, top + target_height))

        return resized

    @classmethod
    def get_output_format(cls, mime_type: str) -> str:
        """Get output format string for PIL from MIME type.

        Args:
            mime_type: MIME type of the input image

        Returns:
            Format string for PIL (PNG, JPEG, WEBP)
        """
        mime_to_format = {
            "image/jpeg": "JPEG",
            "image/png": "PNG",
            "image/webp": "WEBP",
        }
        return mime_to_format.get(mime_type, "PNG")
