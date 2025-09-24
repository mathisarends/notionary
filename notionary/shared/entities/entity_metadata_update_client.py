from abc import ABC, abstractmethod

from notionary.shared.entities.entity_models import NotionEntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon


class EntityMetadataUpdateClient(ABC):
    @abstractmethod
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> NotionEntityResponseDto: ...

    async def patch_emoji_icon(self, emoji: str) -> NotionEntityResponseDto:
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionEntityResponseDto:
        icon = ExternalIcon.from_url(icon_url)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def remove_icon(self) -> None:
        update_dto = NotionEntityUpdateDto(icon=None)
        return await self.patch_metadata(update_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionEntityResponseDto:
        cover = NotionCover.from_url(cover_url)
        update_dto = NotionEntityUpdateDto(cover=cover)
        return await self.patch_metadata(update_dto)

    async def remove_cover(self) -> None:
        update_dto = NotionEntityUpdateDto(cover=None)
        return await self.patch_metadata(update_dto)

    async def archive_page(self) -> NotionEntityResponseDto:
        update_dto = NotionEntityUpdateDto(archived=True)
        return await self.patch_metadata(update_dto)

    async def unarchive_page(self) -> NotionEntityResponseDto:
        update_dto = NotionEntityUpdateDto(archived=False)
        return await self.patch_metadata(update_dto)
