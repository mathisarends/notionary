import re

from notionary.blocks.mappings.base import BaseBlockElement
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import (
    Block,
    BlockColor,
    BlockCreateResult,
    BlockType,
    CreateNumberedListItemBlock,
    NumberedListItemData,
)
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


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
        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)

        numbered_list_content = NumberedListItemData(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateNumberedListItemBlock(numbered_list_item=numbered_list_content)

    # FIX: Roundtrip conversions will never work this way here
    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.NUMBERED_LIST_ITEM or not block.numbered_list_item:
            return None

        rich = block.numbered_list_item.rich_text
        converter = RichTextToMarkdownConverter()
        content = await converter.to_markdown(rich)
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
