from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from notionary.exceptions.file_upload import FileSizeException
from notionary.file_upload.validation.validators import FileUploadLimitValidator
from notionary.user import BotUser


@pytest.fixture
def mock_bot_user() -> Mock:
    bot_user = Mock(spec=BotUser)
    bot_user.workspace_file_upload_limit_in_bytes = 20 * 1024 * 1024
    return bot_user


@pytest.fixture
def mock_bot_user_small_limit() -> Mock:
    bot_user = Mock(spec=BotUser)
    bot_user.workspace_file_upload_limit_in_bytes = 1 * 1024 * 1024
    return bot_user


@pytest.mark.asyncio
async def test_validate_passes_when_file_size_within_limit(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator(
        "small_file.pdf", file_size_bytes=5 * 1024 * 1024
    )

    await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_passes_when_file_size_equals_limit(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator(
        "exact_size.pdf", file_size_bytes=20 * 1024 * 1024
    )

    await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_fails_when_file_size_exceeds_limit(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator(
        "large_file.pdf", file_size_bytes=25 * 1024 * 1024
    )

    with pytest.raises(FileSizeException) as exc_info:
        await validator.validate(integration=mock_bot_user)

    assert exc_info.value.filename == "large_file.pdf"
    assert exc_info.value.file_size_bytes == 25 * 1024 * 1024
    assert exc_info.value.max_size_bytes == 20 * 1024 * 1024
    assert "25.00 MB" in str(exc_info.value)
    assert "20.00 MB" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_fails_when_file_exceeds_small_limit(
    mock_bot_user_small_limit: Mock,
) -> None:
    validator = FileUploadLimitValidator("file.pdf", file_size_bytes=2 * 1024 * 1024)

    with pytest.raises(FileSizeException) as exc_info:
        await validator.validate(integration=mock_bot_user_small_limit)

    assert exc_info.value.max_size_bytes == 1 * 1024 * 1024


@pytest.mark.asyncio
async def test_validate_extracts_filename_from_path(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator(
        Path("/some/path/document.pdf"), file_size_bytes=1024
    )

    assert validator.filename == "document.pdf"
    await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_handles_string_filename(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator("document.pdf", file_size_bytes=1024)

    assert validator.filename == "document.pdf"
    await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_handles_zero_byte_file(mock_bot_user: Mock) -> None:
    validator = FileUploadLimitValidator("empty.txt", file_size_bytes=0)

    await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_fails_with_one_byte_over_limit(mock_bot_user: Mock) -> None:
    limit = mock_bot_user.workspace_file_upload_limit_in_bytes
    validator = FileUploadLimitValidator("file.pdf", file_size_bytes=limit + 1)

    with pytest.raises(FileSizeException):
        await validator.validate(integration=mock_bot_user)


@pytest.mark.asyncio
async def test_validate_fetches_bot_user_when_not_provided() -> None:
    from unittest.mock import patch

    validator = FileUploadLimitValidator("file.pdf", file_size_bytes=1024)

    mock_bot = Mock(spec=BotUser)
    mock_bot.workspace_file_upload_limit_in_bytes = 10 * 1024 * 1024

    with patch(
        "notionary.user.bot.BotUser.from_current_integration",
        new_callable=AsyncMock,
        return_value=mock_bot,
    ):
        await validator.validate()
