from typing import Callable, Optional, Union

from notionary.blocks.client import NotionBlockClient
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.blocks.markdown.markdown_document_model import MarkdownDocumentModel
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
        content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder], MarkdownDocumentModel],
    ) -> Optional[str]:
        """
        Append markdown content to a Notion page using text, builder callback, or MarkdownDocumentModel.
        """
        markdown = self._extract_markdown_from_param(content)

        processed_markdown = MarkdownWhitespaceProcessor.process_markdown_whitespace(
            markdown
        )

        try:
            blocks = await self._markdown_to_notion_converter.convert(
                processed_markdown
            )

            result = await self._block_client.append_block_children(
                block_id=self.page_id, children=blocks
            )

            if result:
                self.logger.debug("Successfully appended %d blocks", len(blocks))
                return processed_markdown
            else:
                self.logger.error("Failed to append blocks")
                return None

        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e), exc_info=True)
            return None

    def _extract_markdown_from_param(
        self, content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder], MarkdownDocumentModel]
    ) -> str:
        """
        Prepare markdown content from string, builder callback, or MarkdownDocumentModel.
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, MarkdownDocumentModel):
            builder = MarkdownBuilder.from_model(content)
            return builder.build()
        elif callable(content):
            builder = MarkdownBuilder()
            content(builder)
            return builder.build()
        else:
            raise ValueError(
                "content must be either a string, a MarkdownDocumentModel, or a callable that takes a MarkdownBuilder"
            )
