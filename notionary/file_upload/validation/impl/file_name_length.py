from typing import override

from notionary.exceptions.file_upload import FilenameTooLongError
from notionary.file_upload.config.config import FileUploadConfig
from notionary.file_upload.validation.port import FileUploadValidator


class FileNameLengthValidator(FileUploadValidator):
    def __init__(
        self, filename: str, file_upload_config: FileUploadConfig | None = None
    ) -> None:
        self._filename = filename

        file_upload_config = file_upload_config or FileUploadConfig()
        self._max_filename_bytes = file_upload_config.MAX_FILENAME_BYTES

    @override
    async def validate(self) -> None:
        filename_bytes = len(self._filename.encode("utf-8"))
        if filename_bytes > self._max_filename_bytes:
            raise FilenameTooLongError(
                filename=self._filename,
                filename_bytes=filename_bytes,
                max_filename_bytes=self._max_filename_bytes,
            )
