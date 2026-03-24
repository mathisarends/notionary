import random
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from notionary.file_upload import NotionFileUpload

from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.file import ExternalFile, FileType, NotionHostedFile


class EntityCover:
    _GRADIENT_COVERS: Sequence[str] = [
        f"https://www.notion.so/images/page-cover/gradients_{i}.png"
        for i in range(1, 10)
    ]

    def __init__(
        self,
        dto: EntityResponseDto,
        update_client: EntityMetadataUpdateClient,
        file_upload_service: NotionFileUpload,
    ) -> None:
        self._client = update_client
        self._upload = file_upload_service
        self._url: str | None = self._extract_url(dto)

    @property
    def url(self) -> str | None:
        return self._url

    async def set_from_url(self, image_url: str) -> None:
        response = await self._client.patch_external_cover(image_url)
        self._url = self._extract_url(response)

    async def set_random_gradient(self) -> None:
        await self.set_from_url(random.choice(self._GRADIENT_COVERS))

    async def set_from_file(self, path: Path, filename: str | None = None) -> None:
        upload = await self._upload.upload_file(path, filename)
        await self.set_from_file_upload(upload.id)

    async def set_from_file_upload(self, file_upload_id: str) -> None:
        response = await self._client.patch_cover_from_file_upload(file_upload_id)
        self._url = self._extract_url(response)

    async def remove(self) -> None:
        await self._client.remove_cover()
        self._url = None

    @staticmethod
    def _extract_url(dto: EntityResponseDto) -> str | None:
        if dto.cover is None:
            return None
        if dto.cover.type == FileType.EXTERNAL:
            return cast(ExternalFile, dto.cover).external.url
        if dto.cover.type == FileType.FILE:
            return cast(NotionHostedFile, dto.cover).file.url
        return None
