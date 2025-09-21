from __future__ import annotations

import re
from typing import cast

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.heading.heading_models import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    HeadingBlock,
)
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation
from notionary.blocks.types import BlockColor


class HeadingElement(BaseBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""

    PATTERN = re.compile(r"^(#{1,3})[ \t]+(.+)$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        return (
            block.type
            in (
                BlockType.HEADING_1,
                BlockType.HEADING_2,
                BlockType.HEADING_3,
            )
            and getattr(block, block.type.value) is not None
        )

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown headings (#, ##, ###) to Notion HeadingBlock."""
        match = cls.PATTERN.match(text.strip())
        if not match:
            return None

        level = len(match.group(1))
        if level < 1 or level > 3:
            return None

        content = match.group(2).strip()
        if not content:
            return None

        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(content)
        heading_content = HeadingBlock(rich_text=rich_text, color=BlockColor.DEFAULT, is_toggleable=False)

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        # Only handle heading blocks via BlockType enum
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return None

        # Determine heading level from enum
        if block.type == BlockType.HEADING_1:
            level = 1
        elif block.type == BlockType.HEADING_2:
            level = 2
        else:
            level = 3

        heading_obj = getattr(block, block.type.value)
        if not heading_obj:
            return None

        heading_data = cast(HeadingBlock, heading_obj)
        if not heading_data.rich_text:
            return None

        converter = RichTextToMarkdownConverter()
        text = await converter.to_markdown(heading_data.rich_text)
        if not text:
            return None

        # Use hash-style for all heading levels
        return f"{('#' * level)} {text}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Get system prompt information for heading blocks."""
        return BlockElementMarkdownInformation(
            block_type=cls.__name__,
            description="Heading blocks create hierarchical document structure with different levels",
            syntax_examples=[
                "# Heading Level 1",
                "## Heading Level 2",
                "### Heading Level 3",
                "# Heading with **bold text**",
                "## Heading with *italic text*",
            ],
            usage_guidelines="Use # for main titles, ## for sections, ### for subsections. Supports inline formatting. Only levels 1-3 are supported in Notion.",
        )
