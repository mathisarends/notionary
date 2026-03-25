import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from notionary.file_upload.exceptions import (
    FilenameTooLongError,
    FileNotFoundError,
    NoFileExtensionException,
    UnsupportedFileTypeException,
    UploadFailedError,
    UploadTimeoutError,
)
from notionary.file_upload.namespace import FileUploads
from notionary.file_upload.schemas import FileUploadResponse, FileUploadStatus

_UPLOAD_PENDING = FileUploadResponse(
    id="upload-123",
    created_time="2024-01-01T00:00:00.000Z",
    last_edited_time="2024-01-01T00:00:00.000Z",
    archived=False,
    status=FileUploadStatus.PENDING,
    filename="test.pdf",
)

_UPLOAD_UPLOADED = FileUploadResponse(
    id="upload-123",
    created_time="2024-01-01T00:00:00.000Z",
    last_edited_time="2024-01-01T00:00:00.000Z",
    archived=False,
    status=FileUploadStatus.UPLOADED,
    filename="test.pdf",
)

_UPLOAD_FAILED = FileUploadResponse(
    id="upload-123",
    created_time="2024-01-01T00:00:00.000Z",
    last_edited_time="2024-01-01T00:00:00.000Z",
    archived=False,
    status=FileUploadStatus.FAILED,
    filename="test.pdf",
)


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.create_single_part_upload = AsyncMock(return_value=_UPLOAD_PENDING)
    client.create_multi_part_upload = AsyncMock(return_value=_UPLOAD_PENDING)
    client.send_file_content = AsyncMock(return_value=_UPLOAD_PENDING)
    client.complete_upload = AsyncMock(return_value=_UPLOAD_PENDING)
    client.get_file_upload = AsyncMock(return_value=_UPLOAD_UPLOADED)
    client.list_file_uploads = AsyncMock(return_value=[_UPLOAD_UPLOADED])
    return client


@pytest.fixture
def file_uploads(mock_client: MagicMock) -> FileUploads:
    namespace = FileUploads(MagicMock())
    namespace._client = mock_client
    return namespace


