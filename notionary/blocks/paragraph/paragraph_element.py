from __future__ import annotations
from typing import Optional

from notionary.blocks.models import Block, BlockCreateResult

from notionary.blocks.types import BlockColor, BlockType
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.base_block_element import BaseBlockElement

from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class ParagraphElement(BaseBlockElement):
    """
    Handles conversion between Markdown paragraphs and Notion paragraph blocks.
    """

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "paragraph" and block.paragraph

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown text to a Notion ParagraphBlock."""
        if not text.strip():
            return None

        rich = TextInlineFormatter.parse_inline_formatting(text)

        paragraph_content = ParagraphBlock(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != "paragraph" or not block.paragraph:
            return None

        rich_list = block.paragraph.rich_text
        markdown = TextInlineFormatter.extract_text_with_formatting(rich_list)
        return markdown or None
