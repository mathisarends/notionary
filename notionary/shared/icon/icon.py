from typing import cast

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
    ) -> None:
        self._client = update_client
        self.emoji: str | None = self._extract_emoji(dto)
        self.external_url: str | None = self._extract_external_url(dto)

    async def set_emoji(self, emoji: str) -> None:
        response = await self._client.patch_emoji_icon(emoji)
        self.emoji = self._extract_emoji(response)
        self.external_url = None

    async def set_from_url(self, url: str) -> None:
        response = await self._client.patch_external_icon(url)
        self.emoji = None
        self.external_url = self._extract_external_url(response)

    async def remove(self) -> None:
        await self._client.remove_icon()
        self.emoji = None
        self.external_url = None

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
