import asyncio
from collections.abc import Callable

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.schemas import Block
from notionary.page.content.markdown.builder import MarkdownBuilder
from notionary.page.content.parser.service import MarkdownToNotionConverter
from notionary.page.content.renderer.service import NotionToMarkdownConverter
from notionary.utils.decorators import async_retry
from notionary.utils.mixins.logging import LoggingMixin


class PageContentService(LoggingMixin):
    def __init__(
        self,
        page_id: str,
        block_client: NotionBlockHttpClient,
        markdown_converter: MarkdownToNotionConverter,
        notion_to_markdown_converter: NotionToMarkdownConverter,
    ) -> None:
        self._page_id = page_id
        self._block_client = block_client
        self._markdown_converter = markdown_converter
        self._notion_to_markdown_converter = notion_to_markdown_converter

    async def get_as_markdown(self) -> str:
        blocks = await self._block_client.get_block_tree(parent_block_id=self._page_id)
        return await self._notion_to_markdown_converter.convert(blocks=blocks)

    async def clear(self) -> None:
        children_response = await self._block_client.get_block_children(block_id=self._page_id)

        if not children_response or not children_response.results:
            self.logger.debug("No blocks to delete for page: %s", self._page_id)
            return

        await asyncio.gather(*[self._delete_single_block(block) for block in children_response.results])

    @async_retry(max_retries=10, initial_delay=0.2, backoff_factor=1.5)
    async def _delete_single_block(self, block: Block) -> None:
        self.logger.debug("Deleting block: %s", block.id)
        await self._block_client.delete_block(block.id)

    async def append_markdown(self, content: str | Callable[[MarkdownBuilder], MarkdownBuilder]) -> None:
        markdown = self._extract_markdown(content)
        if not markdown:
            self.logger.debug("No markdown content to append for page: %s", self._page_id)
            return

        blocks = await self._markdown_converter.convert(markdown)
        await self._append_blocks(blocks)

    def _extract_markdown(self, content: str | Callable[[MarkdownBuilder], MarkdownBuilder]) -> str:
        if isinstance(content, str):
            return content

        if callable(content):
            builder = MarkdownBuilder()
            content(builder)
            return builder.build()

        raise ValueError("content must be either a string or a callable that takes a MarkdownBuilder")

    async def _append_blocks(self, blocks: list[Block]) -> None:
        await self._block_client.append_block_children(block_id=self._page_id, children=blocks)
