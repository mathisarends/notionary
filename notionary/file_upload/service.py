import asyncio
import mimetypes
from collections.abc import AsyncGenerator, AsyncIterator, Callable
from pathlib import Path

from notionary.exceptions.file_upload import UploadFailedError, UploadTimeoutError
from notionary.file_upload.client import FileUploadHttpClient
from notionary.file_upload.config import NOTION_SINGLE_PART_MAX_SIZE, FileUploadConfig
from notionary.file_upload.file.reader import FileContentReader
from notionary.file_upload.query import FileUploadQuery, FileUploadQueryBuilder
from notionary.file_upload.schemas import FileUploadResponse, FileUploadStatus
from notionary.file_upload.validation.factory import (
    create_bytes_upload_validation_service,
    create_file_upload_validation_service,
)
from notionary.utils.mixins.logging import LoggingMixin


class NotionFileUpload(LoggingMixin):
    def __init__(
        self,
        client: FileUploadHttpClient | None = None,
        config: FileUploadConfig | None = None,
        file_reader: FileContentReader | None = None,
    ):
        self._client = client or FileUploadHttpClient()
        self._config = config or FileUploadConfig()
        self._file_reader = file_reader or FileContentReader(config=self._config)

    async def upload_file(self, file_path: Path, filename: str | None = None) -> FileUploadResponse:
        file_path = Path(file_path)

        if not file_path.is_absolute() and self._config.base_upload_path:
            file_path = Path(self._config.base_upload_path) / file_path
        file_path = file_path.resolve()

        validator_service = create_file_upload_validation_service(file_path)
        await validator_service.validate()

        file_size = file_path.stat().st_size
        filename = filename or file_path.name
        content_type = self._guess_content_type(filename)

        if self._fits_in_single_part(file_size):
            content = await self._file_reader.read_full_file(file_path)
            return await self._upload_single_part_content(content, filename, content_type)
        else:
            return await self._upload_multi_part_content(
                filename, content_type, file_size, self._file_reader.read_file_chunks(file_path)
            )

    async def upload_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        file_size = len(file_content)

        validator_service = create_bytes_upload_validation_service(
            filename=filename,
            file_size_bytes=file_size,
        )
        await validator_service.validate()

        content_type = content_type or self._guess_content_type(filename)

        if self._fits_in_single_part(file_size):
            return await self._upload_single_part_content(file_content, filename, content_type)

        return await self._upload_multi_part_content(
            filename, content_type, file_size, self._file_reader.bytes_to_chunks(file_content)
        )

    async def _upload_single_part_content(
        self, content: bytes, filename: str, content_type: str | None
    ) -> FileUploadResponse:
        file_upload = await self._client.create_single_part_upload(
            filename=filename,
            content_type=content_type,
        )

        await self._client.send_file_content(
            file_upload_id=file_upload.id,
            file_content=content,
            filename=filename,
        )

        self.logger.info("Single-part content sent, waiting for completion... (ID: %s)", file_upload.id)
        return await self._wait_for_completion(file_upload.id)

    async def _upload_multi_part_content(
        self,
        filename: str,
        content_type: str | None,
        file_size: int,
        chunk_generator: AsyncGenerator[bytes],
    ) -> FileUploadResponse:
        part_count = self._calculate_part_count(file_size)

        file_upload = await self._client.create_multi_part_upload(
            filename=filename,
            content_type=content_type,
            number_of_parts=part_count,
        )

        await self._send_parts(file_upload.id, filename, part_count, chunk_generator)

        await self._client.complete_upload(file_upload.id)

        self.logger.info("Multi-part content sent, waiting for completion... (ID: %s)", file_upload.id)
        return await self._wait_for_completion(file_upload.id)

    async def _send_parts(
        self,
        file_upload_id: str,
        filename: str,
        total_parts: int,
        chunk_generator: AsyncGenerator[bytes],
    ) -> None:
        part_number = 1
        try:
            async for chunk in chunk_generator:
                await self._client.send_file_content(
                    file_upload_id=file_upload_id,
                    file_content=chunk,
                    filename=filename,
                    part_number=part_number,
                )

                self.logger.debug("Uploaded part %d/%d", part_number, total_parts)
                part_number += 1

        except Exception as e:
            raise UploadFailedError(
                file_upload_id=file_upload_id, reason=f"Failed to upload part {part_number}/{total_parts}: {e}"
            ) from e

    def _fits_in_single_part(self, file_size: int) -> bool:
        return file_size <= NOTION_SINGLE_PART_MAX_SIZE

    def _guess_content_type(self, filename: str) -> str | None:
        content_type, _ = mimetypes.guess_type(filename)
        return content_type

    def _calculate_part_count(self, file_size: int) -> int:
        return (file_size + self._config.multi_part_chunk_size - 1) // self._config.multi_part_chunk_size

    async def get_upload_status(self, file_upload_id: str) -> str:
        try:
            upload_info = await self._client.get_file_upload(file_upload_id)
            return upload_info.status
        except Exception as e:
            raise UploadFailedError(file_upload_id, reason=str(e)) from e

    async def _wait_for_completion(
        self,
        file_upload_id: str,
        timeout_seconds: int | None = None,
    ) -> FileUploadResponse:
        timeout = timeout_seconds or self._config.max_upload_timeout

        try:
            return await asyncio.wait_for(self._poll_status_until_complete(file_upload_id), timeout=timeout)

        except TimeoutError as e:
            raise UploadTimeoutError(file_upload_id, timeout) from e

    async def _poll_status_until_complete(self, file_upload_id: str) -> FileUploadResponse:
        while True:
            upload_info = await self._client.get_file_upload(file_upload_id)

            if upload_info.status == FileUploadStatus.UPLOADED:
                self.logger.info("Upload completed: %s", file_upload_id)
                return upload_info

            if upload_info.status == FileUploadStatus.FAILED:
                raise UploadFailedError(file_upload_id)

            await asyncio.sleep(self._config.poll_interval)

    async def get_uploads(
        self,
        *,
        filter_fn: Callable[[FileUploadQueryBuilder], FileUploadQueryBuilder] | None = None,
        query: FileUploadQuery | None = None,
    ) -> list[FileUploadResponse]:
        resolved_query = self._resolve_query(filter_fn=filter_fn, query=query)
        return await self._client.list_file_uploads(query=resolved_query)

    async def iter_uploads(
        self,
        *,
        filter_fn: Callable[[FileUploadQueryBuilder], FileUploadQueryBuilder] | None = None,
        query: FileUploadQuery | None = None,
    ) -> AsyncIterator[FileUploadResponse]:
        resolved_query = self._resolve_query(filter_fn=filter_fn, query=query)
        async for upload in self._client.list_file_uploads_stream(query=resolved_query):
            yield upload

    def _resolve_query(
        self,
        filter_fn: Callable[[FileUploadQueryBuilder], FileUploadQueryBuilder] | None = None,
        query: FileUploadQuery | None = None,
    ) -> FileUploadQuery:
        if filter_fn and query:
            raise ValueError("Use either filter_fn OR query, not both")

        if filter_fn:
            builder = FileUploadQueryBuilder()
            configured_builder = filter_fn(builder)
            return configured_builder.build()

        return query or FileUploadQuery()
