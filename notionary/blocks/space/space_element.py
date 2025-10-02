from __future__ import annotations

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.models import Block, BlockCreateResult
from notionary.blocks.paragraph.models import (
    CreateParagraphBlock,
    ParagraphBlock,
)
from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.models import RichText
from notionary.blocks.space.models import SPACE_MARKER
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.types import BlockColor, BlockType


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

        # check for empty paragraph because only space element can produce such a block in this conversion logic
        if cls._is_empty_paragraph(block.paragraph.rich_text):
            return True

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown [space] to a Notion space block."""
        if text.strip() != SPACE_MARKER:
            return None

        converter = MarkdownRichTextConverter()
        rich = await converter.to_rich_text("")  # create empty paragraph
        paragraph_content = ParagraphBlock(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if not cls.match_notion(block):
            return None

        return SPACE_MARKER

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for space blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Space blocks create visual spacing between content",
            syntax_examples=[
                SPACE_MARKER,
            ],
            usage_guidelines=f"Use {SPACE_MARKER} to create visual spacing between paragraphs or other content blocks.",
        )

    @classmethod
    def _is_empty_paragraph(cls, rich_text: list[RichText]) -> bool:
        return not len(rich_text)
