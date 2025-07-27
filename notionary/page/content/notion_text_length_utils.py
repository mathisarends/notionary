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

logger = logging.getLogger(__name__)


def fix_blocks_content_length(
    blocks: list[dict[str, Any]], max_text_length: int = 1900
) -> list[dict[str, Any]]:
    """Check each block and ensure text content doesn't exceed Notion's limit."""
    return [_fix_single_block_content(block, max_text_length) for block in blocks]


def _fix_single_block_content(
    block: dict[str, Any], max_text_length: int
) -> dict[str, Any]:
    """Fix content length in a single block and its children recursively."""
    block_copy = block.copy()

    block_type = block.get("type")
    if not block_type:
        return block_copy

    content = block.get(block_type)
    if not content:
        return block_copy

    if "rich_text" in content:
        _fix_rich_text_content(block_copy, block_type, content, max_text_length)

    if "children" in content and content["children"]:
        block_copy[block_type]["children"] = [
            _fix_single_block_content(child, max_text_length)
            for child in content["children"]
        ]

    return block_copy


def _fix_rich_text_content(
    block_copy: dict[str, Any],
    block_type: str,
    content: dict[str, Any],
    max_text_length: int,
) -> None:
    """Fix rich text content that exceeds the length limit."""
    rich_text = content["rich_text"]
    for i, text_item in enumerate(rich_text):
        if "text" not in text_item or "content" not in text_item["text"]:
            continue

        text_content = text_item["text"]["content"]
        if len(text_content) <= max_text_length:
            continue

        logger.warning(
            "Truncating text content from %d to %d chars",
            len(text_content),
            max_text_length,
        )
        block_copy[block_type]["rich_text"][i]["text"]["content"] = text_content[
            :max_text_length
        ]


def split_to_paragraphs(markdown_text: str) -> list[str]:
    """Split markdown into paragraphs."""
    paragraphs = re.split(r"\n\s*\n", markdown_text)
    return [p for p in paragraphs if p.strip()]


def split_to_sentences(paragraph: str) -> list[str]:
    """Split a paragraph into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    return [s for s in sentences if s.strip()]
