from pathlib import Path
from typing import override

from notionary.exceptions.file_upload import FileNotFoundError
from notionary.file_upload.validation.port import FileUploadValidator


class FileExistsValidator(FileUploadValidator):
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    @override
    async def validate(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(str(self.file_path))
