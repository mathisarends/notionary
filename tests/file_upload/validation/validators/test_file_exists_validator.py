from pathlib import Path

import pytest

from notionary.exceptions.file_upload import FileNotFoundError
from notionary.file_upload.validation.validators import FileExistsValidator


@pytest.fixture
def existing_file(tmp_path: Path) -> Path:
    file_path = tmp_path / "existing_file.txt"
    file_path.write_text("content")
    return file_path


@pytest.fixture
def non_existing_file(tmp_path: Path) -> Path:
    return tmp_path / "non_existing_file.txt"


@pytest.mark.asyncio
async def test_validate_passes_for_existing_file(existing_file: Path) -> None:
    validator = FileExistsValidator(existing_file)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_for_non_existing_file(non_existing_file: Path) -> None:
    validator = FileExistsValidator(non_existing_file)

    with pytest.raises(FileNotFoundError) as exc_info:
        await validator.validate()

    assert str(non_existing_file) in str(exc_info.value)
    assert exc_info.value.file_path == str(non_existing_file)


@pytest.mark.asyncio
async def test_validate_fails_for_deleted_file(existing_file: Path) -> None:
    validator = FileExistsValidator(existing_file)
    existing_file.unlink()

    with pytest.raises(FileNotFoundError):
        await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_directory(tmp_path: Path) -> None:
    validator = FileExistsValidator(tmp_path)

    await validator.validate()
