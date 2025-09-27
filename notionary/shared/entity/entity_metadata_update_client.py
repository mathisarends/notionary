from abc import ABC, abstractmethod

from notionary.shared.entity.entity_models import NotionEntityDto, NotionEntityUpdateDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon


class EntityMetadataUpdateClient(ABC):
    @abstractmethod
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> NotionEntityDto: ...

    async def patch_emoji_icon(self, emoji: str) -> NotionEntityDto:
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionEntityDto:
        icon = ExternalIcon.from_url(icon_url)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def remove_icon(self) -> None:
        update_dto = NotionEntityUpdateDto(icon=None)
        return await self.patch_metadata(update_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionEntityDto:
        cover = NotionCover.from_url(cover_url)
        update_dto = NotionEntityUpdateDto(cover=cover)
        return await self.patch_metadata(update_dto)

    async def remove_cover(self) -> None:
        update_dto = NotionEntityUpdateDto(cover=None)
        return await self.patch_metadata(update_dto)

    async def move_to_trash(self) -> NotionEntityDto:
        update_dto = NotionEntityUpdateDto(in_trash=True)
        return await self.patch_metadata(update_dto)

    async def restore_from_trash(self) -> NotionEntityDto:
        update_dto = NotionEntityUpdateDto(in_trash=False)
        return await self.patch_metadata(update_dto)
