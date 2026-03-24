import logging

from notionary.file_upload.validation.port import FileUploadValidator

from notionary.shared.decorators import timed

logger = logging.getLogger(__name__)


class FileUploadValidationService:
    def __init__(self) -> None:
        self._validators: list[FileUploadValidator] = []

    def register(self, validator: FileUploadValidator) -> None:
        self._validators.append(validator)

    @timed()
    async def validate(self) -> None:
        for validator in self._validators:
            logger.info("Validating with %s", validator.__class__.__name__)
            await validator.validate()
