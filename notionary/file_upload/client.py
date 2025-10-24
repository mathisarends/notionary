from pathlib import Path

import aiofiles

from notionary.file_upload.schemas import (
    FileUploadCompleteRequest,
    FileUploadCreateRequest,
    FileUploadFilter,
    FileUploadListResponse,
    FileUploadResponse,
    UploadMode,
)
from notionary.http.client import NotionHttpClient
from notionary.utils.pagination import PaginatedResponse, paginate_notion_api_generator


class FileUploadHttpClient(NotionHttpClient):
    async def create_single_part_upload(
        self,
        filename: str,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        request = FileUploadCreateRequest(
            filename=filename,
            content_type=content_type,
        )
        response = await self.post("file_uploads", data=request.model_dump())
        return FileUploadResponse.model_validate(response)

    async def create_multi_part_upload(
        self,
        filename: str,
        number_of_parts: int,
        content_type: str | None = None,
    ) -> FileUploadResponse:
        request = FileUploadCreateRequest(
            filename=filename,
            content_type=content_type,
            mode=UploadMode.MULTI_PART,
            number_of_parts=number_of_parts,
        )
        response = await self.post("file_uploads", data=request.model_dump())
        return FileUploadResponse.model_validate(response)

    async def send_file_content(
        self,
        file_upload_id: str,
        file_content: bytes,
        filename: str,
        part_number: int | None = None,
    ) -> FileUploadResponse:
        await self._ensure_initialized()

        url = f"{self.BASE_URL}/file_uploads/{file_upload_id}/send"
        files = {"file": (filename, file_content)}
        data = {"part_number": str(part_number)} if part_number is not None else None

        response = await self.client.post(url, files=files, data=data)
        response.raise_for_status()

        return FileUploadResponse.model_validate(response.json())

    async def complete_upload(self, file_upload_id: str) -> FileUploadResponse:
        request = FileUploadCompleteRequest()
        response = await self.post(f"file_uploads/{file_upload_id}/complete", data=request.model_dump())
        return FileUploadResponse.model_validate(response)

    async def get_file_upload(self, file_upload_id: str) -> FileUploadResponse:
        response = await self.get(f"file_uploads/{file_upload_id}")
        return FileUploadResponse.model_validate(response)

    async def list_file_uploads(
        self,
        page_size: int = 100,
        start_cursor: str | None = None,
        filter: FileUploadFilter | None = None,
        total_results_limit: int | None = None,
    ) -> FileUploadListResponse:
        all_results = await paginate_notion_api_generator(
            lambda **kwargs: self._fetch_file_uploads_page(filter=filter, **kwargs),
            total_results_limit=total_results_limit,
            page_size=page_size,
            start_cursor=start_cursor,
        )

        file_uploads = [item async for item in all_results]

        return FileUploadListResponse(
            object="list",
            results=file_uploads,
            next_cursor=None,
            has_more=False,
            type="file_upload",
            request_id="",
        )

    async def send_file_from_path(
        self,
        file_upload_id: str,
        file_path: Path,
        part_number: int | None = None,
    ) -> FileUploadResponse:
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()

        return await self.send_file_content(
            file_upload_id=file_upload_id,
            file_content=file_content,
            filename=file_path.name,
            part_number=part_number,
        )

    async def _fetch_file_uploads_page(
        self,
        page_size: int = 100,
        start_cursor: str | None = None,
        filter: FileUploadFilter | None = None,
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
