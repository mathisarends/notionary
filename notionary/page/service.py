from notionary.page.blocks.service import PageContent
from notionary.page.comments.service import PageComments
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import PageDto
from notionary.shared.entity.cover import EntityCover
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.metadata import EntityMetadata
from notionary.shared.entity.trash import EntityTrash
from notionary.shared.icon.icon import EntityIcon


class Page:
    def __init__(
        self,
        dto: PageDto,
        title: str,
        page_property_handler: PagePropertyHandler,
        content: PageContent,
        comments: PageComments,
        metadata_update_client: EntityMetadataUpdateClient,
    ) -> None:
        self.metadata = EntityMetadata.from_dto(dto)

        self._icon = EntityIcon(dto, metadata_update_client)
        self._cover = EntityCover(dto, metadata_update_client)
        self._trash = EntityTrash(dto, metadata_update_client)

        self.title = title
        self.archived = dto.archived
        self.properties = page_property_handler

        self._content = content
        self._comments = comments

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def url(self) -> str:
        return self.metadata.url

    @property
    def in_trash(self) -> bool:
        return self._trash.in_trash

    async def trash(self) -> None:
        await self._trash.trash()

    async def restore(self) -> None:
        await self._trash.restore()

    async def set_icon_emoji(self, emoji: str) -> None:
        if self._icon:
            await self._icon.set_emoji(emoji)

    async def set_icon_url(self, url: str) -> None:
        if self._icon:
            await self._icon.set_from_url(url)

    async def remove_icon(self) -> None:
        if self._icon:
            await self._icon.remove()

    async def set_cover(self, url: str) -> None:
        if self._cover:
            await self._cover.set_from_url(url)

    async def random_cover(self) -> None:
        if self._cover:
            await self._cover.set_random_gradient()

    async def remove_cover(self) -> None:
        if self._cover:
            await self._cover.remove()

    async def append(self, content: str) -> None:
        await self._content.append(content=content)

    async def replace(self, content: str) -> None:
        await self._content.clear()
        await self._content.append(content=content)

    async def clear(self) -> None:
        await self._content.clear()

    async def get_markdown(self) -> str:
        return await self._content.get_markdown()

    async def comment(self, text: str) -> None:
        await self._comments.create(text)

    async def reply_to(self, discussion_id: str, text: str) -> None:
        await self._comments.reply_to(discussion_id, text)

    async def rename(self, title: str) -> None:
        await self.properties.set_title_property(title)
        self.title = title
