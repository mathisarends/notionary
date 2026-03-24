from typing import override

from notionary.file_upload.config.constants import NOTION_MAX_FILENAME_BYTES
from notionary.file_upload.validation.port import FileUploadValidator

from notionary.exceptions.file_upload import FilenameTooLongError


class FileNameLengthValidator(FileUploadValidator):
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._max_filename_bytes = NOTION_MAX_FILENAME_BYTES

    @override
    async def validate(self) -> None:
        filename_bytes = len(self._filename.encode("utf-8"))
        if filename_bytes > self._max_filename_bytes:
            raise FilenameTooLongError(
                filename=self._filename,
                filename_bytes=filename_bytes,
                max_filename_bytes=self._max_filename_bytes,
            )
