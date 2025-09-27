from abc import ABC, abstractmethod

from notionary.shared.entity.entity_models import NotionEntityUpdateDto
from notionary.shared.models.cover_models import NotionCover
from notionary.shared.models.icon_models import EmojiIcon, ExternalIcon
from notionary.shared.page_or_data_source.page_or_data_source_models import NotionPageOrDataSourceDto


class EntityMetadataUpdateClient(ABC):
    @abstractmethod
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> NotionPageOrDataSourceDto: ...

    async def patch_emoji_icon(self, emoji: str) -> NotionPageOrDataSourceDto:
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def patch_external_icon(self, icon_url: str) -> NotionPageOrDataSourceDto:
        icon = ExternalIcon.from_url(icon_url)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def remove_icon(self) -> None:
        update_dto = NotionEntityUpdateDto(icon=None)
        return await self.patch_metadata(update_dto)

    async def patch_external_cover(self, cover_url: str) -> NotionPageOrDataSourceDto:
        cover = NotionCover.from_url(cover_url)
        update_dto = NotionEntityUpdateDto(cover=cover)
        return await self.patch_metadata(update_dto)

    async def remove_cover(self) -> None:
        update_dto = NotionEntityUpdateDto(cover=None)
        return await self.patch_metadata(update_dto)

    async def archive_page(self) -> NotionPageOrDataSourceDto:
        update_dto = NotionEntityUpdateDto(archived=True)
        return await self.patch_metadata(update_dto)

    async def unarchive_page(self) -> NotionPageOrDataSourceDto:
        update_dto = NotionEntityUpdateDto(archived=False)
        return await self.patch_metadata(update_dto)
