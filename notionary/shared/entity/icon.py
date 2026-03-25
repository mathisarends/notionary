from typing import cast

from notionary.http.client import HttpClient
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.file import ExternalFile, NotionHostedFile
from notionary.shared.models.icon import EmojiIcon, IconType


class EntityIcon:
    def __init__(
        self,
        dto: EntityResponseDto,
        http_client: HttpClient,
        path: str,
    ) -> None:
        self._http = http_client
        self._path = path
        self.emoji: str | None = self._extract_emoji(dto)
        self.external_url: str | None = self._extract_external_url(dto)

    async def set_emoji(self, emoji: str) -> None:
        response = await self._patch(NotionEntityUpdateDto(icon=EmojiIcon(emoji=emoji)))
        self.emoji = self._extract_emoji(response)
        self.external_url = None

    async def set_from_url(self, url: str) -> None:
        response = await self._patch(
            NotionEntityUpdateDto(icon=ExternalFile.from_url(url))
        )
        self.emoji = None
        self.external_url = self._extract_external_url(response)

    async def remove(self) -> None:
        await self._patch(NotionEntityUpdateDto(icon=None))
        self.emoji = None
        self.external_url = None

    async def _patch(self, dto: NotionEntityUpdateDto) -> EntityResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return EntityResponseDto.model_validate(response)

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
