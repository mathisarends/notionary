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


class ParagraphElement(BaseBlockElement):
    """
    Handles conversion between Markdown paragraphs and Notion paragraph blocks.
    """

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return block.type == "paragraph" and block.paragraph

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown text to a Notion ParagraphBlock."""
        if not text.strip():
            return None

        rich = TextInlineFormatter.parse_inline_formatting(text)

        paragraph_content = ParagraphBlock(rich_text=rich, color=BlockColor.DEFAULT)
        return CreateParagraphBlock(paragraph=paragraph_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.PARAGRAPH or not block.paragraph:
            return None

        rich_list = block.paragraph.rich_text
        markdown = TextInlineFormatter.extract_text_with_formatting(rich_list)
        return markdown or None

    @classmethod
    def get_system_prompt_information(cls) -> Optional[BlockElementMarkdownInformation]:
        """Get system prompt information for paragraph blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Paragraph blocks contain regular text content with optional inline formatting",
            syntax_examples=[
                "This is a simple paragraph.",
                "Paragraph with **bold text** and *italic text*.",
                "Paragraph with [link](https://example.com) and `code`.",
                "Multiple sentences in one paragraph. Each sentence flows naturally.",
            ],
            usage_guidelines="Use for regular text content. Supports inline formatting: **bold**, *italic*, `code`, [links](url). Default block type for plain text.",
        )
