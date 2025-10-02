from pathlib import Path

from notionary.file_upload.file_upload_http_client import FileUploadHttpClient
from notionary.file_upload.models import UploadMode
from notionary.page.page_context import get_page_context
from notionary.utils.mixins import LoggingMixin


# TOOD: Hier überlegen wirklich nur was common ist hier in den mixin ansonstne dediziert handeln.
class FileUploadMixin(LoggingMixin):
    """
    Mixin to add file upload functionality to all media block elements.

    Supports uploading local files for:
    - file blocks
    - image blocks
    - pdf blocks
    - audio blocks
    - video blocks
    """

    @classmethod
    def _get_file_upload_client(cls) -> FileUploadHttpClient:
        """Get the file upload client from the current page context."""
        context = get_page_context()
        return context.file_upload_client

    @classmethod
    def _is_local_file_path(cls, path: str) -> bool:
        """Determine if the path is a local file rather than a URL."""
        if path.startswith(("http://", "https://", "ftp://")):
            return False

        return (
            "/" in path or "\\" in path or path.startswith("./") or path.startswith("../") or ":" in path[:3]
        )  # Windows drive letters like C:

    @classmethod
    def _should_upload_file(cls, path: str, expected_category: str = "file") -> bool:
        """
        Determine if a path should be uploaded vs used as external URL.

        Args:
            path: File path or URL
            expected_category: Expected file category

        Returns:
            True if file should be uploaded
        """
        if not cls._is_local_file_path(path):
            return False

        file_path = Path(path)
        return file_path.exists()

    @classmethod
    def _get_content_type(cls, file_path: Path) -> str:
        """Get MIME type based on file extension."""
        extension_map = {
            # Documents
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xls": "application/vnd.ms-excel",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".json": "application/json",
            ".xml": "application/xml",
            ".zip": "application/zip",
            ".rar": "application/vnd.rar",
            ".7z": "application/x-7z-compressed",
            # Images
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".heic": "image/heic",
            ".heif": "image/heif",
            # Audio
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/mp4",
            ".aac": "audio/aac",
            ".flac": "audio/flac",
            ".wma": "audio/x-ms-wma",
            ".opus": "audio/opus",
            # Video
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".wmv": "video/x-ms-wmv",
            ".flv": "video/x-flv",
            ".webm": "video/webm",
            ".mkv": "video/x-matroska",
            ".m4v": "video/mp4",
            ".3gp": "video/3gpp",
        }

        suffix = file_path.suffix.lower()
        return extension_map.get(suffix, "application/octet-stream")

    @classmethod
    def _get_file_category(cls, file_path: Path) -> str:
        """
        Determine the category of file based on extension.

        Returns:
            One of: 'image', 'audio', 'video', 'pdf', 'document', 'archive', 'other'
        """
        suffix = file_path.suffix.lower()

        # Define extension sets for each category
        extension_categories = {
            "image": {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".webp",
                ".bmp",
                ".tiff",
                ".tif",
                ".svg",
                ".ico",
                ".heic",
                ".heif",
            },
            "audio": {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".wma", ".opus"},
            "video": {
                ".mp4",
                ".avi",
                ".mov",
                ".wmv",
                ".flv",
                ".webm",
                ".mkv",
                ".m4v",
                ".3gp",
            },
            "pdf": {".pdf"},
            "document": {
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".txt",
                ".csv",
                ".json",
                ".xml",
            },
            "archive": {".zip", ".rar", ".7z"},
        }

        # Find matching category
        for category, extensions in extension_categories.items():
            if suffix in extensions:
                return category

        return "other"

    @classmethod
    def _is_supported_file_type(cls, file_path: Path, expected_category: str) -> bool:
        """
        Check if the file type matches the expected category.

        Args:
            file_path: Path to the file
            expected_category: Expected category ('image', 'audio', 'video', 'pdf', 'file')

        Returns:
            True if file type matches expected category
        """
        # 'file' category accepts any file type
        if expected_category == "file":
            return True

        actual_category = cls._get_file_category(file_path)
        return actual_category == expected_category

    @classmethod
    async def _upload_local_file(cls, file_path_str: str, expected_category: str = "file") -> str | None:
        """
        Upload a local file and return the file upload ID.

        Args:
            file_path_str: String path to the local file
            expected_category: Expected file category for validation

        Returns:
            File upload ID if successful, None otherwise
        """
        try:
            file_upload_client = cls._get_file_upload_client()
            file_path = Path(file_path_str)

            # Pre-upload validation
            if not cls._validate_file_for_upload(file_path, expected_category):
                return None

            # Get file metadata
            file_size = file_path.stat().st_size
            content_type = cls._get_content_type(file_path)

            cls.logger.info(f"Uploading {expected_category} file: {file_path.name} ({file_size} bytes, {content_type})")

            # Create and execute upload
            upload_id = await cls._execute_upload(file_upload_client, file_path, content_type, file_size)

            if upload_id:
                cls.logger.info(f"File upload completed: {upload_id} ({file_path.name})")

            return upload_id

        except Exception as e:
            cls.logger.error(f"Error uploading {expected_category} file {file_path_str}: {e}")
            cls.logger.debug("Upload error traceback:", exc_info=True)
            return None

    @classmethod
    def _validate_file_for_upload(cls, file_path: Path, expected_category: str) -> bool:
        """Validate file exists and type matches expected category."""
        # Check if file exists
        if not file_path.exists():
            cls.logger.error(f"File not found: {file_path}")
            return False

        # Validate file type if needed
        if not cls._is_supported_file_type(file_path, expected_category):
            actual_category = cls._get_file_category(file_path)
            cls.logger.warning(
                f"File type mismatch: expected {expected_category}, "
                f"got {actual_category} for {file_path} - proceeding anyway"
            )

        return True

    @classmethod
    async def _execute_upload(
        cls,
        file_upload_client: FileUploadHttpClient,
        file_path: Path,
        content_type: str,
        file_size: int,
    ) -> str | None:
        """Execute the actual file upload process."""
        # Step 1: Create file upload
        upload_response = await file_upload_client.create_file_upload(
            filename=file_path.name,
            content_type=content_type,
            content_length=file_size,
            mode=UploadMode.SINGLE_PART,
        )

        if not upload_response:
            cls.logger.error(f"Failed to create file upload for {file_path.name}")
            return None

        cls.logger.debug(f"Created file upload with ID: {upload_response.id}")

        # Step 2: Send file content
        success = await file_upload_client.send_file_from_path(file_upload_id=upload_response.id, file_path=file_path)

        if not success:
            cls.logger.error(f"Failed to send file content for {file_path.name}")
            return None

        cls.logger.debug(f"File content sent successfully for {file_path.name}")
        return upload_response.id

    @classmethod
    def _get_upload_error_message(cls, file_path_str: str, expected_category: str) -> str:
        """Get a user-friendly error message for upload failures."""
        file_path = Path(file_path_str)

        if not file_path.exists():
            return f"File not found: {file_path_str}"

        actual_category = cls._get_file_category(file_path)
        if expected_category not in (actual_category, "file"):
            return (
                f"Invalid file type for {expected_category} block: {file_path.suffix} (detected as {actual_category})"
            )

        return f"Failed to upload {expected_category} file: {file_path_str}"
