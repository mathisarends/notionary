"""
Utility functions for handling Notion API text length limitations.

This module provides functions to fix text content that exceeds Notion's
rich_text character limit of 2000 characters per element.

Resolves API errors like:
"validation_error - body.children[79].toggle.children[2].paragraph.rich_text[0].text.content.length
should be ≤ 2000, instead was 2162."
"""

import re
import logging
from typing import Any
from notionary.blocks.block_models import BlockCreateRequest

logger = logging.getLogger(__name__)


def fix_blocks_content_length(
    blocks: list[BlockCreateRequest], max_text_length: int = 1900
) -> list[BlockCreateRequest]:
    """Check each block and ensure text content doesn't exceed Notion's limit."""
    fixed_blocks: list[BlockCreateRequest] = []

    for block in blocks:
        fixed_block = _fix_single_block_content(block, max_text_length)
        fixed_blocks.append(fixed_block)
    return fixed_blocks


def _fix_single_block_content(
    block: BlockCreateRequest, max_text_length: int
) -> BlockCreateRequest:
    """Fix content length in a single block and its children recursively."""
    block_copy = block.model_copy(deep=True)
    _fix_block_rich_text_direct(block_copy, max_text_length)

    return block_copy


def _fix_block_rich_text_direct(
    block: BlockCreateRequest, max_text_length: int
) -> None:
    """Fix rich text content directly on the Pydantic object."""
    block_content = _get_block_content(block)
    if not block_content:
        return
    if hasattr(block_content, "rich_text") and block_content.rich_text:
        _fix_rich_text_objects_direct(block_content.rich_text, max_text_length)
    if hasattr(block_content, "children") and block_content.children:
        for child in block_content.children:
            _fix_block_rich_text_direct(child, max_text_length)


def _get_block_content(block: BlockCreateRequest):
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
        if attr_value is None or isinstance(attr_value, str) or callable(attr_value):
            continue

        # If it's an object with rich_text or children, it's likely our content
        if hasattr(attr_value, "rich_text") or hasattr(attr_value, "children"):
            return attr_value

    return None


def _fix_rich_text_objects_direct(rich_text_list: list, max_text_length: int) -> None:
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
            if content and len(content) > max_text_length:
                logger.warning(
                    "Truncating text content from %d to %d chars",
                    len(content),
                    max_text_length,
                )
                # Direct assignment - no parsing needed!
                rich_text_item.text.content = content[:max_text_length]


def split_to_paragraphs(markdown_text: str) -> list[str]:
    """Split markdown into paragraphs."""
    paragraphs = re.split(r"\n\s*\n", markdown_text)
    return [p for p in paragraphs if p.strip()]


def split_to_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s for s in sentences if s.strip()]
