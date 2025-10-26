from pathlib import Path

import pytest

from notionary.exceptions.file_upload import (
    NoFileExtensionException,
    UnsupportedFileTypeException,
)
from notionary.file_upload.validation.validators import FileExtensionValidator


@pytest.fixture
def pdf_filename() -> str:
    return "document.pdf"


@pytest.fixture
def jpg_filename() -> str:
    return "image.jpg"


@pytest.fixture
def mp4_filename() -> str:
    return "video.mp4"


@pytest.fixture
def mp3_filename() -> str:
    return "audio.mp3"


@pytest.mark.asyncio
async def test_validate_passes_for_pdf_document(pdf_filename: str) -> None:
    validator = FileExtensionValidator(pdf_filename)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_jpg_image(jpg_filename: str) -> None:
    validator = FileExtensionValidator(jpg_filename)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_mp4_video(mp4_filename: str) -> None:
    validator = FileExtensionValidator(mp4_filename)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_mp3_audio(mp3_filename: str) -> None:
    validator = FileExtensionValidator(mp3_filename)

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_uppercase_extension() -> None:
    validator = FileExtensionValidator("document.PDF")

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_path_object() -> None:
    validator = FileExtensionValidator(Path("folder/subfolder/image.png"))

    await validator.validate()


@pytest.mark.asyncio
async def test_validate_fails_for_unsupported_extension() -> None:
    validator = FileExtensionValidator("script.xyz")

    with pytest.raises(UnsupportedFileTypeException) as exc_info:
        await validator.validate()

    assert exc_info.value.extension == ".xyz"
    assert exc_info.value.filename == "script.xyz"
    assert "audio:" in str(exc_info.value)
    assert "document:" in str(exc_info.value)
    assert "image:" in str(exc_info.value)
    assert "video:" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_fails_for_file_without_extension() -> None:
    validator = FileExtensionValidator("file_without_extension")

    with pytest.raises(NoFileExtensionException) as exc_info:
        await validator.validate()

    assert exc_info.value.filename == "file_without_extension"
    assert "no extension" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_validate_passes_for_all_image_extensions() -> None:
    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".webp",
        ".heic",
        ".tif",
        ".tiff",
        ".ico",
    ]

    for ext in image_extensions:
        validator = FileExtensionValidator(f"image{ext}")
        await validator.validate()


@pytest.mark.asyncio
async def test_validate_passes_for_all_document_extensions() -> None:
    document_extensions = [
        ".pdf",
        ".txt",
        ".json",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    ]

    for ext in document_extensions:
        validator = FileExtensionValidator(f"document{ext}")
        await validator.validate()


@pytest.mark.asyncio
async def test_validate_extracts_filename_from_path() -> None:
    validator = FileExtensionValidator(Path("/some/long/path/document.pdf"))

    assert validator.filename == "document.pdf"
    await validator.validate()


@pytest.mark.asyncio
async def test_validate_handles_multiple_dots_in_filename() -> None:
    validator = FileExtensionValidator("my.file.with.dots.pdf")

    await validator.validate()
