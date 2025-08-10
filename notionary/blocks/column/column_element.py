from __future__ import annotations
import re
from turtle import width

from notionary.blocks.block_models import Block, BlockCreateResult, BlockType
from notionary.blocks.column.column_models import ColumnBlock, CreateColumnBlock
from notionary.blocks.notion_block_element import NotionBlockElement


class ColumnElement(NotionBlockElement):
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
    def match_markdown(cls, text: str) -> bool:
        """Check if text starts a single column."""
        return bool(cls.COLUMN_START.match(text.strip()))

    @classmethod
    def match_notion(cls, block: Block) -> bool:
        """Check if block is a Notion column."""
        return block.type == BlockType.COLUMN and block.column

    @classmethod
    def markdown_to_notion(cls, text: str) -> BlockCreateResult:
        """Convert `::: column [ratio]` to Notion ColumnBlock."""
        match = cls.COLUMN_START.match(text.strip())
        if not match:
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
    def notion_to_markdown(cls, block: Block) -> str:
        """Convert Notion column to markdown."""
        if not cls.match_notion(block):
            return ""

        if not block.column.width_ratio:
            return "::: column"

        return f"::: column {block.column.width_ratio}"
