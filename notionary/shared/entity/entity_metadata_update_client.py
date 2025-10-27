from abc import ABC, abstractmethod

from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto
from notionary.shared.models.file import ExternalFile, FileUploadFile
from notionary.shared.models.icon import EmojiIcon, Icon


class EntityMetadataUpdateClient(ABC):
    @abstractmethod
    async def patch_metadata(
        self, updated_data: NotionEntityUpdateDto
    ) -> EntityResponseDto: ...

    async def patch_emoji_icon(self, emoji: str) -> EntityResponseDto:
        icon = EmojiIcon(emoji=emoji)
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def patch_external_icon(self, icon_url: str) -> EntityResponseDto:
        icon = ExternalFile.from_url(icon_url)
        return await self._patch_icon(icon)

    async def patch_icon_from_file_upload(
        self, file_upload_id: str
    ) -> EntityResponseDto:
        icon = FileUploadFile.from_id(id=file_upload_id)
        return await self._patch_icon(icon)

    async def _patch_icon(self, icon: Icon) -> EntityResponseDto:
        update_dto = NotionEntityUpdateDto(icon=icon)
        return await self.patch_metadata(update_dto)

    async def remove_icon(self) -> None:
        update_dto = NotionEntityUpdateDto(icon=None)
        return await self.patch_metadata(update_dto)

    async def patch_external_cover(self, cover_url: str) -> EntityResponseDto:
        cover = ExternalFile.from_url(cover_url)
        return await self._patch_cover(cover)

    async def patch_cover_from_file_upload(
        self, file_upload_id: str
    ) -> EntityResponseDto:
        cover = FileUploadFile.from_id(id=file_upload_id)
        return await self._patch_cover(cover)

    async def _patch_cover(self, cover: Icon) -> EntityResponseDto:
        update_dto = NotionEntityUpdateDto(cover=cover)
        return await self.patch_metadata(update_dto)

    async def remove_cover(self) -> None:
        update_dto = NotionEntityUpdateDto(cover=None)
        return await self.patch_metadata(update_dto)

    async def move_to_trash(self) -> EntityResponseDto:
        update_dto = NotionEntityUpdateDto(in_trash=True)
        return await self.patch_metadata(update_dto)

    async def restore_from_trash(self) -> EntityResponseDto:
        update_dto = NotionEntityUpdateDto(in_trash=False)
        return await self.patch_metadata(update_dto)
