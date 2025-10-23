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
