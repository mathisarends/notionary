from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.bulleted_list.bulleted_list_models import (
    BulletedListItemBlock,
    CreateBulletedListItemBlock,
)
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class BulletedListElement(BaseBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""

    # Regex for markdown bullets (excluding todo items [ ] or [x])
    PATTERN = re.compile(r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.BULLETED_LIST_ITEM and block.bulleted_list_item

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert a markdown bulleted list item into a Notion BulletedListItemBlock.
        """
        if not (match := cls.PATTERN.match(text.strip())):
            return None

        # Extract the content part (second capture group)
        content = match.group(2)

        # Parse inline markdown formatting into RichTextObject list
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        # Return a properly typed Notion block
        bulleted_list_content = BulletedListItemBlock(
            rich_text=rich_text, color="default"
        )
        return CreateBulletedListItemBlock(bulleted_list_item=bulleted_list_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        """Convert Notion bulleted_list_item block to Markdown."""
        if block.type != BlockType.BULLETED_LIST_ITEM or not block.bulleted_list_item:
            return None

        rich_list = block.bulleted_list_item.rich_text
        if not rich_list:
            return "-"

        text = TextInlineFormatter.extract_text_with_formatting(rich_list)
        return f"- {text}"
