import pytest

from notionary.shared.file_upload.exceptions import (
    FilenameTooLongError,
    FileNotFoundError,
    NoFileExtensionException,
    UnsupportedFileTypeException,
)
from notionary.shared.file_upload.namespace import SUPPORTED_EXTENSIONS, FileUploads


class FakeHttpClient:
    pass


@pytest.fixture
def file_uploads() -> FileUploads:
    return FileUploads(http=FakeHttpClient())  # type: ignore[arg-type]


class TestValidateFilename:
    def test_valid_filename(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("photo.jpg")

    def test_valid_pdf(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("document.pdf")

    def test_valid_mp4(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("video.mp4")

    def test_no_extension_raises(self, file_uploads: FileUploads) -> None:
        with pytest.raises(NoFileExtensionException, match="no extension"):
            file_uploads._validate_filename("noext")

    def test_unsupported_extension_raises(self, file_uploads: FileUploads) -> None:
        with pytest.raises(UnsupportedFileTypeException, match="unsupported extension"):
            file_uploads._validate_filename("file.xyz")

    def test_filename_too_long_raises(self, file_uploads: FileUploads) -> None:
        long_name = "a" * 900 + ".png"
        with pytest.raises(FilenameTooLongError, match="Filename too long"):
            file_uploads._validate_filename(long_name)

    def test_filename_at_byte_limit_passes(self, file_uploads: FileUploads) -> None:
        name = "a" * 896 + ".png"
        assert len(name.encode("utf-8")) == 900
        file_uploads._validate_filename(name)

    def test_case_insensitive_extension(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("photo.JPG")

    def test_multibyte_filename_length(self, file_uploads: FileUploads) -> None:
        long_name = "\u00fc" * 451 + ".png"
        assert len(long_name.encode("utf-8")) > 900
        with pytest.raises(FilenameTooLongError):
            file_uploads._validate_filename(long_name)


class TestUploadFileValidation:
    @pytest.mark.asyncio
    async def test_nonexistent_file_raises(self, file_uploads: FileUploads) -> None:
        from pathlib import Path

        with pytest.raises(FileNotFoundError, match="does not exist"):
            await file_uploads.upload_file(Path("/nonexistent/file.png"))


class TestSupportedExtensions:
    def test_contains_common_image_formats(self) -> None:
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
            assert ext in SUPPORTED_EXTENSIONS

    def test_contains_common_document_formats(self) -> None:
        for ext in [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".json"]:
            assert ext in SUPPORTED_EXTENSIONS

    def test_contains_common_audio_formats(self) -> None:
        for ext in [".mp3", ".wav", ".ogg", ".aac"]:
            assert ext in SUPPORTED_EXTENSIONS

    def test_contains_common_video_formats(self) -> None:
        for ext in [".mp4", ".mkv", ".webm", ".mov", ".avi"]:
            assert ext in SUPPORTED_EXTENSIONS
