from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from notionary.file_upload.client import FileUploadHttpClient
from notionary.file_upload.schemas import (
    FileUploadQuery,
    FileUploadResponse,
    FileUploadStatus,
    UploadMode,
)

_UPLOAD_ID = UUID("00000000-0000-0000-0000-000000000001")
_UPLOAD_ID_2 = UUID("00000000-0000-0000-0000-000000000002")


def _make_upload_response_dict(**overrides: Any) -> dict[str, Any]:
    return {
        "id": str(_UPLOAD_ID),
        "created_time": "2024-01-01T00:00:00.000Z",
        "last_edited_time": "2024-01-01T00:00:00.000Z",
        "expiry_time": None,
        "upload_url": None,
        "in_trash": False,
        "status": FileUploadStatus.PENDING,
        "filename": "test.pdf",
        "content_type": "application/pdf",
        "content_length": None,
        "request_id": None,
        **overrides,
    }


@pytest.fixture
def mock_http() -> MagicMock:
    http = MagicMock()
    http.post = AsyncMock(return_value=_make_upload_response_dict())
    http.post_multipart = AsyncMock(return_value=_make_upload_response_dict())
    http.get = AsyncMock(return_value=_make_upload_response_dict())
    http.paginate = AsyncMock(return_value=[_make_upload_response_dict()])
    return http


@pytest.fixture
def client(mock_http: MagicMock) -> FileUploadHttpClient:
    return FileUploadHttpClient(mock_http)


