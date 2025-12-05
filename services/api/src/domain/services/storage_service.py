"""Storage service interface for file operations."""

from abc import ABC, abstractmethod


class StorageService(ABC):
    """Abstract storage service interface.

    This is a port for file storage operations.
    Implementation can be local filesystem, S3, or other storage backends.
    """

    @abstractmethod
    async def save(
        self,
        file_content: bytes,
        file_path: str,
        content_type: str,
    ) -> str:
        """Save file content to storage.

        Args:
            file_content: File content as bytes
            file_path: Path where to save the file (relative to storage root)
            content_type: MIME type of the file

        Returns:
            URL or path to access the saved file

        Raises:
            StorageException: If save operation fails
        """
        ...

    @abstractmethod
    async def save_multiple(
        self,
        files: list[tuple[bytes, str, str]],
    ) -> list[str]:
        """Save multiple files to storage.

        Args:
            files: List of tuples (file_content, file_path, content_type)

        Returns:
            List of URLs or paths to access the saved files

        Raises:
            StorageException: If save operation fails
        """
        ...

    @abstractmethod
    async def delete(self, file_path: str) -> None:
        """Delete file from storage.

        Args:
            file_path: Path to the file to delete (relative to storage root)

        Raises:
            StorageException: If delete operation fails
        """
        ...

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Check if file exists in storage.

        Args:
            file_path: Path to check (relative to storage root)

        Returns:
            True if file exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_url(self, file_path: str) -> str:
        """Get URL to access a file.

        Args:
            file_path: Path to the file (relative to storage root)

        Returns:
            URL to access the file (absolute URL or relative path)
        """
        ...

