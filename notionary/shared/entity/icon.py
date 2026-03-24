from pathlib import Path
from typing import cast

from notionary.file_upload import NotionFileUpload
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.file import ExternalFile, NotionHostedFile
from notionary.shared.models.icon import EmojiIcon, IconType


class EntityIcon:
    def __init__(
        self,
        dto: EntityResponseDto,
        update_client: EntityMetadataUpdateClient,
        file_upload_service: NotionFileUpload,
    ) -> None:
        self._client = update_client
        self._upload = file_upload_service
        self.emoji: str | None = self._extract_emoji(dto)
        self.external_url: str | None = self._extract_external_url(dto)

    async def set_emoji(self, emoji: str) -> None:
        response = await self._client.patch_emoji_icon(emoji)
        self._emoji = self._extract_emoji(response)
        self._external_url = None

    async def set_from_url(self, url: str) -> None:
        response = await self._client.patch_external_icon(url)
        self._emoji = None
        self._external_url = self._extract_external_url(response)

    async def set_from_file(self, path: Path, filename: str | None = None) -> None:
        upload = await self._upload.upload_file(path, filename)
        await self.set_from_file_upload(upload.id)

    async def set_from_file_upload(self, file_upload_id: str) -> None:
        response = await self._client.patch_icon_from_file_upload(file_upload_id)
        self._emoji = None
        self._external_url = self._extract_external_url(response)

    async def remove(self) -> None:
        await self._client.remove_icon()
        self._emoji = None
        self._external_url = None

    @staticmethod
    def _extract_emoji(dto: EntityResponseDto) -> str | None:
        if dto.icon is None or dto.icon.type is not IconType.EMOJI:
            return None
        return cast(EmojiIcon, dto.icon).emoji

    @staticmethod
    def _extract_external_url(dto: EntityResponseDto) -> str | None:
        if dto.icon is None:
            return None
        if dto.icon.type == IconType.EXTERNAL:
            return cast(ExternalFile, dto.icon).external.url
        if dto.icon.type == IconType.FILE:
            return cast(NotionHostedFile, dto.icon).file.url
        return None
