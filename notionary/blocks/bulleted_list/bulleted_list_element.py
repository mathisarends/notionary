from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.bulleted_list.models import (
    BulletedListItemBlock,
    CreateBulletedListItemBlock,
)
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class BulletedListElement(BaseBlockElement):
    """Class for converting between Markdown bullet lists and Notion bulleted list items."""

    # Regex for markdown bullets (excluding todo items [ ] or [x])
    PATTERN = re.compile(r"^(\s*)[*\-+]\s+(?!\[[ x]\])(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.BULLETED_LIST_ITEM and block.bulleted_list_item

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert a markdown bulleted list item into a Notion BulletedListItemBlock.
        """
        if not (match := cls.PATTERN.match(text.strip())):
            return None

        content = match.group(2)

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)

        bulleted_list_content = BulletedListItemBlock(rich_text=rich_text)
        return CreateBulletedListItemBlock(bulleted_list_item=bulleted_list_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.BULLETED_LIST_ITEM or not block.bulleted_list_item:
            return None

        rich_list = block.bulleted_list_item.rich_text
        if not rich_list:
            return "-"

        converter = RichTextToMarkdownConverter()
        text = await converter.to_markdown(rich_list)
        return f"- {text}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for bulleted list blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Bulleted list items create unordered lists with bullet points",
            syntax_examples=[
                "- First item",
                "* Second item",
                "+ Third item",
                "- Item with **bold text**",
                "- Item with *italic text*",
            ],
            usage_guidelines="Use -, *, or + to create bullet points. Supports inline formatting like bold, italic, and links. Do not use for todo items (use [ ] or [x] for those).",
        )
