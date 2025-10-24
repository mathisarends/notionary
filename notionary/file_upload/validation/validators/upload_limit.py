from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, override

from notionary.exceptions.file_upload import FileSizeException
from notionary.file_upload.validation.port import FileUploadValidator

if TYPE_CHECKING:
    from notionary.user import BotUser


class FileUploadLimitValidator(FileUploadValidator):
    def __init__(self, filename: str | Path, file_size_bytes: int) -> None:
        self.filename = Path(filename).name if isinstance(filename, Path) else filename
        self.file_size_bytes = file_size_bytes

    @override
    async def validate(self, integration: BotUser | None = None) -> None:
        from notionary.user import BotUser

        integration = integration or await BotUser.from_current_integration()

        max_file_size_in_bytes = integration.workspace_file_upload_limit_in_bytes

        if self.file_size_bytes > max_file_size_in_bytes:
            raise FileSizeException(
                filename=self.filename,
                file_size_bytes=self.file_size_bytes,
                max_size_bytes=max_file_size_in_bytes,
            )
