from typing import Optional, BinaryIO
from io import BytesIO
from pathlib import Path
import httpx

from notionary.base_notion_client import BaseNotionClient
from notionary.file_upload.models import (
    FileUploadResponse,
    FileUploadListResponse,
    FileUploadCreateRequest,
    FileUploadCompleteRequest,
)
from notionary.util import singleton


@singleton
class NotionFileUploadClient(BaseNotionClient):
    """
    Client for Notion file upload operations.
    Inherits base HTTP functionality from BaseNotionClient.
    """

    async def create_file_upload(
        self,
        filename: str,
        content_type: Optional[str] = None,
        content_length: Optional[int] = None,
        mode: str = "single_part",
    ) -> Optional[FileUploadResponse]:
        """
        Create a new file upload.

        Args:
            filename: Name of the file (max 900 bytes)
            content_type: MIME type of the file
            content_length: Size of the file in bytes
            mode: Upload mode ("single_part" or "multi_part")

        Returns:
            FileUploadResponse or None if failed
        """
        request_data = FileUploadCreateRequest(
            filename=filename,
            content_type=content_type,
            content_length=content_length,
            mode=mode,
        )

        response = await self.post("file_uploads", data=request_data.model_dump())
        if response is None:
            return None

        try:
            return FileUploadResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate file upload response: %s", e)
            return None

    async def send_file_upload(
        self,
        file_upload_id: str,
        file_content: BinaryIO,
        filename: Optional[str] = None,
        part_number: Optional[int] = None,
    ) -> bool:
        """
        Send file content to Notion.

        Args:
            file_upload_id: ID of the file upload
            file_content: Binary file content
            filename: Optional filename for the form data
            part_number: Part number for multi-part uploads

        Returns:
            True if successful, False otherwise
        """
        await self.ensure_initialized()

        if not self.client:
            self.logger.error("HTTP client not initialized")
            return False

        url = f"{self.BASE_URL}/file_uploads/{file_upload_id}/send"

        try:
            # Read all content from BinaryIO into bytes
            if hasattr(file_content, "read"):
                file_bytes = file_content.read()
                # Reset position if possible (for BytesIO objects)
                if hasattr(file_content, "seek"):
                    file_content.seek(0)
            else:
                file_bytes = file_content

            # Prepare files dict for multipart upload
            files = {"file": (filename or "file", file_bytes)}

            # Prepare form data (only for multi-part uploads)
            data = {}
            if part_number is not None:
                data["part_number"] = str(part_number)

            # Create a new client instance specifically for this upload
            # This avoids issues with the base client's default JSON headers
            upload_headers = {
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.NOTION_VERSION,
                # Explicitly do NOT set Content-Type - let httpx handle multipart
            }

            self.logger.debug(
                "Sending file upload to %s with filename %s", url, filename
            )

            # Use a temporary client for the multipart upload
            async with httpx.AsyncClient(timeout=self.timeout) as upload_client:
                response = await upload_client.post(
                    url,
                    files=files,
                    data=data if data else None,
                    headers=upload_headers,
                )

                response.raise_for_status()
                self.logger.debug("File upload sent successfully: %s", file_upload_id)
                return True

        except httpx.HTTPStatusError as e:
            try:
                error_text = e.response.text
            except:
                error_text = "Unable to read error response"
            error_msg = f"HTTP {e.response.status_code}: {error_text}"
            self.logger.error("Send file upload failed (%s): %s", url, error_msg)
            return False

        except httpx.RequestError as e:
            self.logger.error("Request error sending file upload (%s): %s", url, str(e))
            return False

        except Exception as e:
            self.logger.error("Unexpected error in send_file_upload: %s", str(e))
            import traceback

            self.logger.debug("Full traceback: %s", traceback.format_exc())
            return False

    async def complete_file_upload(
        self, file_upload_id: str
    ) -> Optional[FileUploadResponse]:
        """
        Complete a multi-part file upload.

        Args:
            file_upload_id: ID of the file upload

        Returns:
            FileUploadResponse or None if failed
        """
        request_data = FileUploadCompleteRequest()

        response = await self.post(
            f"file_uploads/{file_upload_id}/complete", data=request_data.model_dump()
        )
        if response is None:
            return None

        try:
            return FileUploadResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate complete file upload response: %s", e)
            return None

    async def retrieve_file_upload(
        self, file_upload_id: str
    ) -> Optional[FileUploadResponse]:
        """
        Retrieve details of a file upload.

        Args:
            file_upload_id: ID of the file upload

        Returns:
            FileUploadResponse or None if failed
        """
        response = await self.get(f"file_uploads/{file_upload_id}")
        if response is None:
            return None

        try:
            return FileUploadResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate retrieve file upload response: %s", e)
            return None

    async def list_file_uploads(
        self, page_size: int = 100, start_cursor: Optional[str] = None
    ) -> Optional[FileUploadListResponse]:
        """
        List file uploads for the current bot integration.

        Args:
            page_size: Number of uploads per page (max 100)
            start_cursor: Cursor for pagination

        Returns:
            FileUploadListResponse or None if failed
        """
        params = {"page_size": min(page_size, 100)}
        if start_cursor:
            params["start_cursor"] = start_cursor

        response = await self.get("file_uploads", params=params)
        if response is None:
            return None

        try:
            return FileUploadListResponse.model_validate(response)
        except Exception as e:
            self.logger.error("Failed to validate list file uploads response: %s", e)
            return None

    async def send_file_from_path(
        self, file_upload_id: str, file_path: Path, part_number: Optional[int] = None
    ) -> bool:
        """
        Convenience method to send file from file path.

        Args:
            file_upload_id: ID of the file upload
            file_path: Path to the file
            part_number: Part number for multi-part uploads

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file content into memory first
            with open(file_path, "rb") as f:
                file_content = f.read()

            # Use BytesIO for the upload
            return await self.send_file_upload(
                file_upload_id=file_upload_id,
                file_content=BytesIO(file_content),
                filename=file_path.name,
                part_number=part_number,
            )
        except Exception as e:
            self.logger.error("Failed to send file from path %s: %s", file_path, e)
            return False
