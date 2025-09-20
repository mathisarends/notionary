from typing import Callable, Union

from notionary.blocks.block_client import NotionBlockClient
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.schemas.base import NotionContentSchema
from notionary.page.markdown_whitespace_processor import MarkdownWhitespaceProcessor
from notionary.page.writer.markdown_to_notion_converter import MarkdownToNotionConverter
from notionary.util import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry):
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockClient()

        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )

    async def append_markdown(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
    ) -> None:
        markdown = self._extract_markdown_from_param(content)
        
        if not markdown or not markdown.strip():
            self.logger.error("append_markdown called with empty markdown content.")
            raise ValueError("Cannot append empty markdown content.")

        processed_markdown = MarkdownWhitespaceProcessor.process_markdown_whitespace(
            markdown
        )
        
        blocks = await self._markdown_to_notion_converter.convert(
            processed_markdown
        )

        await self._block_client.append_block_children(
            block_id=self.page_id, children=blocks
        )


    def _extract_markdown_from_param(
        self,
        content: Union[
            str, Callable[[MarkdownBuilder], MarkdownBuilder], NotionContentSchema
        ],
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
