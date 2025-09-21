from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.quote.quote_models import CreateQuoteBlock, QuoteBlock
from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.types import BlockColor


class QuoteElement(BaseBlockElement):
    """
    Handles conversion between Markdown quotes and Notion quote blocks.

    Markdown quote syntax:
    - > Simple quote text

    Only single-line quotes without author metadata.
    """

    PATTERN = re.compile(r"^>\s*(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == BlockType.QUOTE and block.quote

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown quote to Notion QuoteBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        content = match.group(1).strip()
        if not content:
            return None

        # Reject multiline quotes
        if "\n" in content or "\r" in content:
            return None

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)

        quote_content = QuoteBlock(rich_text=rich_text, color=BlockColor.DEFAULT)
        return CreateQuoteBlock(quote=quote_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.QUOTE or not block.quote:
            return None

        rich = block.quote.rich_text
        converter = RichTextToMarkdownConverter()
        text = await converter.to_markdown(rich)

        if not text.strip():
            return None

        return f"> {text.strip()}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for quote blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Quote blocks display highlighted quotations or emphasized text",
            syntax_examples=[
                "> This is an important quote",
                "> The only way to do great work is to love what you do",
                "> Innovation distinguishes between a leader and a follower",
            ],
            usage_guidelines="Use for quotations, important statements, or text that should be visually emphasized. Content should be meaningful and stand out from regular paragraphs.",
        )
