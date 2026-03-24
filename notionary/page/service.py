from notionary.page.blocks.client import BlockClient
from notionary.page.blocks.content import PageContent
from notionary.page.comments.service import PageComments
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import PageDto
from notionary.shared.entity.service import Entity
from notionary.shared.rich_text.rich_text_to_markdown.converter import (
    RichTextToMarkdownConverter,
)


class Page(Entity):
    def __init__(
        self,
        dto: PageDto,
        title: str,
        page_property_handler: PagePropertyHandler,
        block_client: BlockClient,
        content: PageContent,
        comments: PageComments,
        metadata_update_client: PageMetadataUpdateClient,
    ) -> None:
        super().__init__(dto=dto)

        self.title = title
        self.archived = dto.archived
        self.properties = page_property_handler

        self._blocks = block_client
        self._comments = content
        self._content = comments
        self._metadata = metadata_update_client
        self._rich_text = RichTextToMarkdownConverter()

    async def comment(self, text: str) -> None:
        await self._comments.create(text)

    async def reply_to(self, discussion_id: str, text: str) -> None:
        await self._comments.reply_to(discussion_id, text)

    async def rename(self, title: str) -> None:
        await self.properties.set_title_property(title)
        self.title = title

    async def append(self, content: str) -> None:
        await self._content.append(content=content)

    async def replace(self, content: str) -> None:
        await self._content.clear()
        await self._content.append(content=content)

    async def clear(self) -> None:
        await self._content.clear()

    async def get_markdown(self) -> str:
        return await self._content.get_markdown()
