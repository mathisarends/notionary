import asyncio
import mimetypes
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional

from notionary.file_upload.models import FileUploadResponse
from notionary.util import LoggingMixin


class NotionFileUpload(LoggingMixin):
    """
    High-level service for managing Notion file uploads.
    Handles both small file (single-part) and large file (multi-part) uploads.
    """

    # Notion's file size limits
    SINGLE_PART_MAX_SIZE = 20 * 1024 * 1024  # 20MB
    MULTI_PART_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB per part
    MAX_FILENAME_BYTES = 900

    def __init__(self, token: Optional[str] = None):
        """Initialize the file upload service."""
        from notionary.file_upload import NotionFileUploadClient

        self.client = NotionFileUploadClient(token=token)

    async def upload_file(
        self, file_path: Path, filename: Optional[str] = None
    ) -> Optional[FileUploadResponse]:
        """
        Upload a file to Notion, automatically choosing single-part or multi-part based on size.

        Args:
            file_path: Path to the file to upload
            filename: Optional custom filename (defaults to file_path.name)

        Returns:
            FileUploadResponse if successful, None otherwise
        """
        if not file_path.exists():
            self.logger.error("File does not exist: %s", file_path)
            return None

        file_size = file_path.stat().st_size
        filename = filename or file_path.name

        # Validate filename length
        if len(filename.encode("utf-8")) > self.MAX_FILENAME_BYTES:
            self.logger.error(
                "Filename too long: %d bytes (max %d)",
                len(filename.encode("utf-8")),
                self.MAX_FILENAME_BYTES,
            )
            return None

        # Choose upload method based on file size
        if file_size <= self.SINGLE_PART_MAX_SIZE:
            return await self._upload_small_file(file_path, filename, file_size)
        else:
            return await self._upload_large_file(file_path, filename, file_size)

    async def upload_from_bytes(
        self, file_content: bytes, filename: str, content_type: Optional[str] = None
    ) -> Optional[FileUploadResponse]:
        """
        Upload file content from bytes.

        Args:
            file_content: File content as bytes
            filename: Name for the file
            content_type: Optional MIME type

        Returns:
            FileUploadResponse if successful, None otherwise
        """
        file_size = len(file_content)

        # Validate filename length
        if len(filename.encode("utf-8")) > self.MAX_FILENAME_BYTES:
            self.logger.error(
                "Filename too long: %d bytes (max %d)",
                len(filename.encode("utf-8")),
                self.MAX_FILENAME_BYTES,
            )
            return None

        # Guess content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)

        # Choose upload method based on size
        if file_size <= self.SINGLE_PART_MAX_SIZE:
            return await self._upload_small_file_from_bytes(
                file_content, filename, content_type, file_size
            )
        else:
            return await self._upload_large_file_from_bytes(
                file_content, filename, content_type, file_size
            )

    async def get_upload_status(self, file_upload_id: str) -> Optional[str]:
        """
        Get the current status of a file upload.

        Args:
            file_upload_id: ID of the file upload

        Returns:
            Status string ("pending", "uploaded", etc.) or None if failed
        """
        upload_info = await self.client.retrieve_file_upload(file_upload_id)
        return upload_info.status if upload_info else None

    async def wait_for_upload_completion(
        self, file_upload_id: str, timeout_seconds: int = 300, poll_interval: int = 2
    ) -> Optional[FileUploadResponse]:
        """
        Wait for a file upload to complete.

        Args:
            file_upload_id: ID of the file upload
            timeout_seconds: Maximum time to wait
            poll_interval: Seconds between status checks

        Returns:
            FileUploadResponse when complete, None if timeout or failed
        """
        start_time = datetime.now()
        timeout_delta = timedelta(seconds=timeout_seconds)

        while datetime.now() - start_time < timeout_delta:
            upload_info = await self.client.retrieve_file_upload(file_upload_id)

            if not upload_info:
                self.logger.error(
                    "Failed to retrieve upload info for %s", file_upload_id
                )
                return None

            if upload_info.status == "uploaded":
                self.logger.info("Upload completed: %s", file_upload_id)
                return upload_info
            elif upload_info.status == "failed":
                self.logger.error("Upload failed: %s", file_upload_id)
                return None

            await asyncio.sleep(poll_interval)

        self.logger.warning("Upload timeout: %s", file_upload_id)
        return None

    async def list_recent_uploads(self, limit: int = 50) -> list[FileUploadResponse]:
        """
        List recent file uploads.

        Args:
            limit: Maximum number of uploads to return

        Returns:
            List of FileUploadResponse objects
        """
        uploads = []
        start_cursor = None
        remaining = limit

        while remaining > 0:
            page_size = min(remaining, 100)  # API max per request

            response = await self.client.list_file_uploads(
                page_size=page_size, start_cursor=start_cursor
            )

            if not response or not response.results:
                break

            uploads.extend(response.results)
            remaining -= len(response.results)

            if not response.has_more or not response.next_cursor:
                break

            start_cursor = response.next_cursor

        return uploads[:limit]

    async def _upload_small_file(
        self, file_path: Path, filename: str, file_size: int
    ) -> Optional[FileUploadResponse]:
        """Upload a small file using single-part upload."""
        content_type, _ = mimetypes.guess_type(str(file_path))

        # Create file upload
        file_upload = await self.client.create_file_upload(
            filename=filename,
            content_type=content_type,
            content_length=file_size,
            mode="single_part",
        )

        if not file_upload:
            self.logger.error("Failed to create file upload for %s", filename)
            return None

        # Send file content
        success = await self.client.send_file_from_path(
            file_upload_id=file_upload.id, file_path=file_path
        )

        if not success:
            self.logger.error("Failed to send file content for %s", filename)
            return None

        self.logger.info(
            "Successfully uploaded file: %s (ID: %s)", filename, file_upload.id
        )
        return file_upload

    async def _upload_large_file(
        self, file_path: Path, filename: str, file_size: int
    ) -> Optional[FileUploadResponse]:
        """Upload a large file using multi-part upload."""
        content_type, _ = mimetypes.guess_type(str(file_path))

        # Create file upload with multi-part mode
        file_upload = await self.client.create_file_upload(
            filename=filename,
            content_type=content_type,
            content_length=file_size,
            mode="multi_part",
        )

        if not file_upload:
            self.logger.error(
                "Failed to create multi-part file upload for %s", filename
            )
            return None

        # Upload file in parts
        success = await self._upload_file_parts(file_upload.id, file_path, file_size)

        if not success:
            self.logger.error("Failed to upload file parts for %s", filename)
            return None

        # Complete the upload
        completed_upload = await self.client.complete_file_upload(file_upload.id)

        if not completed_upload:
            self.logger.error("Failed to complete file upload for %s", filename)
            return None

        self.logger.info(
            "Successfully uploaded large file: %s (ID: %s)", filename, file_upload.id
        )
        return completed_upload

    async def _upload_small_file_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str],
        file_size: int,
    ) -> Optional[FileUploadResponse]:
        """Upload small file from bytes."""
        # Create file upload
        file_upload = await self.client.create_file_upload(
            filename=filename,
            content_type=content_type,
            content_length=file_size,
            mode="single_part",
        )

        if not file_upload:
            return None

        # Send file content
        from io import BytesIO

        success = await self.client.send_file_upload(
            file_upload_id=file_upload.id,
            file_content=BytesIO(file_content),
            filename=filename,
        )

        return file_upload if success else None

    async def _upload_large_file_from_bytes(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str],
        file_size: int,
    ) -> Optional[FileUploadResponse]:
        """Upload large file from bytes using multi-part."""
        # Create file upload
        file_upload = await self.client.create_file_upload(
            filename=filename,
            content_type=content_type,
            content_length=file_size,
            mode="multi_part",
        )

        if not file_upload:
            return None

        # Upload in chunks
        success = await self._upload_bytes_parts(file_upload.id, file_content)

        if not success:
            return None

        # Complete the upload
        return await self.client.complete_file_upload(file_upload.id)

    async def _upload_file_parts(
        self, file_upload_id: str, file_path: Path, file_size: int
    ) -> bool:
        """Upload file in parts for multi-part upload."""
        part_number = 1
        total_parts = (
            file_size + self.MULTI_PART_CHUNK_SIZE - 1
        ) // self.MULTI_PART_CHUNK_SIZE

        try:
            import aiofiles

            async with aiofiles.open(file_path, "rb") as file:
                while True:
                    chunk = await file.read(self.MULTI_PART_CHUNK_SIZE)
                    if not chunk:
                        break

                    success = await self.client.send_file_upload(
                        file_upload_id=file_upload_id,
                        file_content=BytesIO(chunk),
                        filename=file_path.name,
                        part_number=part_number,
                    )

                    if not success:
                        self.logger.error(
                            "Failed to upload part %d/%d", part_number, total_parts
                        )
                        return False

                    self.logger.debug("Uploaded part %d/%d", part_number, total_parts)
                    part_number += 1

            self.logger.info("Successfully uploaded all %d parts", total_parts)
            return True

        except Exception as e:
            self.logger.error("Error uploading file parts: %s", e)
            return False

    async def _upload_bytes_parts(
        self, file_upload_id: str, file_content: bytes
    ) -> bool:
        """Upload bytes in parts for multi-part upload."""
        part_number = 1
        total_parts = (
            len(file_content) + self.MULTI_PART_CHUNK_SIZE - 1
        ) // self.MULTI_PART_CHUNK_SIZE

        for i in range(0, len(file_content), self.MULTI_PART_CHUNK_SIZE):
            chunk = file_content[i : i + self.MULTI_PART_CHUNK_SIZE]

            success = await self.client.send_file_upload(
                file_upload_id=file_upload_id,
                file_content=BytesIO(chunk),
                part_number=part_number,
            )

            if not success:
                self.logger.error(
                    "Failed to upload part %d/%d", part_number, total_parts
                )
                return False

            self.logger.debug("Uploaded part %d/%d", part_number, total_parts)
            part_number += 1

        self.logger.info("Successfully uploaded all %d parts", total_parts)
        return True
