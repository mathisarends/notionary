from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar

from notionary.file_upload.file_system.models import FileInfo
from notionary.file_upload.validation.models import (
    AudioExtension,
    DocumentExtension,
    FileCategory,
    ImageExtension,
    VideoExtension,
)
from notionary.utils.mixins.logging import LoggingMixin


class FilePathResolver(LoggingMixin):
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = (
        {ext.value for ext in AudioExtension}
        | {ext.value for ext in DocumentExtension}
        | {ext.value for ext in ImageExtension}
        | {ext.value for ext in VideoExtension}
    )

    CATEGORY_EXTENSIONS: ClassVar[dict[FileCategory, frozenset[str]]] = {
        FileCategory.AUDIO: frozenset(ext.value for ext in AudioExtension),
        FileCategory.DOCUMENT: frozenset(ext.value for ext in DocumentExtension),
        FileCategory.IMAGE: frozenset(ext.value for ext in ImageExtension),
        FileCategory.VIDEO: frozenset(ext.value for ext in VideoExtension),
    }

    def __init__(self, base_path: Path | str | None = None):
        self._base_path = Path(base_path) if base_path else Path.cwd()
        self._base_path = self._base_path.resolve()
        self.logger.info(
            "Initialized FileSystemService with base path: %s", self._base_path
        )

    @property
    def base_path(self) -> Path:
        return self._base_path

    def resolve_path(self, filename: str | Path) -> Path:
        file_path = Path(filename)

        if file_path.is_absolute():
            self.logger.debug("Using absolute path: %s", file_path)
            return file_path

        resolved = (self._base_path / file_path).resolve()
        self.logger.debug("Resolved '%s' to: %s", filename, resolved)
        return resolved

    def list_files(
        self,
        pattern: str = "*",
        recursive: bool = False,
        only_supported: bool = True,
        categories: list[FileCategory] | None = None,
    ) -> list[FileInfo]:
        self.logger.info(
            "Scanning directory: %s (pattern='%s', recursive=%s, only_supported=%s, categories=%s)",
            self._base_path,
            pattern,
            recursive,
            only_supported,
            [c.value for c in categories] if categories else "all",
        )

        glob_method = self._base_path.rglob if recursive else self._base_path.glob
        files = []
        skipped_unsupported = 0

        for path in glob_method(pattern):
            if not path.is_file():
                continue

            if only_supported and not self._is_supported_file(path, categories):
                skipped_unsupported += 1
                self.logger.debug("Skipping unsupported file: %s", path.name)
                continue

            try:
                files.append(self._get_file_info(path.relative_to(self._base_path)))
            except (ValueError, OSError) as e:
                self.logger.warning("Could not process file %s: %s", path.name, e)
                continue

        if skipped_unsupported > 0:
            self.logger.info("Skipped %d unsupported files", skipped_unsupported)

        if not files and only_supported:
            self.logger.warning(
                "No supported files found in directory: %s", self._base_path
            )

        self.logger.info("Found %d file(s)", len(files))
        return files

    def _get_file_info(self, filename: str | Path) -> FileInfo:
        absolute_path = self.resolve_path(filename)

        if not absolute_path.exists():
            self.logger.error("File not found: %s", absolute_path)
            raise FileNotFoundError(f"File not found: {absolute_path}")

        if not absolute_path.is_file():
            self.logger.error("Path is not a file: %s", absolute_path)
            raise ValueError(f"Path is not a file: {absolute_path}")

        stat = absolute_path.stat()
        self.logger.debug(
            "Retrieved file info for '%s' (%.2f KB)",
            absolute_path.name,
            stat.st_size / 1024,
        )

        return FileInfo(
            name=absolute_path.name,
            path=Path(filename),
            size_bytes=stat.st_size,
            absolute_path=absolute_path,
        )

    def iter_files(
        self,
        pattern: str = "*",
        recursive: bool = False,
        only_supported: bool = True,
        categories: list[FileCategory] | None = None,
    ) -> Iterator[FileInfo]:
        self.logger.info(
            "Iterating files in: %s (pattern='%s', recursive=%s, only_supported=%s, categories=%s)",
            self._base_path,
            pattern,
            recursive,
            only_supported,
            [c.value for c in categories] if categories else "all",
        )

        glob_method = self._base_path.rglob if recursive else self._base_path.glob
        files_yielded = 0

        for path in glob_method(pattern):
            if not path.is_file():
                continue

            if only_supported and not self._is_supported_file(path, categories):
                self.logger.debug("Skipping unsupported file: %s", path.name)
                continue

            try:
                files_yielded += 1
                yield self._get_file_info(path.relative_to(self._base_path))
            except (ValueError, OSError) as e:
                self.logger.warning("Could not process file %s: %s", path.name, e)
                continue

        self.logger.info("Iterated through %d file(s)", files_yielded)

    def file_exists(self, filename: str | Path) -> bool:
        try:
            path = self.resolve_path(filename)
            exists = path.exists() and path.is_file()
            self.logger.debug("File exists check for '%s': %s", filename, exists)
            return exists
        except (ValueError, OSError):
            return False

    def _is_supported_file(
        self, path: Path, categories: list[FileCategory] | None = None
    ) -> bool:
        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            return False

        if categories is None:
            return True

        for category in categories:
            if extension in self.CATEGORY_EXTENSIONS.get(category, set()):
                return True

        return False
