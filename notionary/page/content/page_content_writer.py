from typing import Optional

from notionary.blocks import BlockRegistry
from notionary.blocks.shared.block_client import NotionBlockClient
from notionary.models.notion_block_response import Block
from notionary.page.content.markdown_whitespace_processor import (
    MarkdownWhitespaceProcessor,
)
from notionary.page.content.notion_text_length_utils import fix_blocks_content_length
from notionary.page.formatting.markdown_to_notion_converter import (
    MarkdownToNotionConverter,
)

from notionary.util import LoggingMixin


class PageContentWriter(LoggingMixin):
    def __init__(self, page_id: str, block_registry: BlockRegistry):
        self.page_id = page_id
        self.block_registry = block_registry
        self._block_client = NotionBlockClient()

        self._markdown_to_notion_converter = MarkdownToNotionConverter(
            block_registry=block_registry
        )

    async def append_markdown(self, markdown_text: str, append_divider=True) -> bool:
        """Append markdown text to a Notion page, automatically handling content length limits."""
        if append_divider:
            markdown_text = markdown_text + "---\n"

        markdown_text = self._process_markdown_whitespace(markdown_text)

        try:
            blocks = self._markdown_to_notion_converter.convert(markdown_text)

            fixed_blocks = fix_blocks_content_length(blocks)

            result = await self._block_client.append_block_children(
                block_id=self.page_id, children=fixed_blocks
            )
            self.logger.debug("Append block children result: %r", result)
            return bool(result)
        except Exception as e:
            self.logger.error("Error appending markdown: %s", str(e), exc_info=True)
            return False

    async def clear_page_content(self) -> bool:
        """Clear all content of the page."""
        try:
            children_response = await self._block_client.get_block_children(
                block_id=self.page_id
            )

            if not children_response or not children_response.results:
                return True

            success = True
            for block in children_response.results:
                block_success = await self._delete_block_with_children(block)
                if not block_success:
                    success = False

            return success
        except Exception as e:
            self.logger.error("Error clearing page content: %s", str(e))
            return False

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
