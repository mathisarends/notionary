import re

from notionary.blocks.mappings.base import NotionMarkdownMapper
from notionary.blocks.mappings.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.schemas import (
    Block,
    BlockColor,
    BlockType,
    CreateNumberedListItemBlock,
    NumberedListItemData,
)


class NumberedListMapper(NotionMarkdownMapper):
    PATTERN = re.compile(r"^\s*(\d+)\.\s+(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.NUMBERED_LIST_ITEM and block.numbered_list_item

    @classmethod
    async def markdown_to_notion(cls, text: str) -> CreateNumberedListItemBlock:
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
