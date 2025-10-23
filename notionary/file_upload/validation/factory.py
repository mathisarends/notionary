from notionary.file_upload.validation.impl import FileExtensionValidator, FileUploadSizeValidator
from notionary.file_upload.validation.service import FileUploadValidationService


def create_file_upload_validator_service() -> FileUploadValidationService:
    validation_service = FileUploadValidationService()

    extension_validator = _create_extension_validator()
    size_validator = _create_size_validator()

    validation_service.register(extension_validator)
    validation_service.register(size_validator)

    return validation_service


def _create_extension_validator() -> FileExtensionValidator:
    return FileExtensionValidator()


def _create_size_validator() -> FileUploadSizeValidator:
    return FileUploadSizeValidator()
