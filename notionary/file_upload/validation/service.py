from notionary.file_upload.validation.port import FileUploadValidator
from notionary.utils.decorators import time_execution_async
from notionary.utils.mixins.logging import LoggingMixin


class FileUploadValidationService(LoggingMixin):
    def __init__(self) -> None:
        self._validators: list[FileUploadValidator] = []

    def register(self, validator: FileUploadValidator) -> None:
        self._validators.append(validator)

    @time_execution_async()
    async def validate(self) -> None:
        for validator in self._validators:
            self.logger.info("Validating with %s", validator.__class__.__name__)
            await validator.validate()
