from collections.abc import Callable

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.markdown.builder import MarkdownBuilder
from notionary.blocks.registry.service import BlockRegistry
from notionary.page.content.writer.markdown_to_notion_converter import MarkdownToNotionConverter
from notionary.page.markdown_whitespace_processor import MarkdownWhitespaceProcessor
from notionary.schemas.base import NotionContentSchema
from notionary.utils.mixins.logging import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry, block_client: NotionBlockHttpClient) -> None:
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = block_client

        self._markdown_to_notion_converter = MarkdownToNotionConverter(block_registry=block_registry)

    async def append_markdown(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> None:
        markdown = self._extract_markdown_from_param(content)

        if not markdown or not markdown.strip():
            self.logger.error("append_markdown called with empty markdown content.")
            raise ValueError("Cannot append empty markdown content.")

        processed_markdown = MarkdownWhitespaceProcessor.process_markdown_whitespace(markdown)

        blocks = await self._markdown_to_notion_converter.convert(processed_markdown)

        await self._block_client.append_block_children(block_id=self.page_id, children=blocks)

    def _extract_markdown_from_param(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, NotionContentSchema):
            builder = MarkdownBuilder()
            return content.to_notion_content(builder)

        if callable(content):
            builder = MarkdownBuilder()
            content(builder)
            return builder.build()

        raise ValueError(
            "content must be either a string, a NotionContentSchema, a MarkdownDocumentModel, or a callable that takes a MarkdownBuilder"
        )
