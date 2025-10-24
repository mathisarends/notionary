import asyncio
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles

from notionary.exceptions.file_upload import UploadFailedError, UploadTimeoutError
from notionary.file_upload.client import FileUploadHttpClient
from notionary.file_upload.config import FileUploadConfig
from notionary.file_upload.schemas import FileUploadResponse, FileUploadStatus
from notionary.file_upload.validation.factory import (
    create_bytes_upload_validator_service,
    create_file_upload_validator_service,
)
from notionary.utils.mixins.logging import LoggingMixin


class FileUploadService(LoggingMixin):
    def __init__(self, client: FileUploadHttpClient | None = None, config: FileUploadConfig | None = None):
        self.client = client or FileUploadHttpClient()
        self.config = config or FileUploadConfig()

    async def upload_file(self, file_path: Path, filename: str | None = None) -> FileUploadResponse:
        file_size = file_path.stat().st_size
        filename = filename or file_path.name

        # Validierung über Validator-Chain
        validator_service = create_file_upload_validator_service(
            file_path=file_path,
            filename=filename,
            file_size_bytes=file_size,
        )
        await validator_service.validate_all()

        if self._fits_in_single_part(file_size):
            return await self._upload_in_single_part(file_path, filename)

        return await self._upload_in_multiple_parts(file_path, filename, file_size)

    async def upload_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        file_size = len(file_content)

        validator_service = create_bytes_upload_validator_service(
            filename=filename,
            file_size_bytes=file_size,
        )
        await validator_service.validate_all()

        content_type = content_type or self._guess_content_type(filename)

        if self._fits_in_single_part(file_size):
            return await self._upload_bytes_in_single_part(file_content, filename, content_type)

        return await self._upload_bytes_in_multiple_parts(file_content, filename, content_type, file_size)

    async def get_upload_status(self, file_upload_id: str) -> str:
        try:
            upload_info = await self.client.get_file_upload(file_upload_id)
            return upload_info.status
        except Exception as e:
            raise UploadFailedError(file_upload_id, reason=str(e)) from e

    async def wait_for_completion(
        self,
        file_upload_id: str,
        timeout_seconds: int | None = None,
    ) -> FileUploadResponse:
        timeout = timeout_seconds or self.config.MAX_UPLOAD_TIMEOUT
        deadline = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() < deadline:
            upload_info = await self.client.get_file_upload(file_upload_id)

            if upload_info.status == FileUploadStatus.UPLOADED:
                self.logger.info("Upload completed: %s", file_upload_id)
                return upload_info

            if upload_info.status == FileUploadStatus.FAILED:
                raise UploadFailedError(file_upload_id)

            await asyncio.sleep(self.config.POLL_INTERVAL)

        raise UploadTimeoutError(file_upload_id, timeout)

    async def list_recent_uploads(self, limit: int = 50) -> list[FileUploadResponse]:
        response = await self.client.list_file_uploads(
            page_size=min(limit, 100),
            total_results_limit=limit,
        )
        return response.results[:limit]

    def _fits_in_single_part(self, file_size: int) -> bool:
        return file_size <= self.config.SINGLE_PART_MAX_SIZE

    def _guess_content_type(self, filename: str) -> str | None:
        content_type, _ = mimetypes.guess_type(filename)
        return content_type

    def _calculate_part_count(self, file_size: int) -> int:
        return (file_size + self.config.MULTI_PART_CHUNK_SIZE - 1) // self.config.MULTI_PART_CHUNK_SIZE

    async def _upload_in_single_part(self, file_path: Path, filename: str) -> FileUploadResponse:
        content_type = self._guess_content_type(filename)

        file_upload = await self.client.create_single_part_upload(
            filename=filename,
            content_type=content_type,
        )

        await self.client.send_file_from_path(
            file_upload_id=file_upload.id,
            file_path=file_path,
        )

        self.logger.info("Single-part upload completed: %s (ID: %s)", filename, file_upload.id)
        return file_upload

    async def _upload_bytes_in_single_part(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
    ) -> FileUploadResponse:
        file_upload = await self.client.create_single_part_upload(
            filename=filename,
            content_type=content_type,
        )

        await self.client.send_file_content(
            file_upload_id=file_upload.id,
            file_content=file_content,
            filename=filename,
        )

        self.logger.info("Single-part upload from bytes completed: %s (ID: %s)", filename, file_upload.id)
        return file_upload

    async def _upload_in_multiple_parts(
        self,
        file_path: Path,
        filename: str,
        file_size: int,
    ) -> FileUploadResponse:
        content_type = self._guess_content_type(filename)
        part_count = self._calculate_part_count(file_size)

        file_upload = await self.client.create_multi_part_upload(
            filename=filename,
            content_type=content_type,
            number_of_parts=part_count,
        )

        await self._send_file_parts(file_upload.id, file_path, part_count)

        completed_upload = await self.client.complete_upload(file_upload.id)

        self.logger.info("Multi-part upload completed: %s (ID: %s)", filename, file_upload.id)
        return completed_upload

    async def _upload_bytes_in_multiple_parts(
        self,
        file_content: bytes,
        filename: str,
        content_type: str | None,
        file_size: int,
    ) -> FileUploadResponse:
        part_count = self._calculate_part_count(file_size)

        file_upload = await self.client.create_multi_part_upload(
            filename=filename,
            content_type=content_type,
            number_of_parts=part_count,
        )

        await self._send_bytes_parts(file_upload.id, file_content, filename, part_count)

        completed_upload = await self.client.complete_upload(file_upload.id)

        self.logger.info("Multi-part upload from bytes completed: %s (ID: %s)", filename, file_upload.id)
        return completed_upload

    async def _send_file_parts(
        self,
        file_upload_id: str,
        file_path: Path,
        total_parts: int,
    ) -> None:
        part_number = 1

        try:
            async with aiofiles.open(file_path, "rb") as file:
                while True:
                    chunk = await file.read(self.config.MULTI_PART_CHUNK_SIZE)
                    if not chunk:
                        break

                    await self.client.send_file_content(
                        file_upload_id=file_upload_id,
                        file_content=chunk,
                        filename=file_path.name,
                        part_number=part_number,
                    )

                    self.logger.debug("Uploaded part %d/%d", part_number, total_parts)
                    part_number += 1

        except Exception as e:
            raise UploadFailedError(
                file_upload_id=file_upload_id, reason=f"Failed to upload part {part_number}/{total_parts}: {e}"
            ) from e

    async def _send_bytes_parts(
        self,
        file_upload_id: str,
        file_content: bytes,
        filename: str,
        total_parts: int,
    ) -> None:
        chunk_size = self.config.MULTI_PART_CHUNK_SIZE
        part_number = 1

        try:
            for part_number in range(1, total_parts + 1):
                start = (part_number - 1) * chunk_size
                end = start + chunk_size
                chunk = file_content[start:end]

                await self.client.send_file_content(
                    file_upload_id=file_upload_id,
                    file_content=chunk,
                    filename=filename,
                    part_number=part_number,
                )

                self.logger.debug("Uploaded part %d/%d", part_number, total_parts)

        except Exception as e:
            raise UploadFailedError(
                file_upload_id=file_upload_id, reason=f"Failed to upload part {part_number}/{total_parts}: {e}"
            ) from e
