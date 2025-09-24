from abc import ABC, abstractmethod

from notionary.shared.entities.entity_models import NotionEntityResponseDto


class EntityMetadataClient(ABC):
    @abstractmethod
    async def set_title(self, title: str) -> None: ...

    @abstractmethod
    async def patch_emoji_icon(self, emoji: str) -> NotionEntityResponseDto: ...

    @abstractmethod
    async def patch_external_icon(self, icon_url: str) -> NotionEntityResponseDto: ...

    @abstractmethod
    async def remove_icon(self) -> None: ...

    @abstractmethod
    async def patch_external_cover(self, cover_url: str) -> NotionEntityResponseDto: ...

    @abstractmethod
    async def remove_cover(self) -> None: ...

    @abstractmethod
    async def archive_page(self) -> NotionEntityResponseDto: ...

    @abstractmethod
    async def unarchive_page(self) -> NotionEntityResponseDto: ...
