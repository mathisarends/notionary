from notionary.file_upload.validation.port import FileUploadValidator
from notionary.utils.decorators import time_execution_async
from notionary.utils.mixins.logging import LoggingMixin


class FileUploadValidationService(LoggingMixin):
    def __init__(self) -> None:
        self._processors: list[FileUploadValidator] = []

    def register(self, processor: FileUploadValidator) -> None:
        self._processors.append(processor)

    @time_execution_async()
    async def process(self, uploaded_file: str) -> str:
        for processor in self._processors:
            self.logger.info(f"Validating uploaded file with {processor.__class__.__name__}")
            await processor.validate(uploaded_file)
