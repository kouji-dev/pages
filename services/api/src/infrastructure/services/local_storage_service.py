"""Local filesystem storage service implementation."""

from pathlib import Path

import structlog

from src.domain.exceptions import StorageException
from src.domain.services import StorageService
from src.infrastructure.config import get_settings

logger = structlog.get_logger()


class LocalStorageService(StorageService):
    """Local filesystem implementation of StorageService."""

    def __init__(self, storage_path: str | None = None, base_url: str | None = None) -> None:
        """Initialize local storage service.

        Args:
            storage_path: Root path for file storage (defaults to settings.storage_path)
            base_url: Base URL for file access (defaults to settings.storage_base_url)
        """
        settings = get_settings()
        self._storage_path = Path(storage_path or settings.storage_path)
        self._base_url = base_url or settings.storage_base_url

        # Create storage directory if it doesn't exist
        self._storage_path.mkdir(parents=True, exist_ok=True)

        logger.info("LocalStorageService initialized", storage_path=str(self._storage_path))

    async def save(
        self,
        file_content: bytes,
        file_path: str,
        content_type: str,
    ) -> str:
        """Save file content to local filesystem.

        Args:
            file_content: File content as bytes
            file_path: Relative path where to save the file
            content_type: MIME type of the file

        Returns:
            URL to access the saved file

        Raises:
            StorageException: If save operation fails
        """
        try:
            # Create full path
            full_path = self._storage_path / file_path

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, "wb") as f:
                f.write(file_content)

            logger.info("File saved", file_path=file_path, size=len(file_content))

            # Return URL
            return self._get_url(file_path)

        except OSError as e:
            logger.error("Failed to save file", file_path=file_path, error=str(e))
            raise StorageException(f"Failed to save file: {str(e)}") from e

    async def save_multiple(
        self,
        files: list[tuple[bytes, str, str]],
    ) -> list[str]:
        """Save multiple files to local filesystem.

        Args:
            files: List of tuples (file_content, file_path, content_type)

        Returns:
            List of URLs to access the saved files

        Raises:
            StorageException: If save operation fails
        """
        urls = []
        for file_content, file_path, content_type in files:
            url = await self.save(file_content, file_path, content_type)
            urls.append(url)
        return urls

    async def delete(self, file_path: str) -> None:
        """Delete file from local filesystem.

        Args:
            file_path: Relative path to the file to delete

        Raises:
            StorageException: If delete operation fails
        """
        try:
            full_path = self._storage_path / file_path

            if not full_path.exists():
                logger.warning("File not found for deletion", file_path=file_path)
                return

            full_path.unlink()
            logger.info("File deleted", file_path=file_path)

        except OSError as e:
            logger.error("Failed to delete file", file_path=file_path, error=str(e))
            raise StorageException(f"Failed to delete file: {str(e)}") from e

    async def exists(self, file_path: str) -> bool:
        """Check if file exists in local filesystem.

        Args:
            file_path: Relative path to check

        Returns:
            True if file exists, False otherwise
        """
        full_path = self._storage_path / file_path
        return full_path.exists() and full_path.is_file()

    async def get_url(self, file_path: str) -> str:
        """Get URL to access a file.

        Args:
            file_path: Relative path to the file

        Returns:
            URL to access the file
        """
        return self._get_url(file_path)

    async def get_file(self, file_path: str) -> bytes:
        """Retrieve file content from local filesystem.

        Args:
            file_path: Relative path to the file

        Returns:
            File content as bytes

        Raises:
            StorageException: If file does not exist or read fails
        """
        try:
            full_path = self._storage_path / file_path

            if not full_path.exists():
                raise StorageException(f"File not found: {file_path}")

            with open(full_path, "rb") as f:
                return f.read()

        except OSError as e:
            logger.error("Failed to read file", file_path=file_path, error=str(e))
            raise StorageException(f"Failed to read file: {str(e)}") from e

    def _get_url(self, file_path: str) -> str:
        """Generate URL for a file path.

        Args:
            file_path: Relative file path

        Returns:
            Full URL to access the file
        """
        # Normalize path (remove leading slashes, use forward slashes)
        normalized_path = file_path.lstrip("/").replace("\\", "/")
        base_url = self._base_url.rstrip("/")
        return f"{base_url}/{normalized_path}"
