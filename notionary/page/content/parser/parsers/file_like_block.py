from abc import abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, override

from notionary.blocks.schemas import (
    ExternalFileWithCaption,
    FileUploadFileWithCaption,
    FileWithCaption,
)
from notionary.exceptions.file_upload import UploadFailedError, UploadTimeoutError
from notionary.file_upload.service import NotionFileUpload
from notionary.page.content.parser.parsers.base import BlockParsingContext, LineParser
from notionary.page.content.syntax import SyntaxRegistry
from notionary.page.content.syntax.models import SyntaxDefinition
from notionary.shared.models.file import ExternalFileData, FileUploadedFileData
from notionary.utils.mixins.logging import LoggingMixin

_TBlock = TypeVar("_TBlock")


class FileLikeBlockParser(LineParser, LoggingMixin, Generic[_TBlock]):
    def __init__(self, syntax_registry: SyntaxRegistry, file_upload_service: NotionFileUpload | None = None) -> None:
        super().__init__(syntax_registry)
        self._syntax = self._get_syntax(syntax_registry)
        self._file_upload_service = file_upload_service or NotionFileUpload()

    @abstractmethod
    def _get_syntax(self, syntax_registry: SyntaxRegistry) -> SyntaxDefinition:
        pass

    @abstractmethod
    def _create_block(self, file_data: FileWithCaption) -> _TBlock:
        pass

    @override
    def _can_handle(self, context: BlockParsingContext) -> bool:
        if context.is_inside_parent_context():
            return False
        return self._syntax.regex_pattern.search(context.line) is not None

    @override
    async def _process(self, context: BlockParsingContext) -> None:
        path_or_url = self._extract_path_or_url(context.line)
        if not path_or_url:
            return

        try:
            if self._is_external_url(path_or_url):
                file_data = ExternalFileWithCaption(external=ExternalFileData(url=path_or_url))
            else:
                file_data = await self._upload_local_file(path_or_url)

            block = self._create_block(file_data)
            context.result_blocks.append(block)

        except FileNotFoundError:
            self.logger.warning("File not found: '%s' - skipping block", path_or_url)
        except PermissionError:
            self.logger.warning("No permission to read file: '%s' - skipping block", path_or_url)
        except IsADirectoryError:
            self.logger.warning("Path is a directory, not a file: '%s' - skipping block", path_or_url)
        except (UploadFailedError, UploadTimeoutError) as e:
            self.logger.warning("Upload failed for '%s': %s - skipping block", path_or_url, e)
        except OSError as e:
            self.logger.warning("IO error reading file '%s': %s - skipping block", path_or_url, e)
        except Exception as e:
            self.logger.warning("Unexpected error processing file '%s': %s - skipping block", path_or_url, e)

    def _extract_path_or_url(self, line: str) -> str | None:
        match = self._syntax.regex_pattern.search(line)
        return match.group(1).strip() if match else None

    def _is_external_url(self, path_or_url: str) -> bool:
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            return True

        if path_or_url.startswith("data:"):
            return True

        return path_or_url.startswith("/")

    async def _upload_local_file(self, file_path: str) -> FileUploadFileWithCaption:
        path = Path(file_path)
        self.logger.debug("Uploading local file: '%s'", path)
        upload_response = await self._file_upload_service.upload_file(path)

        return FileUploadFileWithCaption(
            file_upload=FileUploadedFileData(id=upload_response.id),
        )
