"""
Post-processor for handling Notion API text length limitations.

Handles text length validation and truncation for blocks that exceed
Notion's rich_text character limit of 2000 characters per element.
"""

from typing import TypeGuard

from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import HasChildren, HasRichText
from notionary.util import LoggingMixin


class NotionTextLengthProcessor(LoggingMixin):
    """
    Processes Notion blocks to ensure text content doesn't exceed API limits.

    The Notion API has a limit of 2000 characters per rich_text element.
    This processor truncates content that exceeds the specified limit.
    """

    DEFAULT_MAX_LENGTH = 1900  # Leave some buffer under the 2000 limit
    NOTION_MAX_LENGTH = 2000

    def __init__(self, max_text_length: int = DEFAULT_MAX_LENGTH) -> None:
        """
        Initialize the processor.

        Args:
            max_text_length: Maximum allowed text length (default: 1900)
        """
        if max_text_length <= 0:
            raise ValueError("max_text_length must be positive")
        if max_text_length > self.NOTION_MAX_LENGTH:
            self.logger.warning(
                "max_text_length (%d) exceeds Notion's limit of 2000 characters",
                max_text_length,
            )

        self.max_text_length = max_text_length

    def process(self, blocks: list[BlockCreateRequest]) -> list[BlockCreateRequest]:
        """
        Process blocks to fix text length limits.
        """
        if not blocks:
            return blocks

        flattened_blocks = self._flatten_block_list(blocks)
        return [self._process_single_block(block) for block in flattened_blocks]

    def _process_single_block(self, block: BlockCreateRequest) -> BlockCreateRequest:
        """
        Process a single block to fix text length issues.
        """
        block_copy = block.model_copy(deep=True)

        block_content = self._extract_block_content(block_copy)

        if block_content is not None:
            self._fix_content_text_lengths(block_content)

        return block_copy

    def _extract_block_content(self, block: BlockCreateRequest) -> object | None:
        """
        Extract the content object from a block using type-safe attribute access.
        """
        # Get the block's content using the block type as attribute name
        # We assume block.type always exists as per the BlockCreateRequest structure
        content = getattr(block, block.type, None)

        # Verify it's a valid content object (has rich_text or children)
        if content and (self._is_rich_text_container(content) or self._is_children_container(content)):
            return content

        return None

    def _fix_content_text_lengths(self, content: object) -> None:
        """
        Fix text lengths in a content object and its children recursively.
        """
        # Process rich_text if present
        if self._is_rich_text_container(content):
            self._truncate_rich_text_content(content.rich_text)

        # Process children recursively if present
        if self._is_children_container(content):
            for child in content.children:
                child_content = self._extract_block_content(child)
                if child_content:
                    self._fix_content_text_lengths(child_content)

    def _truncate_rich_text_content(self, rich_text_list: list[RichTextObject]) -> None:
        """
        Truncate text content in rich text objects that exceed the limit.
        """
        for rich_text_obj in rich_text_list:
            if not self._is_text_rich_text_object(rich_text_obj):
                continue

            content = rich_text_obj.text.content
            if len(content) > self.max_text_length:
                self.logger.warning(
                    "Truncating text content from %d to %d characters",
                    len(content),
                    self.max_text_length,
                )
                # Truncate the content
                rich_text_obj.text.content = content[: self.max_text_length]

    def _flatten_block_list(self, blocks: list[BlockCreateRequest | list]) -> list[BlockCreateRequest]:
        """
        Flatten a potentially nested list of blocks.
        """
        flattened: list[BlockCreateRequest] = []

        for item in blocks:
            if isinstance(item, list):
                # Recursively flatten nested lists
                flattened.extend(self._flatten_block_list(item))
            else:
                # Add individual block
                flattened.append(item)

        return flattened

    def _is_rich_text_container(self, obj: object) -> TypeGuard[HasRichText]:
        """Type guard to check if an object has rich_text attribute."""
        return hasattr(obj, "rich_text") and isinstance(obj.rich_text, list)

    def _is_children_container(self, obj: object) -> TypeGuard[HasChildren]:
        """Type guard to check if an object has children attribute."""
        return hasattr(obj, "children") and isinstance(obj.children, list)

    def _is_text_rich_text_object(self, rich_text_obj: RichTextObject) -> TypeGuard[RichTextObject]:
        """Type guard to check if a RichTextObject is of type 'text' with content."""
        return (
            rich_text_obj.type == "text" and rich_text_obj.text is not None and rich_text_obj.text.content is not None
        )
