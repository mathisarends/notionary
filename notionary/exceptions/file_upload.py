from notionary.exceptions.base import NotionaryException


class UnsupportedFileTypeException(NotionaryException):
    def __init__(self, extension: str, filename: str, supported_extensions_by_category: dict[str, list[str]]):
        supported_exts = []
        for category, extensions in supported_extensions_by_category.items():
            supported_exts.append(f"{category}: {', '.join(extensions[:5])}...")

        supported_info = "\n  ".join(supported_exts)
        super().__init__(
            f"File '{filename}' has unsupported extension '{extension}'.\n"
            f"Supported file types by category:\n  {supported_info}"
        )
        self.extension = extension
        self.filename = filename


class NoFileExtensionException(NotionaryException):
    def __init__(self, filename: str):
        super().__init__(
            f"File '{filename}' has no extension. Files must have a valid extension to determine their type."
        )
        self.filename = filename


class FileSizeException(NotionaryException):
    def __init__(self, filename: str, file_size_bytes: int, max_size_bytes: int):
        file_size_mb = file_size_bytes / (1024 * 1024)
        max_size_mb = max_size_bytes / (1024 * 1024)
        super().__init__(
            f"File '{filename}' is too large ({file_size_mb:.2f} MB). Maximum allowed size is {max_size_mb:.2f} MB."
        )
        self.filename = filename
        self.file_size_bytes = file_size_bytes
        self.max_size_bytes = max_size_bytes


class FileNotFoundError(NotionaryException):
    def __init__(self, file_path: str):
        super().__init__(f"File does not exist: {file_path}")
        self.file_path = file_path


class FilenameTooLongError(NotionaryException):
    def __init__(self, filename: str, filename_bytes: int, max_filename_bytes: int):
        super().__init__(f"Filename too long: {filename_bytes} bytes (max {max_filename_bytes}). Filename: {filename}")
        self.filename = filename
        self.filename_bytes = filename_bytes
        self.max_filename_bytes = max_filename_bytes


class UploadFailedError(NotionaryException):
    def __init__(self, file_upload_id: str, reason: str | None = None):
        message = f"Upload failed for file_upload_id: {file_upload_id}"
        if reason:
            message += f". Reason: {reason}"
        super().__init__(message)
        self.file_upload_id = file_upload_id
        self.reason = reason


class UploadTimeoutError(NotionaryException):
    def __init__(self, file_upload_id: str, timeout_seconds: int):
        super().__init__(f"Upload timeout after {timeout_seconds}s for file_upload_id: {file_upload_id}")
        self.file_upload_id = file_upload_id
        self.timeout_seconds = timeout_seconds
