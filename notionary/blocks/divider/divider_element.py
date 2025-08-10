from __future__ import annotations

import re
from typing import Optional

from notionary.blocks.block_models import Block, BlockCreateResult

from notionary.blocks.block_types import BlockType
from notionary.blocks.divider.divider_models import CreateDividerBlock, DividerBlock
from notionary.blocks.notion_block_element import NotionBlockElement
from notionary.blocks.paragraph.paragraph_models import (
    CreateParagraphBlock,
    ParagraphBlock,
)


class DividerElement(NotionBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.

    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """

    PATTERN = re.compile(r"^\s*-{3,}\s*$")

    @classmethod
    def match_markdown(cls, text: str) -> bool:
        return bool(cls.PATTERN.match(text))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.DIVIDER and block.divider

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown horizontal rule to Notion divider, with preceding empty paragraph."""
        if not cls.PATTERN.match(text.strip()):
            return None

        empty_para = ParagraphBlock(rich_text=[])
        divider = DividerBlock()

        return [
            CreateParagraphBlock(paragraph=empty_para),
            CreateDividerBlock(divider=divider),
        ]

    @classmethod
    def notion_to_markdown(cls, block: Block) -> Optional[str]:
        if block.type != BlockType.DIVIDER or not block.divider:
            return None
        return "---"
