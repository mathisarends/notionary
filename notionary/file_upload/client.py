from collections.abc import AsyncGenerator
from uuid import UUID

from notionary.file_upload.schemas import (
    FileUploadCompleteRequest,
    FileUploadCreateRequest,
    FileUploadQuery,
    FileUploadResponse,
    UploadMode,
)
from notionary.http import HttpClient


class FileUploadHttpClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def create_single_part_upload(
        self, filename: str, content_type: str | None = None
    ) -> FileUploadResponse:
        return await self._create_upload(
            filename, UploadMode.SINGLE_PART, content_type, None
        )

    async def create_multi_part_upload(
        self, filename: str, number_of_parts: int, content_type: str | None = None
    ) -> FileUploadResponse:
        return await self._create_upload(
            filename, UploadMode.MULTI_PART, content_type, number_of_parts
        )

    async def send_file_content(
        self,
        file_upload_id: UUID,
        file_content: bytes,
        filename: str,
        part_number: int | None = None,
    ) -> FileUploadResponse:
        data = {"part_number": str(part_number)} if part_number is not None else None
        response = await self._http.post_multipart(
            f"file_uploads/{file_upload_id}/send",
            files={"file": (filename, file_content)},
            data=data,
        )
        return FileUploadResponse.model_validate(response)

    async def complete_upload(self, file_upload_id: UUID) -> FileUploadResponse:
        response = await self._http.post(
            f"file_uploads/{file_upload_id}/complete",
            data=FileUploadCompleteRequest().model_dump(),
        )
        return FileUploadResponse.model_validate(response)

    async def get_file_upload(self, file_upload_id: UUID) -> FileUploadResponse:
        response = await self._http.get(f"file_uploads/{file_upload_id}")
        return FileUploadResponse.model_validate(response)

    async def list_file_uploads(
        self, query: FileUploadQuery | None = None
    ) -> list[FileUploadResponse]:
        q = query or FileUploadQuery()
        raw = await self._http.paginate(
            "file_uploads",
            total_results_limit=q.total_results_limit,
            method="GET",
            **q.model_dump(exclude_none=True),
        )
        return [FileUploadResponse.model_validate(r) for r in raw]

    async def list_file_uploads_stream(
        self, query: FileUploadQuery | None = None
    ) -> AsyncGenerator[FileUploadResponse]:
        q = query or FileUploadQuery()
        async for item in self._http.paginate_stream(
            "file_uploads",
            total_results_limit=q.total_results_limit,
            method="GET",
            **q.model_dump(exclude_none=True),
        ):
            yield FileUploadResponse.model_validate(item)

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
        response = await self._http.post(
            "file_uploads", data=request.model_dump(exclude_none=True)
        )
        return FileUploadResponse.model_validate(response)
