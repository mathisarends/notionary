"""
Post-processor for handling Notion API text length limitations.

Handles text length validation and truncation for blocks that exceed
Notion's rich_text character limit of 2000 characters per element.
"""

import logging
from notionary.blocks.models import BlockCreateRequest

logger = logging.getLogger(__name__)


class MarkdownToNotionTextLengthPostProcessor:
    """Handles text length validation and truncation for Notion blocks."""

    def __init__(self, max_text_length: int = 1900):
        self.max_text_length = max_text_length

    def process(self, blocks: list[BlockCreateRequest]) -> list[BlockCreateRequest]:
        """Process blocks to fix text length limits."""
        if not blocks:
            return blocks

        return self._fix_blocks_content_length(blocks)

    def _fix_blocks_content_length(
        self, blocks: list[BlockCreateRequest]
    ) -> list[BlockCreateRequest]:
        """Check each block and ensure text content doesn't exceed Notion's limit."""
        fixed_blocks: list[BlockCreateRequest] = []

        flattened_blocks = self._flatten_blocks(blocks)

        for block in flattened_blocks:
            fixed_block = self._fix_single_block_content(block)
            fixed_blocks.append(fixed_block)
        return fixed_blocks

    def _fix_single_block_content(
        self, block: BlockCreateRequest
    ) -> BlockCreateRequest:
        """Fix content length in a single block and its children recursively."""
        block_copy = block.model_copy(deep=True)
        self._fix_block_rich_text_direct(block_copy)
        return block_copy

    def _fix_block_rich_text_direct(self, block: BlockCreateRequest) -> None:
        """Fix rich text content directly on the Pydantic object."""
        block_content = self._get_block_content(block)
        if not block_content:
            return
        if hasattr(block_content, "rich_text") and block_content.rich_text:
            self._fix_rich_text_objects_direct(block_content.rich_text)
        if hasattr(block_content, "children") and block_content.children:
            for child in block_content.children:
                self._fix_block_rich_text_direct(child)

    def _get_block_content(self, block: BlockCreateRequest):
        """Get the actual content object from a create block dynamically."""
        # Get all attributes that don't start with underscore and aren't methods
        for attr_name in dir(block):
            if attr_name.startswith("_") or attr_name in [
                "model_copy",
                "model_dump",
                "model_validate",
            ]:
                continue

            attr_value = getattr(block, attr_name, None)

            # Skip None values, strings (like 'type'), and callable methods
            if (
                attr_value is None
                or isinstance(attr_value, str)
                or callable(attr_value)
            ):
                continue

            # If it's an object with rich_text or children, it's likely our content
            if hasattr(attr_value, "rich_text") or hasattr(attr_value, "children"):
                return attr_value

        return None

    def _fix_rich_text_objects_direct(self, rich_text_list: list) -> None:
        """Fix rich text objects directly without dict conversion."""
        if not rich_text_list:
            return

        for rich_text_item in rich_text_list:
            if not rich_text_item:
                continue

            # Check if this is a text type rich text object
            if (
                hasattr(rich_text_item, "text")
                and rich_text_item.text
                and hasattr(rich_text_item.text, "content")
            ):

                content = rich_text_item.text.content
                if content and len(content) > self.max_text_length:
                    logger.warning(
                        "Truncating text content from %d to %d chars",
                        len(content),
                        self.max_text_length,
                    )
                    # Direct assignment - no parsing needed!
                    rich_text_item.text.content = content[: self.max_text_length]

    def _flatten_blocks(self, blocks: list) -> list[BlockCreateRequest]:
        """Flatten nested block lists."""
        flattened = []
        for item in blocks:
            if isinstance(item, list):
                # Rekursiv flatten für nested lists
                flattened.extend(self._flatten_blocks(item))
            else:
                # Normal block
                flattened.append(item)
        return flattened
