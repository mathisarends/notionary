from typing import cast

from notionary.http.client import HttpClient
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.file import ExternalFile, NotionHostedFile
from notionary.shared.models.icon import EmojiIcon, Icon, IconType


class EntityIcon:
    def __init__(
        self,
        icon: Icon | None,
        http_client: HttpClient,
        path: str,
    ) -> None:
        self._http = http_client
        self._path = path
        self.emoji: str | None = self._extract_emoji(icon)
        self.external_url: str | None = self._extract_external_url(icon)

    async def set_emoji(self, emoji: str) -> None:
        response = await self._patch(NotionEntityUpdateDto(icon=EmojiIcon(emoji=emoji)))
        self.emoji = self._extract_emoji(response.icon)
        self.external_url = None

    async def set_from_url(self, url: str) -> None:
        response = await self._patch(
            NotionEntityUpdateDto(icon=ExternalFile.from_url(url))
        )
        self.emoji = None
        self.external_url = self._extract_external_url(response.icon)

    async def remove(self) -> None:
        await self._patch(NotionEntityUpdateDto(icon=None))
        self.emoji = None
        self.external_url = None

    async def _patch(self, dto: NotionEntityUpdateDto) -> EntityResponseDto:
        data = dto.model_dump(exclude_unset=True, exclude_none=True)
        response = await self._http.patch(self._path, data=data)
        return EntityResponseDto.model_validate(response)

    @staticmethod
    def _extract_emoji(icon: Icon | None) -> str | None:
        if icon is None or icon.type is not IconType.EMOJI:
            return None
        return cast(EmojiIcon, icon).emoji

    @staticmethod
    def _extract_external_url(icon: Icon | None) -> str | None:
        if icon is None:
            return None
        if icon.type == IconType.EXTERNAL:
            return cast(ExternalFile, icon).external.url
        if icon.type == IconType.FILE:
            return cast(NotionHostedFile, icon).file.url
        return None
