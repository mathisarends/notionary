from __future__ import annotations

import re

from notionary.blocks.base_block_element import BaseBlockElement
from notionary.blocks.column.column_models import ColumnBlock, CreateColumnBlock
from notionary.blocks.models import Block, BlockCreateResult, BlockType
from notionary.blocks.syntax_prompt_builder import BlockElementMarkdownInformation


class ColumnElement(BaseBlockElement):
    """
    Handles individual `::: column` blocks with optional width ratio.
    Content is automatically added by the stack processor.

    Supported syntax:
    - `::: column` (equal width)
    - `::: column 0.5` (50% width)
    - `::: column 0.25` (25% width)
    """

    COLUMN_START = re.compile(r"^:::\s*column(?:\s+(0?\.\d+|1\.0?))?\s*$")

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column."""
        return block.type == BlockType.COLUMN and block.column

    @classmethod
    async def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: column [ratio]` to Notion ColumnBlock."""
        if not (match := cls.COLUMN_START.match(text.strip())):
            return None

        ratio_str = match.group(1)
        width_ratio = None

        if ratio_str:
            try:
                width_ratio = float(ratio_str)
                # Validate ratio is between 0 and 1
                if not (0 < width_ratio <= 1.0):
                    width_ratio = None  # Invalid ratio, use default
            except ValueError:
                width_ratio = None  # Invalid format, use default

        column_content = ColumnBlock(width_ratio=width_ratio)
        return CreateColumnBlock(column=column_content)

    @classmethod
    async def notion_to_markdown(cls, block: Block) -> str:
        """Convert Notion column to markdown."""
        if not cls.match_notion(block):
            return ""

        if not block.column.width_ratio:
            return "::: column"

        return f"::: column {block.column.width_ratio}"

    @classmethod
    def get_system_prompt_information(cls) -> BlockElementMarkdownInformation | None:
        """Column elements are documented via ColumnListElement - return None to avoid duplication."""
        return None
