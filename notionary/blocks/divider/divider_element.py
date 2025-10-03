from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.divider.models import CreateDividerBlock, DividerBlock
from notionary.blocks.schemas import Block, BlockCreateResult
from notionary.blocks.types import BlockType


class DividerElement(BaseBlockElement):
    """
    Handles conversion between Markdown horizontal dividers and Notion divider blocks.

    Markdown divider syntax:
    - Three or more hyphens (---) on a line by themselves
    """

    PATTERN = re.compile(r"^\s*-{3,}\s*$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if this element can handle the given Notion block."""
        return block.type == BlockType.DIVIDER and block.divider

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert markdown horizontal rule to Notion divider, with preceding empty paragraph."""
        if not cls.PATTERN.match(text.strip()):
            return None

        divider = DividerBlock()

        return CreateDividerBlock(divider=divider)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str | None:
        if block.type != BlockType.DIVIDER or not block.divider:
            return None
        return "---"
