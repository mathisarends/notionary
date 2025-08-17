from __future__ import annotations
import re
from typing import Optional

from notionary.blocks.models import Block, BlockCreateResult

from notionary.blocks.models import (
    Block,
    BlockType,
)
from notionary.blocks.types import BlockColor
from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.numbered_list.numbered_list_models import (
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class NumberedListElement(BaseBlockElement):
    """Converts between Markdown numbered lists and Notion numbered list items."""

    PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM and block.numbered_list_item

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown numbered list item to Notion NumberedListItemBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(2)
        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        numbered_list_content = NumberedListItemBlock(
            rich_text=rich_text, color=BlockColor.DEFAULT
        )
        return CreateNumberedListItemBlock(numbered_list_item=numbered_list_content)

    # FIX: Roundtrip conversions will never work this way here
    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.NUMBERED_LIST_ITEM or not block.numbered_list_item:
            return None

        rich = block.numbered_list_item.rich_text
        content = TextInlineFormatter.extract_text_with_formatting(rich)
        return f"1. {content}"
