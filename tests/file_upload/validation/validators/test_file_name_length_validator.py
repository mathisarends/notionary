import pytest

from notionary.exceptions.file_upload import FilenameTooLongError
from notionary.file_upload.config import FileUploadConfig
from notionary.file_upload.validation.validators import FileNameLengthValidator


@pytest.fixture
def default_config() -> FileUploadConfig:
    return FileUploadConfig()


@pytest.fixture
def custom_config() -> FileUploadConfig:
    return FileUploadConfig(MAX_FILENAME_BYTES=50)


@pytest.mark.asyncio
async def test_validate_passes_for_short_filename(default_config: FileUploadConfig) -> None:
    validator = FileNameLengthValidator("test.pdf", default_config)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_max_length_filename(custom_config: FileUploadConfig) -> None:
    filename = "a" * 46 + ".pdf"
    validator = FileNameLengthValidator(filename, custom_config)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_when_filename_exceeds_limit(custom_config: FileUploadConfig) -> None:
    filename = "a" * 50 + ".pdf"
    validator = FileNameLengthValidator(filename, custom_config)

    with pytest.raises(FilenameTooLongError) as exc_info:
        await validator.validate()

    assert filename in str(exc_info.value)
    assert exc_info.value.filename == filename
    assert exc_info.value.filename_bytes > custom_config.MAX_FILENAME_BYTES
    assert exc_info.value.max_filename_bytes == custom_config.MAX_FILENAME_BYTES


@pytest.mark.asyncio
async def test_validate_handles_unicode_characters() -> None:
    config = FileUploadConfig(MAX_FILENAME_BYTES=10)
    filename = "日本語.txt"
    validator = FileNameLengthValidator(filename, config)

    with pytest.raises(FilenameTooLongError) as exc_info:
        await validator.validate()

    assert exc_info.value.filename_bytes == len(filename.encode("utf-8"))


@pytest.mark.asyncio
async def test_validate_uses_default_config_when_none_provided() -> None:
    validator = FileNameLengthValidator("test.pdf")

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_with_very_long_filename() -> None:
    filename = "x" * 1000 + ".pdf"
    validator = FileNameLengthValidator(filename)

    with pytest.raises(FilenameTooLongError) as exc_info:
        await validator.validate()

    assert exc_info.value.filename_bytes > 900
