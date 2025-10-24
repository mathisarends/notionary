from pathlib import Path

from notionary.file_upload.validation.service import FileUploadValidationService
from notionary.file_upload.validation.validators import (
    FileExistsValidator,
    FileExtensionValidator,
    FileNameLengthValidator,
    FileUploadLimitValidator,
)


def create_file_upload_validation_service(
    file_path: Path,
) -> FileUploadValidationService:
    file_path = Path(file_path)
    filename = file_path.name
    file_size_bytes = file_path.stat().st_size

    validation_service = FileUploadValidationService()

    file_exists_validator = _create_file_exists_validator(file_path)
    filename_length_validator = _create_filename_length_validator(filename)
    extension_validator = _create_extension_validator(filename)
    size_validator = _create_size_validator(filename, file_size_bytes)

    validation_service.register(file_exists_validator)
    validation_service.register(filename_length_validator)
    validation_service.register(extension_validator)
    validation_service.register(size_validator)

    return validation_service


def create_bytes_upload_validation_service(
    filename: str,
    file_size_bytes: int,
) -> FileUploadValidationService:
    validation_service = FileUploadValidationService()

    filename_length_validator = _create_filename_length_validator(filename)
    extension_validator = _create_extension_validator(filename)
    size_validator = _create_size_validator(filename, file_size_bytes)

    validation_service.register(filename_length_validator)
    validation_service.register(extension_validator)
    validation_service.register(size_validator)

    return validation_service


def _create_file_exists_validator(file_path: Path) -> FileExistsValidator:
    return FileExistsValidator(file_path=file_path)


def _create_filename_length_validator(filename: str) -> FileNameLengthValidator:
    return FileNameLengthValidator(filename=filename)


def _create_extension_validator(filename: str) -> FileExtensionValidator:
    return FileExtensionValidator(filename=filename)


def _create_size_validator(filename: str, file_size_bytes: int) -> FileUploadLimitValidator:
    return FileUploadLimitValidator(filename=filename, file_size_bytes=file_size_bytes)
