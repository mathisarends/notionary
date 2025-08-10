from __future__ import annotations
import re
from typing import Optional, cast

from notionary.blocks.heading.heading_models import (
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    HeadingBlock,
)
from notionary.blocks.block_models import (
    Block,
    BlockType,
)
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


from notionary.blocks.block_models import Block, BlockCreateResult


class HeadingElement(NotionBlockElement):
    """Handles conversion between Markdown headings and Notion heading blocks."""

    PATTERN = re.compile(r"^(#{1,3})[ \t]+(.+)$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        m = cls.PATTERN.match(text)
        return bool(m and m.group(2).strip())

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
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown headings (#, ##, ###) to Notion HeadingBlock."""
        m = cls.PATTERN.match(text.strip())
        if not m:
            return None

        level = len(m.group(1))
        if level < 1 or level > 3:
            return None

        content = m.group(2).strip()
        if not content:
            return None

        rich_text = TextInlineFormatter.parse_inline_formatting(content)
        heading_content = HeadingBlock(
            rich_text=rich_text, color="default", is_toggleable=False
        )

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
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

        text = TextInlineFormatter.extract_text_with_formatting(heading_data.rich_text)
        if not text:
            return None

        # Use dashed underline for level 2 headings
        if level == 2:
            underline = "-" * len(text)
            return f"{text}\n{underline}"

        # Fallback to hash-style for other levels
        return f"{('#' * level)} {text}"