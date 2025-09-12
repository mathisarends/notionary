from __future__ import annotations

from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter
from notionary.blocks.types import BlockColor, BlockType

from notionary.blocks.space.space_models import SPACE_MARKER


class SpaceElement(BaseBlockElement):
    """
    Handles conversion between Markdown space markers ([space]) and Notion space blocks.
    """

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        if block.type != BlockType.PARAGRAPH:
            return False

        if not block.paragraph:
            return False

        rich_list = block.paragraph.rich_text
        if len(rich_list) != 1:
            return False

        return rich_list[0].plain_text == SPACE_MARKER

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown [space] to a Notion space block."""
        if text.strip() != SPACE_MARKER:
            return None

        rich = await TextInlineFormatter.parse_inline_formatting(
            ""
        )  # create_empty paragraph
        paragraph_content = ParagraphBlock(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if not cls.match_notion(block):
            return None

        return SPACE_MARKER

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for space blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Space blocks create visual spacing between content",
            syntax_examples=[
                SPACE_MARKER,
            ],
            usage_guidelines=f"Use {SPACE_MARKER} to create visual spacing between paragraphs or other content blocks.",
        )
