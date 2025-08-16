import json
from typing import Callable, Optional, Union

from mkdocs.structure.toc import TableOfContents

from notionary.blocks.block_client import NotionBlockClient
from notionary.blocks.block_models import Block
from notionary.blocks.divider.divider_models import DividerBlock
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.markdown.markdown_builder import MarkdownBuilder
from notionary.page.markdown_whitespace_processor import (
    MarkdownWhitespaceProcessor,
)
from notionary.page.writer.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)
from notionary.page.reader.page_content_retriever import PageContentRetriever

from notionary.util import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry):
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockClient()

        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )

        self._content_retriever = PageContentRetriever(
            page_id=page_id, block_registry=block_registry
        )

    async def append_markdown(
        self,
        content: Union[str, Callable[[MarkdownBuilder], MarkdownBuilder]],
        *,
        append_divider: bool = True,
        prepend_table_of_contents: bool = False,
    ) -> Optional[str]:
        """
        Append markdown content to a Notion page using either text or builder callback.

        Args:
            content: Either raw markdown text OR a callback function that receives a MarkdownBuilder
            append_divider: Whether to append a divider
            prepend_table_of_contents: Whether to prepend table of contents

        Returns:
            str: The processed markdown content that was appended (None if failed)
        """

        if isinstance(content, str):
            final_markdown = content
        elif callable(content):
            builder = MarkdownBuilder()
            content(builder)
            final_markdown = builder.build()
        else:
            raise ValueError(
                "content must be either a string or a callable that takes a MarkdownBuilder"
            )

        # Add optional components
        if prepend_table_of_contents:
            self._ensure_table_of_contents_exists_in_registry()
            final_markdown = "[toc]\n\n" + final_markdown

        if append_divider:
            self._ensure_divider_exists_in_registry()
            final_markdown = final_markdown + "\n\n---\n"

        processed_markdown = self._process_markdown_whitespace(final_markdown)

        try:
            blocks = self._markdown_to_notion_converter.convert(processed_markdown)

            children_dicts = [block.model_dump(exclude_none=True) for block in blocks]
            import json

            print("json", json.dumps(children_dicts, indent=2))

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

    async def clear_page_content(self) -> Optional[str]:
        """Clear all content of the page and return deleted content as markdown."""
        try:
            children_response = await self._block_client.get_block_children(
                block_id=self.page_id
            )

            if not children_response or not children_response.results:
                return None

            # Use PageContentRetriever for sophisticated markdown conversion
            deleted_content = self._content_retriever._convert_blocks_to_markdown(
                children_response.results, indent_level=0
            )

            # Delete blocks
            success = True
            for block in children_response.results:
                block_success = await self._delete_block_with_children(block)
                if not block_success:
                    success = False

            if not success:
                self.logger.warning("Some blocks could not be deleted")

            return deleted_content if deleted_content else None

        except Exception:
            self.logger.error("Error clearing page content", exc_info=True)
            return None

    async def _delete_block_with_children(self, block: Block) -> bool:
        """Delete a block and all its children recursively."""
        if not block.id:
            self.logger.error("Block has no valid ID")
            return False

        self.logger.debug("Deleting block: %s (type: %s)", block.id, block.type)

        try:
            if block.has_children and not await self._delete_block_children(block):
                return False

            return await self._delete_single_block(block)

        except Exception as e:
            self.logger.error("Failed to delete block %s: %s", block.id, str(e))
            return False

    async def _delete_block_children(self, block: Block) -> bool:
        """Delete all children of a block."""
        self.logger.debug("Block %s has children, deleting children first", block.id)

        try:
            children_blocks = await self._block_client.get_all_block_children(block.id)

            if not children_blocks:
                self.logger.debug("No children found for block: %s", block.id)
                return True

            self.logger.debug(
                "Found %d children to delete for block: %s",
                len(children_blocks),
                block.id,
            )

            # Delete all children recursively
            for child_block in children_blocks:
                if not await self._delete_block_with_children(child_block):
                    self.logger.error(
                        "Failed to delete child block: %s", child_block.id
                    )
                    return False

            self.logger.debug(
                "Successfully deleted all children of block: %s", block.id
            )
            return True

        except Exception as e:
            self.logger.error(
                "Failed to delete children of block %s: %s", block.id, str(e)
            )
            return False

    async def _delete_single_block(self, block: Block) -> bool:
        """Delete a single block."""
        deleted_block: Optional[Block] = await self._block_client.delete_block(block.id)

        if deleted_block is None:
            self.logger.error("Failed to delete block: %s", block.id)
            return False

        if deleted_block.archived or deleted_block.in_trash:
            self.logger.debug("Successfully deleted/archived block: %s", block.id)
            return True
        else:
            self.logger.warning("Block %s was not properly archived/deleted", block.id)
            return False

    def _process_markdown_whitespace(self, markdown_text: str) -> str:
        """Process markdown text to normalize whitespace while preserving code blocks."""
        lines = markdown_text.split("\n")
        if not lines:
            return ""

        processor = MarkdownWhitespaceProcessor()
        return processor.process_lines(lines)

    def _ensure_table_of_contents_exists_in_registry(self) -> None:
        """Ensure TableOfContents is registered in the block registry."""
        self.block_registry.register(TableOfContents)

    def _ensure_divider_exists_in_registry(self) -> None:
        """Ensure DividerBlock is registered in the block registry."""
        self.block_registry.register(DividerBlock)
