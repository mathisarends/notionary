from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.heading.heading_models import (CreateHeading1Block,
                                                     CreateHeading2Block,
                                                     CreateHeading3Block,
                                                     HeadingBlock)
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.rich_text.text_inline_formatter import \
    TextInlineFormatter


class ToggleableHeadingElement(BaseBlockElement):
    """
    Simplified ToggleableHeadingElement that works with the stack-based converter.
    Children are automatically handled by the StackBasedMarkdownConverter.
    """

    # Updated pattern for simplified +++# Title syntax (no quotes!)
    PATTERN = re.compile(r"^[+]{3}(?P<level>#{1,3})\s+(.+)$", re.IGNORECASE)

    @staticmethod
    def match_notion(block: Block) -> bool:
        """Check if block is a Notion toggleable heading."""
        # Use BlockType enum for matching heading blocks
        if block.type not in (
            BlockType.HEADING_1,
            BlockType.HEADING_2,
            BlockType.HEADING_3,
        ):
            return False

        if block.heading_1 and block.heading_1.is_toggleable:
            return True
        if block.heading_2 and block.heading_2.is_toggleable:
            return True
        if block.heading_3 and block.heading_3.is_toggleable:
            return True

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """
        Convert markdown collapsible heading to a toggleable Notion HeadingBlock.
        Children are automatically handled by the StackBasedMarkdownConverter.
        """
        if not (match := cls.PATTERN.match(text.strip())):
            return None

        level = len(match.group("level"))  # Count # characters
        content = match.group(2).strip()  # group(2) is the title (no quotes needed)

        if level < 1 or level > 3 or not content:
            return None

        rich_text = TextInlineFormatter.parse_inline_formatting(content)

        heading_content = HeadingBlock(
            rich_text=rich_text, color="default", is_toggleable=True, children=[]
        )

        if level == 1:
            return CreateHeading1Block(heading_1=heading_content)
        elif level == 2:
            return CreateHeading2Block(heading_2=heading_content)
        else:
            return CreateHeading3Block(heading_3=heading_content)

    @staticmethod
    def notion_to_markdown(block: Block) -> Optional[str]:
        """Convert Notion toggleable heading block to markdown collapsible heading."""
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

        heading_content = getattr(block, block.type.value)
        if not isinstance(heading_content, HeadingBlock):
            return None

        text = TextInlineFormatter.extract_text_with_formatting(
            heading_content.rich_text
        )
        prefix = "#" * level

        return f'+++{prefix} {text or ""}'