class TestUploadFile:
    @pytest.mark.asyncio
    async def test_small_file_uses_single_part(
        self, file_uploads: FileUploads, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        file = tmp_path / "test.pdf"
        file.write_bytes(b"small content")

        result = await file_uploads.upload_file(file)

        mock_client.create_single_part_upload.assert_called_once_with(
            "test.pdf", "application/pdf"
        )
        mock_client.send_file_content.assert_called_once()
        assert result.status == FileUploadStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_large_file_uses_multi_part(
        self, file_uploads: FileUploads, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        file = tmp_path / "big.pdf"
        file.write_bytes(b"content")

        with patch.object(file_uploads, "_is_single_part", return_value=False):
            result = await file_uploads.upload_file(file, wait=False)

        mock_client.create_multi_part_upload.assert_called_once()
        mock_client.complete_upload.assert_called_once()
        assert result.status == FileUploadStatus.PENDING

    @pytest.mark.asyncio
    async def test_uses_custom_filename_when_provided(
        self, file_uploads: FileUploads, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        file = tmp_path / "original.pdf"
        file.write_bytes(b"content")

        await file_uploads.upload_file(file, filename="renamed.pdf")

        mock_client.create_single_part_upload.assert_called_once_with(
            "renamed.pdf", "application/pdf"
        )

    @pytest.mark.asyncio
    async def test_no_wait_skips_polling(
        self, file_uploads: FileUploads, mock_client: MagicMock, tmp_path: Path
    ) -> None:
        file = tmp_path / "test.pdf"
        file.write_bytes(b"content")

        result = await file_uploads.upload_file(file, wait=False)

        mock_client.get_file_upload.assert_not_called()
        assert result.status == FileUploadStatus.PENDING

    @pytest.mark.asyncio
    async def test_nonexistent_file_raises_file_not_found(
        self, file_uploads: FileUploads
    ) -> None:
        with pytest.raises(FileNotFoundError, match="does not exist"):
            await file_uploads.upload_file(Path("/nonexistent/path/test.pdf"))


class TestUploadFromBytes:
    @pytest.mark.asyncio
    async def test_small_content_uses_single_part(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        result = await file_uploads.upload_from_bytes(b"hello", "test.pdf")

        mock_client.create_single_part_upload.assert_called_once()
        assert result.status == FileUploadStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_large_content_uses_multi_part(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        with patch.object(file_uploads, "_is_single_part", return_value=False):
            result = await file_uploads.upload_from_bytes(
                b"x" * 100, "big.pdf", wait=False
            )

        mock_client.create_multi_part_upload.assert_called_once()
        mock_client.complete_upload.assert_called_once()
        assert result.status == FileUploadStatus.PENDING

    @pytest.mark.asyncio
    async def test_no_wait_skips_polling(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.upload_from_bytes(b"data", "test.pdf", wait=False)

        mock_client.get_file_upload.assert_not_called()

    @pytest.mark.asyncio
    async def test_infers_content_type_from_filename(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.upload_from_bytes(b"data", "image.png", wait=False)

        mock_client.create_single_part_upload.assert_called_once_with(
            "image.png", "image/png"
        )

    @pytest.mark.asyncio
    async def test_explicit_content_type_overrides_inferred(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.upload_from_bytes(
            b"data",
            "test.pdf",
            content_type="application/octet-stream",
            wait=False,
        )

        mock_client.create_single_part_upload.assert_called_once_with(
            "test.pdf", "application/octet-stream"
        )


class TestGet:
    @pytest.mark.asyncio
    async def test_delegates_to_client_get_file_upload(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        result = await file_uploads.get("upload-123")

        mock_client.get_file_upload.assert_called_once_with("upload-123")
        assert isinstance(result, FileUploadResponse)


class TestList:
    @pytest.mark.asyncio
    async def test_returns_list_of_responses(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        result = await file_uploads.list()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], FileUploadResponse)

    @pytest.mark.asyncio
    async def test_passes_status_filter(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.list(status=FileUploadStatus.UPLOADED)

        query = mock_client.list_file_uploads.call_args.args[0]
        assert query.status == FileUploadStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_passes_archived_filter(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.list(archived=False)

        query = mock_client.list_file_uploads.call_args.args[0]
        assert query.archived is False

    @pytest.mark.asyncio
    async def test_passes_page_size_limit(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        await file_uploads.list(page_size_limit=25)

        query = mock_client.list_file_uploads.call_args.args[0]
        assert query.page_size_limit == 25


class TestIter:
    @pytest.mark.asyncio
    async def test_yields_responses_from_stream(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        async def _fake_stream(query):  # type: ignore[no-untyped-def]
            yield _UPLOAD_UPLOADED
            yield _UPLOAD_UPLOADED

        mock_client.list_file_uploads_stream = _fake_stream

        results = []
        async for item in file_uploads.iter():
            results.append(item)

        assert len(results) == 2
        assert all(isinstance(r, FileUploadResponse) for r in results)

    @pytest.mark.asyncio
    async def test_passes_status_filter_to_stream(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        received_queries: list = []

        async def _fake_stream(query):  # type: ignore[no-untyped-def]
            received_queries.append(query)
            yield _UPLOAD_UPLOADED

        mock_client.list_file_uploads_stream = _fake_stream

        async for _ in file_uploads.iter(status=FileUploadStatus.PENDING):
            pass

        assert received_queries[0].status == FileUploadStatus.PENDING


class TestValidateFilename:
    def test_valid_pdf_filename_passes(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("document.pdf")

    def test_valid_image_filename_passes(self, file_uploads: FileUploads) -> None:
        file_uploads._validate_filename("photo.jpg")

    def test_no_extension_raises(self, file_uploads: FileUploads) -> None:
        with pytest.raises(NoFileExtensionException, match="no extension"):
            file_uploads._validate_filename("noextension")

    def test_unsupported_extension_raises(self, file_uploads: FileUploads) -> None:
        with pytest.raises(UnsupportedFileTypeException, match="unsupported extension"):
            file_uploads._validate_filename("script.exe")

    def test_too_long_filename_raises(self, file_uploads: FileUploads) -> None:
        long_name = "a" * 900 + ".pdf"
        with pytest.raises(FilenameTooLongError, match="too long"):
            file_uploads._validate_filename(long_name)

    def test_extension_check_is_case_insensitive(
        self, file_uploads: FileUploads
    ) -> None:
        file_uploads._validate_filename("IMAGE.PNG")
        file_uploads._validate_filename("document.PDF")


class TestPollingAndCompletion:
    @pytest.mark.asyncio
    async def test_poll_returns_when_status_is_uploaded(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        mock_client.get_file_upload = AsyncMock(return_value=_UPLOAD_UPLOADED)

        result = await file_uploads._poll_until_complete("upload-123")

        assert result.status == FileUploadStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_poll_raises_on_failed_status(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        mock_client.get_file_upload = AsyncMock(return_value=_UPLOAD_FAILED)

        with pytest.raises(UploadFailedError, match="upload-123"):
            await file_uploads._poll_until_complete("upload-123")

    @pytest.mark.asyncio
    async def test_poll_keeps_polling_through_pending_status(
        self, file_uploads: FileUploads, mock_client: MagicMock
    ) -> None:
        mock_client.get_file_upload = AsyncMock(
            side_effect=[_UPLOAD_PENDING, _UPLOAD_PENDING, _UPLOAD_UPLOADED]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await file_uploads._poll_until_complete("upload-123")

        assert result.status == FileUploadStatus.UPLOADED
        assert mock_client.get_file_upload.call_count == 3

    @pytest.mark.asyncio
    async def test_wait_for_completion_raises_upload_timeout_error(
        self, file_uploads: FileUploads
    ) -> None:
        with (
            patch(
                "notionary.file_upload.namespace.asyncio.wait_for",
                side_effect=asyncio.TimeoutError,
            ),
            pytest.raises(UploadTimeoutError, match="upload-999"),
        ):
            await file_uploads._wait_for_completion("upload-999")


class TestIsSinglePart:
    def test_small_file_is_single_part(self, file_uploads: FileUploads) -> None:
        assert file_uploads._is_single_part(1024) is True

    def test_exactly_at_limit_is_single_part(self, file_uploads: FileUploads) -> None:
        limit = file_uploads._config._SINGLE_PART_MAX_SIZE
        assert file_uploads._is_single_part(limit) is True

    def test_above_limit_is_not_single_part(self, file_uploads: FileUploads) -> None:
        limit = file_uploads._config._SINGLE_PART_MAX_SIZE
        assert file_uploads._is_single_part(limit + 1) is False


class TestCalculatePartCount:
    def test_content_smaller_than_chunk_size_gives_one_part(
        self, file_uploads: FileUploads
    ) -> None:
        chunk_size = file_uploads._config.multi_part_chunk_size
        assert file_uploads._calculate_part_count(chunk_size - 1) == 1

    def test_content_equal_to_chunk_size_gives_one_part(
        self, file_uploads: FileUploads
    ) -> None:
        chunk_size = file_uploads._config.multi_part_chunk_size
        assert file_uploads._calculate_part_count(chunk_size) == 1

    def test_content_one_byte_over_chunk_size_gives_two_parts(
        self, file_uploads: FileUploads
    ) -> None:
        chunk_size = file_uploads._config.multi_part_chunk_size
        assert file_uploads._calculate_part_count(chunk_size + 1) == 2

    def test_content_three_chunks_gives_three_parts(
        self, file_uploads: FileUploads
    ) -> None:
        chunk_size = file_uploads._config.multi_part_chunk_size
        assert file_uploads._calculate_part_count(chunk_size * 3) == 3
