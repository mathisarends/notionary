from __future__ import annotations

import json
import os
import math
import mimetypes
import httpx
from typing import Optional, TYPE_CHECKING
from notionary.models.notion_file_upload_response import NotionFileUploadResponse
from notionary.util.logging_mixin import LoggingMixin

if TYPE_CHECKING:
    from notionary import NotionClient


class NotionFileUploader(LoggingMixin):
    """
    Handles file uploads to Notion using both single-part and multi-part methods.

    Encapsulates all file upload logic and provides a clean interface for the NotionClient.
    """

    def __init__(self, notion_client: NotionClient):
        """
        Initialize the file uploader with a reference to the NotionClient.

        Args:
            notion_client: The NotionClient instance for making API requests.
        """
        self.notion_client = notion_client

    async def upload_file(
        self,
        file_path: str,
        max_part_size: int = 20 * 1024 * 1024,
        force_multipart: bool = False,
    ) -> Optional[NotionFileUploadResponse]:
        """
        Uploads a file to Notion using the optimal method (single-part or multi-part).

        Automatically chooses single-part for files ≤5MB (free accounts) or ≤20MB (paid accounts)
        or multi-part for larger files. Single-part is attempted first for compatibility
        with free workspaces that don't support multi-part uploads.

        Args:
            file_path: Path to the file to upload.
            max_part_size: Maximum size per part for multi-part uploads (default: 20MB).
            force_multipart: If True, forces multi-part upload regardless of file size.

        Returns:
            Validated NotionFileUploadResponse or None if failed.
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        retries = 3
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        self.logger.info(f"Starting upload: {file_path} ({file_size_mb:.2f}MB)")

        # Use single-part for smaller files unless explicitly forced to multi-part
        while retries > 0 and not force_multipart and file_size <= 20 * 1024 * 1024:
            try:
                result = await self._upload_single_part(file_path)
                if result:
                    self.logger.info(f"Single-part upload successful: {file_path}")
                    return result
            except httpx.ReadTimeout:
                retries -= 1
                self.logger.warning(
                    f"Timeout during single-part upload, retrying"
                )
            except Exception as e:
                self.logger.warning(
                    f"Single-part upload failed, trying multi-part: {e}"
                )

        # Fallback to multi-part or when explicitly requested
        return await self._upload_multipart(file_path, max_part_size)

    async def _upload_single_part(
        self, file_path: str
    ) -> Optional[NotionFileUploadResponse]:
        """
        Internal method for single-part file upload using Direct Upload method.

        Creates an upload object, uploads file content directly to the provided URL,
        and completes the upload process.

        Returns:
            Validated NotionFileUploadResponse or None if failed.
        """
        filename = os.path.basename(file_path)
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        # Step 1: Create file upload object
        upload_response = await self.notion_client.post("file_uploads", data={})
        if not upload_response:
            return None

        # Validate and parse the response
        try:
            upload = NotionFileUploadResponse.model_validate(upload_response)
        except Exception as e:
            self.logger.error(f"Failed to validate upload response: {e}")
            return None

        if not upload.upload_url:
            self.logger.error("No upload URL in response")
            return None

        # Step 2: Upload file content
        with open(file_path, "rb") as f:
            file_data = f.read()

        files = {"file": (filename, file_data, content_type)}
        upload_headers = {
            "Authorization": f"Bearer {self.notion_client.token}",
            "Notion-Version": self.notion_client.NOTION_VERSION,
        }

        async with httpx.AsyncClient() as upload_client:
            response = await upload_client.post(
                upload.upload_url, files=files, headers=upload_headers
            )
            response.raise_for_status()

        return upload

    async def _upload_multipart(
        self, file_path: str, max_part_size: int
    ) -> Optional[NotionFileUploadResponse]:
        """
        Internal method for multi-part file upload for large files.

        Creates upload object, sends file in chunks, and completes the upload.

        Returns:
            Validated NotionFileUploadResponse or None if failed.
        """
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        num_parts = math.ceil(file_size / max_part_size)

        self.logger.info(
            f"Multi-part upload: {file_path} ({file_size_mb:.2f}MB, {num_parts} parts)"
        )

        upload = await self._create_file_upload(file_path, max_part_size)
        if not upload:
            return None

        file_upload_id = upload.id
        expected_parts = (
            upload.number_of_parts.total if upload.number_of_parts else num_parts
        )

        with open(file_path, "rb") as f:
            for part_number in range(1, expected_parts + 1):
                part_data = f.read(max_part_size)

                success = await self._send_file_part(
                    file_upload_id, part_number, part_data
                )
                if not success:
                    self.logger.error(f"Failed at part {part_number}/{expected_parts}")
                    return None

        result = await self._complete_file_upload(file_upload_id)
        if not result:
            return None

        if result:
            self.logger.info(f"Multi-part upload completed: {file_path}")

        return result

    async def _create_file_upload(
        self, filename: str, max_part_size: int
    ) -> Optional[NotionFileUploadResponse]:
        """
        Creates a multi-part file upload object with the specified parameters.

        Args:
            filename: Path to the file.
            max_part_size: Maximum size per upload part.

        Returns:
            Validated NotionFileUploadResponse or None if creation failed.
        """
        file_size = os.path.getsize(filename)
        num_parts = math.ceil(file_size / max_part_size)
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        basename = os.path.basename(filename)

        data = {
            "mode": "multi_part",
            "filename": basename,
            "content_type": content_type,
            "number_of_parts": num_parts,
        }

        response = await self.notion_client.post("file_uploads", data=data)
        if not response:
            return None

        try:
            return NotionFileUploadResponse.model_validate(response)
        except Exception as e:
            self.logger.error(f"Failed to validate multi-part upload response: {e}")
            return None

    async def _send_file_part(
        self, file_upload_id: str, part_number: int, file_part_data: bytes
    ) -> bool:
        """
        Sends a single part of a multi-part file upload.

        Args:
            file_upload_id: The upload session ID.
            part_number: Part number (1-indexed).
            file_part_data: Binary data for this part.

        Returns:
            True if part was uploaded successfully, False otherwise.
        """
        retries = 3
        url = f"{self.notion_client.BASE_URL}/file_uploads/{file_upload_id}/send"

        while retries > 0:
            try:
                files = {"file": file_part_data}
                data = {"part_number": str(part_number)}
                # Explicit content type and boundary are needed because of bug in the httpx package
                # that strips the auto-generated boundary from the header erroneously, causing Notion to
                # refuse the upload.
                headers = {"Content-Type": "multipart/form-data; boundary=9fec9660cb6f09b74688cba7c1e14ee0"}
                response = await self.notion_client.client.post(url, data=data, files=files, headers=headers)
                response.raise_for_status()
                return True
            except httpx.ReadTimeout:
                retries -= 1
                self.logger.warning(
                    f"Timeout during multi-part upload, retrying"
                )
            except Exception:
                return False
        return False
    async def _complete_file_upload(
        self, file_upload_id: str
    ) -> Optional[NotionFileUploadResponse]:
        """
        Completes a multi-part file upload and finalizes the process.

        Args:
            file_upload_id: The upload session ID.

        Returns:
            Validated NotionFileUploadResponse or None if completion failed.
        """
        response = await self.notion_client.post(
            f"file_uploads/{file_upload_id}/complete"
        )
        if not response:
            return None

        try:
            return NotionFileUploadResponse.model_validate(response)
        except Exception as e:
            self.logger.error(f"Failed to validate completion response: {e}")
            return None
