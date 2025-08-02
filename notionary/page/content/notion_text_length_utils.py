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
from notionary.blocks.shared.models import BlockCreateRequest

logger = logging.getLogger(__name__)


def fix_blocks_content_length(
    blocks: list[BlockCreateRequest], max_text_length: int = 1900
) -> list[BlockCreateRequest]:
    """Check each block and ensure text content doesn't exceed Notion's limit."""
    return [_fix_single_block_content(block, max_text_length) for block in blocks]


def _fix_single_block_content(
    block: BlockCreateRequest, max_text_length: int
) -> BlockCreateRequest:
    """Fix content length in a single block and its children recursively."""
    # Create a copy by converting to dict and back to model
    block_dict = block.model_dump()

    # Fix rich_text content if present
    _fix_rich_text_in_block_dict(block_dict, max_text_length)

    # Recreate the model from the fixed dict
    return block.__class__.model_validate(block_dict)


def _fix_rich_text_in_block_dict(
    block_dict: dict[str, Any], max_text_length: int
) -> None:
    """Fix rich text content in a block dictionary recursively."""

    # Handle rich_text at the top level
    if "rich_text" in block_dict:
        _fix_rich_text_list(block_dict["rich_text"], max_text_length)

    # Handle rich_text in nested content and children
    for key, value in block_dict.items():
        if not isinstance(value, dict):
            continue

        _fix_nested_rich_text(value, max_text_length)
        _fix_nested_children(value, max_text_length)


def _fix_nested_rich_text(value: dict[str, Any], max_text_length: int) -> None:
    """Fix rich_text in nested content (e.g., paragraph.rich_text)."""
    if "rich_text" in value:
        _fix_rich_text_list(value["rich_text"], max_text_length)


def _fix_nested_children(value: dict[str, Any], max_text_length: int) -> None:
    """Handle children recursively."""
    children = value.get("children")
    if not isinstance(children, list):
        return

    for child_dict in children:
        if isinstance(child_dict, dict):
            _fix_rich_text_in_block_dict(child_dict, max_text_length)


def _fix_rich_text_list(
    rich_text_list: list[dict[str, Any]], max_text_length: int
) -> None:
    """Fix a list of rich text objects."""
    for rich_text_item in rich_text_list:
        if not isinstance(rich_text_item, dict):
            continue

        text_obj = rich_text_item.get("text")
        if not text_obj or not isinstance(text_obj, dict):
            continue

        content = text_obj.get("content")
        if not content or not isinstance(content, str):
            continue

        if len(content) > max_text_length:
            logger.warning(
                "Truncating text content from %d to %d chars",
                len(content),
                max_text_length,
            )
            text_obj["content"] = content[:max_text_length]


def split_to_paragraphs(markdown_text: str) -> list[str]:
    """Split markdown into paragraphs."""
    paragraphs = re.split(r"\n\s*\n", markdown_text)
    return [p for p in paragraphs if p.strip()]


def split_to_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s for s in sentences if s.strip()]
