import asyncio
import logging

from notionary.page.blocks.client import BlockClient
from notionary.page.blocks.schemas import Block
from notionary.page.content import MarkdownToNotionConverter, NotionToMarkdownConverter
from notionary.shared.decorators import with_retry

logger = logging.getLogger(__name__)


class PageContent:
    def __init__(self, page_id: str) -> None:
        self._page_id = page_id
        self._client = BlockClient()
        self._to_notion = MarkdownToNotionConverter()
        self._to_markdown = NotionToMarkdownConverter()

    async def get_markdown(self) -> str:
        blocks = await self._client.get_block_tree(block_id=self._page_id)
        return await self._to_markdown.convert(blocks=blocks)

    async def append(self, content: str) -> None:
        if not content:
            logger.debug("No markdown content to append for page: %s", self._page_id)
            return
        blocks = await self._to_notion.convert(content)
        await self._client.append_block_children(
            block_id=self._page_id, children=blocks
        )

    async def clear(self) -> None:
        children = await self._client.get_block_children(block_id=self._page_id)
        if not children or not children.results:
            logger.debug("No blocks to delete for page: %s", self._page_id)
            return
        await asyncio.gather(*[self._delete_block(block) for block in children.results])

    @with_retry(max_retries=10, initial_delay=0.2, backoff_factor=1.5)
    async def _delete_block(self, block: Block) -> None:
        logger.debug("Deleting block: %s", block.id)
        await self._client.delete_block(block.id)