class TestCreateSinglePartUpload:
    @pytest.mark.asyncio
    async def test_returns_file_upload_response(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.create_single_part_upload("test.pdf", "application/pdf")

        assert isinstance(result, FileUploadResponse)
        assert result.id == _UPLOAD_ID

    @pytest.mark.asyncio
    async def test_posts_to_file_uploads_endpoint(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_single_part_upload("test.pdf")

        mock_http.post.assert_called_once()
        assert mock_http.post.call_args.args[0] == "file_uploads"

    @pytest.mark.asyncio
    async def test_sends_single_part_mode(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_single_part_upload("test.pdf")

        data = mock_http.post.call_args.kwargs["data"]
        assert data["mode"] == UploadMode.SINGLE_PART

    @pytest.mark.asyncio
    async def test_excludes_number_of_parts_from_payload(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_single_part_upload("test.pdf")

        data = mock_http.post.call_args.kwargs["data"]
        assert "number_of_parts" not in data

    @pytest.mark.asyncio
    async def test_without_content_type_omits_field(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_single_part_upload("test.pdf")

        data = mock_http.post.call_args.kwargs["data"]
        assert "content_type" not in data


class TestCreateMultiPartUpload:
    @pytest.mark.asyncio
    async def test_returns_file_upload_response(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.create_multi_part_upload("big.pdf", 3, "application/pdf")

        assert isinstance(result, FileUploadResponse)
        assert result.id == _UPLOAD_ID

    @pytest.mark.asyncio
    async def test_sends_multi_part_mode(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_multi_part_upload("big.pdf", 3)

        data = mock_http.post.call_args.kwargs["data"]
        assert data["mode"] == UploadMode.MULTI_PART

    @pytest.mark.asyncio
    async def test_includes_number_of_parts_in_payload(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.create_multi_part_upload("big.pdf", 3)

        data = mock_http.post.call_args.kwargs["data"]
        assert data["number_of_parts"] == 3


class TestSendFileContent:
    @pytest.mark.asyncio
    async def test_posts_to_send_endpoint(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.send_file_content(_UPLOAD_ID, b"content", "test.pdf")

        assert (
            mock_http.post_multipart.call_args.args[0]
            == f"file_uploads/{_UPLOAD_ID}/send"
        )

    @pytest.mark.asyncio
    async def test_sends_file_bytes_in_files_param(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.send_file_content(_UPLOAD_ID, b"hello", "test.pdf")

        files = mock_http.post_multipart.call_args.kwargs["files"]
        assert files == {"file": ("test.pdf", b"hello")}

    @pytest.mark.asyncio
    async def test_without_part_number_passes_none_data(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.send_file_content(_UPLOAD_ID, b"content", "test.pdf")

        data = mock_http.post_multipart.call_args.kwargs["data"]
        assert data is None

    @pytest.mark.asyncio
    async def test_with_part_number_includes_it_in_data(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.send_file_content(
            _UPLOAD_ID, b"content", "test.pdf", part_number=2
        )

        data = mock_http.post_multipart.call_args.kwargs["data"]
        assert data == {"part_number": "2"}

    @pytest.mark.asyncio
    async def test_returns_file_upload_response(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.send_file_content(_UPLOAD_ID, b"data", "test.pdf")

        assert isinstance(result, FileUploadResponse)


class TestCompleteUpload:
    @pytest.mark.asyncio
    async def test_posts_to_complete_endpoint(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.complete_upload(_UPLOAD_ID)

        assert mock_http.post.call_args.args[0] == f"file_uploads/{_UPLOAD_ID}/complete"

    @pytest.mark.asyncio
    async def test_returns_file_upload_response(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.complete_upload(_UPLOAD_ID)

        assert isinstance(result, FileUploadResponse)


class TestGetFileUpload:
    @pytest.mark.asyncio
    async def test_gets_from_correct_endpoint(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.get_file_upload(_UPLOAD_ID)

        mock_http.get.assert_called_once_with(f"file_uploads/{_UPLOAD_ID}")

    @pytest.mark.asyncio
    async def test_returns_file_upload_response(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.get_file_upload(_UPLOAD_ID)

        assert isinstance(result, FileUploadResponse)
        assert result.id == _UPLOAD_ID


class TestListFiles:
    @pytest.mark.asyncio
    async def test_returns_list_of_responses(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        result = await client.list_file_uploads()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], FileUploadResponse)

    @pytest.mark.asyncio
    async def test_calls_paginate_on_file_uploads_endpoint(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.list_file_uploads()

        mock_http.paginate.assert_called_once()
        assert mock_http.paginate.call_args.args[0] == "file_uploads"

    @pytest.mark.asyncio
    async def test_passes_status_filter_to_paginate(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        query = FileUploadQuery(status=FileUploadStatus.UPLOADED)
        await client.list_file_uploads(query)

        kwargs = mock_http.paginate.call_args.kwargs
        assert kwargs["status"] == FileUploadStatus.UPLOADED

    @pytest.mark.asyncio
    async def test_passes_total_results_limit_to_paginate(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        query = FileUploadQuery(total_results_limit=10)
        await client.list_file_uploads(query)

        kwargs = mock_http.paginate.call_args.kwargs
        assert kwargs["total_results_limit"] == 10

    @pytest.mark.asyncio
    async def test_without_query_uses_defaults(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        await client.list_file_uploads(None)

        mock_http.paginate.assert_called_once()


class TestListFilesStream:
    @pytest.mark.asyncio
    async def test_yields_file_upload_responses(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        async def _fake_stream(*args: Any, **kwargs: Any) -> AsyncGenerator[dict]:
            yield _make_upload_response_dict()
            yield _make_upload_response_dict(id=str(_UPLOAD_ID_2))

        mock_http.paginate_stream = _fake_stream

        results = []
        async for upload in client.list_file_uploads_stream():
            results.append(upload)

        assert len(results) == 2
        assert results[0].id == _UPLOAD_ID
        assert results[1].id == _UPLOAD_ID_2

    @pytest.mark.asyncio
    async def test_yields_file_upload_response_instances(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        async def _fake_stream(*args: Any, **kwargs: Any) -> AsyncGenerator[dict]:
            yield _make_upload_response_dict()

        mock_http.paginate_stream = _fake_stream

        results = []
        async for upload in client.list_file_uploads_stream():
            results.append(upload)

        assert all(isinstance(r, FileUploadResponse) for r in results)

    @pytest.mark.asyncio
    async def test_passes_query_to_stream(
        self, client: FileUploadHttpClient, mock_http: MagicMock
    ) -> None:
        received_kwargs: dict[str, Any] = {}

        async def _fake_stream(*args: Any, **kwargs: Any) -> AsyncGenerator[dict]:
            received_kwargs.update(kwargs)
            yield _make_upload_response_dict()

        mock_http.paginate_stream = _fake_stream
        query = FileUploadQuery(status=FileUploadStatus.PENDING)

        async for _ in client.list_file_uploads_stream(query):
            pass

        assert received_kwargs.get("status") == FileUploadStatus.PENDING
