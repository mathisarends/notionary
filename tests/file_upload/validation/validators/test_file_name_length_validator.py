import pytest

from notionary.exceptions.file_upload import FilenameTooLongError
from notionary.file_upload.config.constants import NOTION_MAX_FILENAME_BYTES
from notionary.file_upload.validation.validators import FileNameLengthValidator


@pytest.mark.asyncio
async def test_validate_passes_for_short_filename() -> None:
    validator = FileNameLengthValidator("test.pdf")

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_max_length_filename() -> None:
    filename = "a" * (NOTION_MAX_FILENAME_BYTES - 4) + ".pdf"
    validator = FileNameLengthValidator(filename)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_when_filename_exceeds_limit() -> None:
    filename = "a" * (NOTION_MAX_FILENAME_BYTES + 1)
    validator = FileNameLengthValidator(filename)

    with pytest.raises(FilenameTooLongError) as exc_info:
        await validator.validate()

    assert filename in str(exc_info.value)
    assert exc_info.value.filename == filename
    assert exc_info.value.filename_bytes > NOTION_MAX_FILENAME_BYTES
    assert exc_info.value.max_filename_bytes == NOTION_MAX_FILENAME_BYTES


@pytest.mark.asyncio
async def test_validate_handles_unicode_characters() -> None:
    filename = "日本語.txt"
    validator = FileNameLengthValidator(filename)

    if len(filename.encode("utf-8")) > NOTION_MAX_FILENAME_BYTES:
        with pytest.raises(FilenameTooLongError) as exc_info:
            await validator.validate()

        assert exc_info.value.filename_bytes == len(filename.encode("utf-8"))
    else:
        await validator.validate()


@pytest.mark.asyncio
async def test_validate_uses_constant_notion_limit() -> None:
    validator = FileNameLengthValidator("test.pdf")

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_with_very_long_filename() -> None:
    filename = "x" * 1000 + ".pdf"
    validator = FileNameLengthValidator(filename)

    with pytest.raises(FilenameTooLongError) as exc_info:
        await validator.validate()

    assert exc_info.value.filename_bytes > NOTION_MAX_FILENAME_BYTES
