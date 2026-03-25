import asyncio
import logging
import mimetypes
import os
from collections.abc import AsyncGenerator, AsyncIterator, Generator
from pathlib import Path

import aiofiles

from notionary.file_upload.client import FileUploadHttpClient
from notionary.file_upload.exceptions import (
    FilenameTooLongError,
    FileNotFoundError,
    NoFileExtensionException,
    UnsupportedFileTypeException,
    UploadFailedError,
    UploadTimeoutError,
)
from notionary.file_upload.schemas import (
    FileUploadConfig,
    FileUploadQuery,
    FileUploadResponse,
    FileUploadStatus,
)
from notionary.http import HttpClient

logger = logging.getLogger(__name__)


class FileUploads:
    _SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
        {
            ".aac",
            ".adts",
            ".mid",
            ".midi",
            ".mp3",
            ".mpga",
            ".m4a",
            ".m4b",
            ".oga",
            ".ogg",
            ".wav",
            ".wma",
            ".pdf",
            ".txt",
            ".json",
            ".doc",
            ".dot",
            ".docx",
            ".dotx",
            ".xls",
            ".xlt",
            ".xla",
            ".xlsx",
            ".xltx",
            ".ppt",
            ".pot",
            ".pps",
            ".ppa",
            ".pptx",
            ".potx",
            ".gif",
            ".heic",
            ".jpeg",
            ".jpg",
            ".png",
            ".svg",
            ".tif",
            ".tiff",
            ".webp",
            ".ico",
            ".amv",
            ".asf",
            ".wmv",
            ".avi",
            ".f4v",
            ".flv",
            ".gifv",
            ".m4v",
            ".mp4",
            ".mkv",
            ".webm",
            ".mov",
            ".qt",
            ".mpeg",
        }
    )

    def __init__(self, http: HttpClient) -> None:
        self._client = FileUploadHttpClient(http)
        self._config = FileUploadConfig()

    async def upload_file(
        self,
        file_path: Path,
        filename: str | None = None,
        *,
        wait: bool = True,
    ) -> FileUploadResponse:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            raise FileNotFoundError(str(file_path))

        filename = filename or file_path.name
        self._validate_filename(filename)

        content_type = self._guess_content_type(filename)
        file_size = file_path.stat().st_size

        if self._is_single_part(file_size):
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
            return await self._upload_single_part(content, filename, content_type, wait)

        return await self._upload_multi_part(
            filename, content_type, file_size, self._iter_file_chunks(file_path), wait
        )

    async def upload_from_bytes(
        self,
        content: bytes,
        filename: str,
        content_type: str | None = None,
        *,
        wait: bool = True,
    ) -> FileUploadResponse:
        self._validate_filename(filename)

        content_type = content_type or self._guess_content_type(filename)
        file_size = len(content)

        if self._is_single_part(file_size):
            return await self._upload_single_part(content, filename, content_type, wait)

        return await self._upload_multi_part(
            filename, content_type, file_size, self._iter_byte_chunks(content), wait
        )

    async def get(self, file_upload_id: str) -> FileUploadResponse:
        return await self._client.get_file_upload(file_upload_id)

    async def list(
        self,
        *,
        status: FileUploadStatus | None = None,
        archived: bool | None = None,
        page_size_limit: int | None = None,
        total_results_limit: int | None = None,
    ) -> list[FileUploadResponse]:
        query = FileUploadQuery(
            status=status,
            archived=archived,
            page_size_limit=page_size_limit,
            total_results_limit=total_results_limit,
        )
        return await self._client.list_file_uploads(query)

    async def iter(
        self,
        *,
        status: FileUploadStatus | None = None,
        archived: bool | None = None,
        page_size_limit: int | None = None,
        total_results_limit: int | None = None,
    ) -> AsyncIterator[FileUploadResponse]:
        query = FileUploadQuery(
            status=status,
            archived=archived,
            page_size_limit=page_size_limit,
            total_results_limit=total_results_limit,
        )
        async for upload in self._client.list_file_uploads_stream(query):
            yield upload

    async def _upload_single_part(
        self, content: bytes, filename: str, content_type: str | None, wait: bool
    ) -> FileUploadResponse:
        upload = await self._client.create_single_part_upload(filename, content_type)
        await self._client.send_file_content(upload.id, content, filename)

        if not wait:
            return upload

        logger.info(
            "Single-part upload sent, waiting for completion... (ID: %s)", upload.id
        )
        return await self._wait_for_completion(upload.id)

    async def _upload_multi_part(
        self,
        filename: str,
        content_type: str | None,
        file_size: int,
        chunks: AsyncGenerator[bytes],
        wait: bool,
    ) -> FileUploadResponse:
        part_count = self._calculate_part_count(file_size)
        upload = await self._client.create_multi_part_upload(
            filename, part_count, content_type
        )

        part_number = 1
        try:
            async for chunk in chunks:
                await self._client.send_file_content(
                    upload.id, chunk, filename, part_number
                )
                logger.debug("Uploaded part %d/%d", part_number, part_count)
                part_number += 1
        except Exception as e:
            raise UploadFailedError(
                upload.id, reason=f"Failed on part {part_number}/{part_count}: {e}"
            ) from e

        await self._client.complete_upload(upload.id)

        if not wait:
            return upload

        logger.info(
            "Multi-part upload sent, waiting for completion... (ID: %s)", upload.id
        )
        return await self._wait_for_completion(upload.id)

    async def _wait_for_completion(self, file_upload_id: str) -> FileUploadResponse:
        try:
            return await asyncio.wait_for(
                self._poll_until_complete(file_upload_id),
                timeout=self._config.max_upload_timeout,
            )
        except TimeoutError as e:
            raise UploadTimeoutError(
                file_upload_id, self._config.max_upload_timeout
            ) from e

    async def _poll_until_complete(self, file_upload_id: str) -> FileUploadResponse:
        while True:
            upload = await self._client.get_file_upload(file_upload_id)
            if upload.status == FileUploadStatus.UPLOADED:
                logger.info("Upload completed: %s", file_upload_id)
                return upload
            if upload.status == FileUploadStatus.FAILED:
                raise UploadFailedError(file_upload_id)
            await asyncio.sleep(self._config.poll_interval)

    async def _iter_file_chunks(self, file_path: Path) -> AsyncGenerator[bytes]:
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(self._config.multi_part_chunk_size):
                yield chunk

    def _iter_byte_chunks(self, content: bytes) -> Generator[bytes]:
        size = self._config.multi_part_chunk_size
        for i in range(0, len(content), size):
            yield content[i : i + size]

    def _is_single_part(self, file_size: int) -> bool:
        return file_size <= self._config._SINGLE_PART_MAX_SIZE

    def _calculate_part_count(self, file_size: int) -> int:
        return (
            file_size + self._config.multi_part_chunk_size - 1
        ) // self._config.multi_part_chunk_size

    def _validate_filename(self, filename: str) -> None:
        filename_bytes = len(filename.encode("utf-8"))
        if filename_bytes > self._config._MAX_FILENAME_BYTES:
            raise FilenameTooLongError(
                filename, filename_bytes, self._config._MAX_FILENAME_BYTES
            )

        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if not ext:
            raise NoFileExtensionException(filename)
        if ext not in self._SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeException(ext, filename)

    @staticmethod
    def _guess_content_type(filename: str) -> str | None:
        content_type, _ = mimetypes.guess_type(filename)
        return content_type
