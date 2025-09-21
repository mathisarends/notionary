from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.numbered_list.numbered_list_models import (
    CreateNumberedListItemBlock,
    NumberedListItemBlock,
)
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.types import BlockColor


class NumberedListElement(BaseBlockElement):
    """Converts between Markdown numbered lists and Notion numbered list items."""

    PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM and block.numbered_list_item

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown numbered list item to Notion NumberedListItemBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(2)
        rich_text = await TextInlineFormatter.parse_inline_formatting(content)

        numbered_list_content = NumberedListItemBlock(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateNumberedListItemBlock(numbered_list_item=numbered_list_content)

    # FIX: Roundtrip conversions will never work this way here
    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.NUMBERED_LIST_ITEM or not block.numbered_list_item:
            return None

        rich = block.numbered_list_item.rich_text
        content = await TextInlineFormatter.extract_text_with_formatting(rich)
        return f"1. {content}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for numbered list blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Numbered list items create ordered lists with sequential numbering",
            syntax_examples=[
                "1. First item",
                "2. Second item",
                "3. Third item",
                "1. Item with **bold text**",
                "1. Item with *italic text*",
            ],
            usage_guidelines="Use numbers followed by periods to create ordered lists. Supports inline formatting like bold, italic, and links. Numbering is automatically handled by Notion.",
        )
