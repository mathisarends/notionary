from collections.abc import AsyncGenerator

import httpx

from notionary.file_upload.schemas import (
    FileUploadCompleteRequest,
    FileUploadCreateRequest,
    FileUploadFilter,
    FileUploadListResponse,
    FileUploadResponse,
    UploadMode,
)
from notionary.http.client import NotionHttpClient
from notionary.utils.pagination import PaginatedResponse, paginate_notion_api, paginate_notion_api_generator


class FileUploadHttpClient(NotionHttpClient):
    async def create_single_part_upload(
        self,
        filename: str,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        return await self._create_upload(
            filename=filename,
            content_type=content_type,
            mode=UploadMode.SINGLE_PART,
            number_of_parts=None,
        )

    async def create_multi_part_upload(
        self,
        filename: str,
        number_of_parts: int,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        return await self._create_upload(
            filename=filename,
            content_type=content_type,
            mode=UploadMode.MULTI_PART,
            number_of_parts=number_of_parts,
        )

    async def send_file_content(
        self,
        file_upload_id: str,
        file_content: bytes,
        filename: str,
        part_number: int | None = None,
    ) -> FileUploadResponse:
        await self._ensure_initialized()

        url = self._build_send_url(file_upload_id)
        files = {"file": (filename, file_content)}
        data = self._build_part_number_data(part_number)

        response = await self._send_multipart_request(url, files=files, data=data)
        return FileUploadResponse.model_validate(response.json())

    async def complete_upload(self, file_upload_id: str) -> FileUploadResponse:
        request = FileUploadCompleteRequest()
        response = await self.post(
            f"file_uploads/{file_upload_id}/complete",
            data=request.model_dump(),
        )
        return FileUploadResponse.model_validate(response)

    async def get_file_upload(self, file_upload_id: str) -> FileUploadResponse:
        response = await self.get(f"file_uploads/{file_upload_id}")
        return FileUploadResponse.model_validate(response)

    async def list_file_uploads(
        self,
        filter: FileUploadFilter | None = None,
        total_results_limit: int | None = None,
    ) -> list[FileUploadResponse]:
        return await paginate_notion_api(
            lambda **kwargs: self._fetch_file_uploads_page(filter=filter, **kwargs),
            total_results_limit=total_results_limit,
        )

    async def list_file_uploads_stream(
        self,
        filter: FileUploadFilter | None = None,
        total_results_limit: int | None = None,
    ) -> AsyncGenerator[FileUploadResponse]:
        async for upload in paginate_notion_api_generator(
            lambda **kwargs: self._fetch_file_uploads_page(filter=filter, **kwargs),
            total_results_limit=total_results_limit,
        ):
            yield upload

    async def _create_upload(
        self,
        filename: str,
        mode: UploadMode,
        content_type: str | None,
        number_of_parts: int | None,
    ) -> FileUploadResponse:
        request = FileUploadCreateRequest(
            filename=filename,
            content_type=content_type,
            mode=mode,
            number_of_parts=number_of_parts,
        )
        response = await self.post("file_uploads", data=request.model_dump())
        return FileUploadResponse.model_validate(response)

    async def _send_multipart_request(
        self,
        url: str,
        files: dict,
        data: dict | None = None,
    ) -> httpx.Response:
        headers = self._build_multipart_headers()

        async with httpx.AsyncClient(headers=headers, timeout=self.timeout) as client:
            response = await client.post(url, files=files, data=data)

        response.raise_for_status()
        return response

    async def _fetch_file_uploads_page(
        self,
        filter: FileUploadFilter | None = None,
        page_size: int = 100,
        start_cursor: str | None = None,
        **kwargs,
    ) -> PaginatedResponse:
        params = {"page_size": min(page_size, 100)}

        if start_cursor:
            params["start_cursor"] = start_cursor

        if filter:
            params.update(filter.model_dump(exclude_none=True))

        response = await self.get("file_uploads", params=params)
        parsed = FileUploadListResponse.model_validate(response)

        return PaginatedResponse(
            results=parsed.results,
            has_more=parsed.has_more,
            next_cursor=parsed.next_cursor,
        )

    def _build_send_url(self, file_upload_id: str) -> str:
        return f"{self.BASE_URL}/file_uploads/{file_upload_id}/send"

    def _build_part_number_data(self, part_number: int | None) -> dict | None:
        if part_number is not None:
            return {"part_number": str(part_number)}
        return None

    def _build_multipart_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.NOTION_VERSION,
        }
