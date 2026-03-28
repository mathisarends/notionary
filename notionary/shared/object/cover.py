import random
from collections.abc import Sequence
from pathlib import Path

from notionary.file_upload import Files
from notionary.http.client import HttpClient
from notionary.shared.object.dtos import NotionObjectResponseDto, NotionObjectUpdateDto
from notionary.shared.object.schemas import (
    ExternalFile,
    File,
    FileUploadedFileData,
    FileUploadFile,
)


class Cover:
    _GRADIENT_COVERS: Sequence[str] = [
        f"https://www.notion.so/images/page-cover/gradients_{i}.png"
        for i in range(1, 10)
    ]

    def __init__(
        self,
        cover: File | None,
        http_client: HttpClient,
        path: str,
        file_uploads: Files,
    ) -> None:
        self._http = http_client
        self._path = path
        self.url: str | None = self._extract_url(cover)
        self._file_uploads = file_uploads

    async def set_from_file(
        self,
        file_path: Path | str,
    ) -> None:
        upload = await self._file_uploads.upload(Path(file_path), wait=True)
        cover = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(cover=cover))
        self.url = None

    async def set_from_bytes(
        self,
        content: bytes,
        filename: str,
    ) -> None:
        upload = await self._file_uploads.upload_from_bytes(
            content, filename, wait=True
        )
        cover = FileUploadFile(file_upload=FileUploadedFileData(id=upload.id))
        await self._patch(NotionObjectUpdateDto(cover=cover))
        self.url = None

    async def set_from_url(self, image_url: str) -> None:
        response = await self._patch(
            NotionObjectUpdateDto(cover=ExternalFile.from_url(image_url))
        )
        self.url = self._extract_url(response.cover)

    async def set_random_gradient(self) -> None:
        await self.set_from_url(random.choice(self._GRADIENT_COVERS))

    async def remove(self) -> None:
        await self._patch(NotionObjectUpdateDto(cover=None))
        self.url = None

    async def _patch(self, dto: NotionObjectUpdateDto) -> NotionObjectResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return NotionObjectResponseDto.model_validate(response)

    @staticmethod
    def _extract_url(cover: File | None) -> str | None:
        if cover is None:
            return None
        return cover.get_url()
